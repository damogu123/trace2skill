from __future__ import annotations

import argparse
import difflib
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_SCHEMA = ROOT / "schemas" / "run_manifest.schema.json"
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
DEFAULT_TRACE_SCHEMA = ROOT / "schemas" / "agent_trace.schema.json"
DEFAULT_TRAJECTORY_SCHEMA = ROOT / "schemas" / "trajectory.schema.json"
EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "runs",
    "trajectories",
}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}
EXCLUDED_FILENAMES = {
    "agent_trace.json",
    ".agent_trace.json",
}


class SafeFormat(dict[str, str]):
    def __missing__(self, key: str) -> str:
        raise KeyError(f"Unknown command placeholder: {key}")


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def project_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def to_wsl_path(path: Path) -> str:
    resolved = path.resolve()
    if os.name != "nt":
        return resolved.as_posix()
    drive = resolved.drive.rstrip(":").lower()
    if not drive:
        return resolved.as_posix().replace("\\", "/")
    relative = resolved.relative_to(resolved.anchor)
    return f"/mnt/{drive}/" + relative.as_posix()


def load_validated(path: Path, schema_path: Path) -> dict[str, Any]:
    data = load_json(path)
    validate_instance(data, load_json(schema_path))
    return data


def run_env(repo_dir: Path, run: dict[str, Any], paths: dict[str, Path]) -> dict[str, str]:
    env = os.environ.copy()
    src_path = str((repo_dir / "src").resolve())
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src_path if not existing_pythonpath else src_path + os.pathsep + existing_pythonpath
    env.update(
        {
            "RUN_ID": run["run_id"],
            "METHOD": run["method"],
            "PROMPT_PATH": str(paths["prompt_path"]),
            "REPO_DIR": str(paths["repo_dir"]),
            "ARTIFACTS_DIR": str(paths["artifacts_dir"]),
            "TRACE_PATH": str(paths["trace_path"]),
            "TASK_PATH": str(paths["task_path"]),
        }
    )
    return env


def run_command(
    command: str,
    cwd: Path,
    log_path: Path,
    timeout: int,
    env: dict[str, str],
    runner: str = "native",
    wsl_distro: str = "Ubuntu-24.04",
    wsl_env_prefix: str = "",
) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if runner == "wsl":
        bash_parts = []
        if wsl_env_prefix.strip():
            bash_parts.append(wsl_env_prefix.strip())
        bash_parts.append(f"cd {shlex.quote(to_wsl_path(cwd))}")
        bash_parts.append(command)
        process_command: str | list[str] = [
            "wsl.exe",
            "-d",
            wsl_distro,
            "--exec",
            "/bin/bash",
            "-lc",
            "; ".join(bash_parts),
        ]
        shell = False
        process_cwd = None
    else:
        process_command = command
        shell = True
        process_cwd = cwd
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        process = subprocess.run(
            process_command,
            cwd=process_cwd,
            shell=shell,
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            env=env,
        )
    return process.returncode


def should_snapshot(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    if any(part in EXCLUDED_DIRS for part in relative_parts):
        return False
    if path.name in EXCLUDED_FILENAMES:
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if path.name.endswith(".egg-info"):
        return False
    return path.is_file()


def read_text_or_none(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def snapshot_tree(root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not should_snapshot(path, root):
            continue
        relative = path.relative_to(root).as_posix()
        text = read_text_or_none(path)
        if text is not None:
            snapshot[relative] = text
    return snapshot


def write_unified_diff(before: dict[str, str], after: dict[str, str], patch_path: Path) -> list[str]:
    modified_files = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    lines: list[str] = []
    for relative in modified_files:
        old_text = before.get(relative, "")
        new_text = after.get(relative, "")
        fromfile = f"a/{relative}" if relative in before else "/dev/null"
        tofile = f"b/{relative}" if relative in after else "/dev/null"
        lines.extend(
            difflib.unified_diff(
                old_text.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=fromfile,
                tofile=tofile,
            )
        )
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_text("".join(lines), encoding="utf-8", newline="\n")
    return modified_files


def modified_files_from_patch(patch_path: Path) -> list[str]:
    if not patch_path.exists():
        raise FileNotFoundError(f"Patch artifact missing: {patch_path}")

    modified_files: set[str] = set()
    for line in patch_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("--- a/") or line.startswith("+++ b/"):
            path_text = line[6:]
            if path_text != "/dev/null":
                modified_files.add(path_text)
    return sorted(modified_files)


def command_placeholders(run: dict[str, Any], paths: dict[str, Path]) -> dict[str, str]:
    return {
        "prompt_path": str(paths["prompt_path"]),
        "repo_dir": str(paths["repo_dir"]),
        "artifacts_dir": str(paths["artifacts_dir"]),
        "trace_path": str(paths["trace_path"]),
        "task_path": str(paths["task_path"]),
        "run_id": run["run_id"],
        "method": run["method"],
    }


def render_agent_command(template: str, run: dict[str, Any], paths: dict[str, Path]) -> str:
    return template.format_map(SafeFormat(command_placeholders(run, paths)))


def load_trace(trace_path: Path, schema_path: Path, allow_missing: bool) -> dict[str, Any] | None:
    if not trace_path.exists():
        if allow_missing:
            return None
        raise FileNotFoundError(f"Agent trace missing: {trace_path}")
    trace = load_json(trace_path)
    normalize_trace(trace)
    validate_instance(trace, load_json(schema_path))
    return trace


def normalize_trace(trace: dict[str, Any]) -> None:
    negative_transfer = trace.get("negative_transfer")
    if isinstance(negative_transfer, dict):
        category = negative_transfer.get("category")
        detected = bool(negative_transfer.get("detected"))
        allowed_categories = {"performance", "behavioral", "self_contradictory", None}
        if category not in allowed_categories:
            negative_transfer["category"] = "performance" if detected else None

    for cycle in trace.get("cycles", []):
        mistakes = cycle.get("mistakes")
        if not isinstance(mistakes, list):
            continue
        normalized = []
        changed = False
        for mistake in mistakes:
            if isinstance(mistake, str):
                normalized.append(
                    {
                        "type": "agent_reported_mistake",
                        "description": mistake,
                    }
                )
                changed = True
            else:
                normalized.append(mistake)
        if changed:
            cycle["mistakes"] = normalized


def minimal_trace(modified_files: list[str], args: argparse.Namespace) -> dict[str, Any]:
    return {
        "llm_turns": 0,
        "tool_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cycles": [
            {
                "cycle_id": 1,
                "diagnosis": args.missing_trace_diagnosis,
                "file_inspections": [],
                "modified_files": modified_files,
                "patch_summary": "External agent did not emit a structured trace.",
                "test_command": None,
                "test_passed": None,
                "test_log_path": None,
                "mistakes": [],
            }
        ],
        "negative_transfer": {
            "detected": False,
            "category": None,
            "reason": None,
        },
    }


def build_cycles(
    trace: dict[str, Any],
    task: dict[str, Any],
    final_test_passed: bool,
    final_log_path: str,
    patch_path: str,
    observed_modified_files: list[str],
) -> list[dict[str, Any]]:
    cycles = []
    trace_cycles = trace["cycles"]
    for index, cycle in enumerate(trace_cycles):
        is_last = index == len(trace_cycles) - 1
        modified_files = cycle.get("modified_files") or ([] if not is_last else observed_modified_files)
        test_command = cycle.get("test_command") or task["environment"]["test_command"]
        test_passed = cycle.get("test_passed")
        if test_passed is None:
            test_passed = final_test_passed if is_last else False
        test_log_path = cycle.get("test_log_path") or (final_log_path if is_last else "")
        cycles.append(
            {
                "cycle_id": cycle["cycle_id"],
                "diagnosis": cycle["diagnosis"],
                "file_inspections": cycle["file_inspections"],
                "patch_attempt": {
                    "modified_files": modified_files,
                    "patch_path": patch_path if is_last else None,
                    "patch_summary": cycle.get("patch_summary"),
                },
                "test_rerun": {
                    "command": test_command,
                    "passed": bool(test_passed),
                    "log_path": test_log_path,
                },
                "mistakes": cycle.get("mistakes", []),
            }
        )
    return cycles


def count_failed_patches(cycles: list[dict[str, Any]]) -> int:
    failed = 0
    for cycle in cycles:
        if cycle["patch_attempt"]["modified_files"] and not cycle["test_rerun"]["passed"]:
            failed += 1
    return failed


def context_tokens(run: dict[str, Any]) -> int:
    total = 0
    for key in ("baseline_context_path", "memory_path"):
        path_text = run.get(key)
        if path_text:
            text = resolve_project_path(path_text).read_text(encoding="utf-8")
            total += max(1, (len(text) + 3) // 4)
    return total


def build_trajectory(
    run: dict[str, Any],
    manifest: dict[str, Any],
    task: dict[str, Any],
    trace: dict[str, Any],
    narrow_code: int,
    full_code: int | None,
    patch_path: Path,
    final_log_path: Path,
    modified_files: list[str],
) -> dict[str, Any]:
    final_test_passed = narrow_code == 0
    full_test_passed = None if full_code is None else full_code == 0
    solved = final_test_passed and (full_test_passed in (True, None))
    broke_existing = None if full_code is None else final_test_passed and not full_test_passed
    patch_path_text = project_relative(patch_path)
    final_log_text = project_relative(final_log_path)
    cycles = build_cycles(
        trace,
        task,
        final_test_passed,
        final_log_text,
        patch_path_text,
        modified_files,
    )
    input_tokens = trace["input_tokens"]
    output_tokens = trace["output_tokens"]
    prompt_overhead_tokens = context_tokens(run)
    total_tokens = input_tokens + output_tokens
    negative_transfer = trace.get(
        "negative_transfer",
        {"detected": False, "category": None, "reason": None},
    )

    return {
        "run_id": run["run_id"],
        "task_id": run["task_id"],
        "method": run["method"],
        "model": manifest["model"],
        "temperature": manifest["temperature"],
        "budget": manifest["budget"],
        "final_outcome": {
            "solved": solved,
            "final_test_passed": final_test_passed,
            "full_test_passed": full_test_passed,
            "broke_existing_tests": broke_existing,
            "timeout": False,
            "cycles_used": len(cycles),
            "llm_turns": trace["llm_turns"],
            "tool_calls": trace["tool_calls"],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "prompt_overhead_tokens": prompt_overhead_tokens,
            "active_debugging_tokens": max(total_tokens - prompt_overhead_tokens, 0),
            "failed_patch_count": count_failed_patches(cycles),
        },
        "cycles": cycles,
        "negative_transfer": negative_transfer,
    }


def select_runs(
    runs: list[dict[str, Any]],
    methods: set[str] | None,
    run_ids: set[str] | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    selected = [
        run
        for run in runs
        if (methods is None or run["method"] in methods)
        and (run_ids is None or run["run_id"] in run_ids)
    ]
    if limit is not None:
        selected = selected[:limit]
    return selected


def parse_csv_set(value: str | None) -> set[str] | None:
    if value is None:
        return None
    return {item.strip() for item in value.split(",") if item.strip()}


def paths_for_run(run: dict[str, Any]) -> dict[str, Path]:
    artifacts_dir = resolve_project_path(run["artifacts_dir"])
    return {
        "repo_dir": resolve_project_path(run["workspace_path"]),
        "artifacts_dir": artifacts_dir,
        "prompt_path": resolve_project_path(run["prompt_path"]),
        "trajectory_path": resolve_project_path(run["trajectory_path"]),
        "task_path": resolve_project_path(run["task_path"]),
        "trace_path": artifacts_dir / "agent_trace.json",
        "agent_log_path": artifacts_dir / "agent.log",
        "reproduce_log_path": artifacts_dir / "reproduce.log",
        "final_log_path": artifacts_dir / "final_test.log",
        "full_log_path": artifacts_dir / "full_test.log",
        "patch_path": artifacts_dir / "agent.patch",
    }


def prepare_run_if_requested(run: dict[str, Any], args: argparse.Namespace) -> None:
    if not args.prepare:
        return
    log_path = paths_for_run(run)["artifacts_dir"] / "prepare.log"
    env = os.environ.copy()
    code = run_command(
        run["prepare_command"],
        ROOT,
        log_path,
        args.prepare_timeout,
        env,
        args.test_runner,
        args.wsl_distro,
        args.wsl_env_prefix,
    )
    if code != 0:
        raise RuntimeError(f"Prepare failed for {run['run_id']} with returncode={code}")


def run_one(run: dict[str, Any], manifest: dict[str, Any], args: argparse.Namespace) -> None:
    paths = paths_for_run(run)
    task = load_validated(paths["task_path"], args.task_schema)
    timeout = int(task["environment"]["timeout_seconds"])
    repo_dir = paths["repo_dir"]
    artifacts_dir = paths["artifacts_dir"]
    trajectory_path = paths["trajectory_path"]

    if trajectory_path.exists() and args.skip_existing_trajectories:
        print(f"SKIP {run['run_id']}: trajectory exists at {project_relative(trajectory_path)}")
        return
    if trajectory_path.exists() and not args.force:
        raise FileExistsError(f"Trajectory exists: {trajectory_path}. Use --force to overwrite.")

    prepare_run_if_requested(run, args)
    if not repo_dir.exists():
        raise FileNotFoundError(f"Workspace missing for {run['run_id']}: {repo_dir}")

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    env = run_env(repo_dir, run, paths)
    reproduce_code = run_command(
        task["environment"]["test_command"],
        repo_dir,
        paths["reproduce_log_path"],
        timeout,
        env,
        args.test_runner,
        args.wsl_distro,
        args.wsl_env_prefix,
    )
    if reproduce_code == 0 and not args.allow_initial_pass:
        raise RuntimeError(f"Initial failure did not reproduce for {run['run_id']}")

    before = snapshot_tree(repo_dir)
    agent_command = render_agent_command(args.agent_command, run, paths)
    if args.dry_run:
        print(f"DRY-RUN {run['run_id']}: {agent_command}")
        return

    agent_code = run_command(
        agent_command,
        ROOT if args.agent_cwd == "root" else repo_dir,
        paths["agent_log_path"],
        args.agent_timeout,
        env,
    )
    if agent_code != 0 and args.require_agent_zero:
        raise RuntimeError(f"Agent command failed for {run['run_id']} returncode={agent_code}")

    after_agent = snapshot_tree(repo_dir)
    modified_files = write_unified_diff(before, after_agent, paths["patch_path"])
    trace = load_trace(paths["trace_path"], args.trace_schema, args.allow_missing_trace)
    if trace is None:
        trace = minimal_trace(modified_files, args)

    narrow_code = run_command(
        task["environment"]["test_command"],
        repo_dir,
        paths["final_log_path"],
        timeout,
        env,
        args.test_runner,
        args.wsl_distro,
        args.wsl_env_prefix,
    )
    full_command = task["environment"].get("full_test_command")
    full_code = None
    if full_command:
        full_code = run_command(
            full_command,
            repo_dir,
            paths["full_log_path"],
            timeout,
            env,
            args.test_runner,
            args.wsl_distro,
            args.wsl_env_prefix,
        )

    trajectory = build_trajectory(
        run,
        manifest,
        task,
        trace,
        narrow_code,
        full_code,
        paths["patch_path"],
        paths["final_log_path"],
        modified_files,
    )
    validate_instance(trajectory, load_json(args.trajectory_schema))
    trajectory_path.parent.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text(json.dumps(trajectory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"{run['run_id']}: agent={agent_code} reproduce={reproduce_code} "
        f"narrow={narrow_code} full={full_code} modified={len(modified_files)}"
    )


def finalize_existing_artifacts(run: dict[str, Any], manifest: dict[str, Any], args: argparse.Namespace) -> None:
    paths = paths_for_run(run)
    task = load_validated(paths["task_path"], args.task_schema)
    timeout = int(task["environment"]["timeout_seconds"])
    repo_dir = paths["repo_dir"]
    artifacts_dir = paths["artifacts_dir"]
    trajectory_path = paths["trajectory_path"]

    if trajectory_path.exists() and args.skip_existing_trajectories:
        print(f"SKIP {run['run_id']}: trajectory exists at {project_relative(trajectory_path)}")
        return
    if trajectory_path.exists() and not args.force:
        raise FileExistsError(f"Trajectory exists: {trajectory_path}. Use --force to overwrite.")
    if not repo_dir.exists():
        raise FileNotFoundError(f"Workspace missing for {run['run_id']}: {repo_dir}")

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    env = run_env(repo_dir, run, paths)
    trace = load_trace(paths["trace_path"], args.trace_schema, args.allow_missing_trace)
    if trace is None:
        trace = minimal_trace(modified_files_from_patch(paths["patch_path"]), args)
    modified_files = modified_files_from_patch(paths["patch_path"])

    narrow_code = run_command(
        task["environment"]["test_command"],
        repo_dir,
        paths["final_log_path"],
        timeout,
        env,
        args.test_runner,
        args.wsl_distro,
        args.wsl_env_prefix,
    )
    full_command = task["environment"].get("full_test_command")
    full_code = None
    if full_command:
        full_code = run_command(
            full_command,
            repo_dir,
            paths["full_log_path"],
            timeout,
            env,
            args.test_runner,
            args.wsl_distro,
            args.wsl_env_prefix,
        )

    trajectory = build_trajectory(
        run,
        manifest,
        task,
        trace,
        narrow_code,
        full_code,
        paths["patch_path"],
        paths["final_log_path"],
        modified_files,
    )
    validate_instance(trajectory, load_json(args.trajectory_schema))
    trajectory_path.parent.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text(json.dumps(trajectory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{run['run_id']}: finalized narrow={narrow_code} full={full_code} modified={len(modified_files)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run external debugging agents from a manifest and emit trajectory JSON files."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--agent-command",
        required=False,
        help="Shell command template. Supports {prompt_path}, {repo_dir}, {artifacts_dir}, {trace_path}, {task_path}, {run_id}, {method}.",
    )
    parser.add_argument("--methods", default=None, help="Comma-separated method filter")
    parser.add_argument("--run-ids", default=None, help="Comma-separated run_id filter")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--prepare", action="store_true", help="Run each manifest prepare_command before invoking the agent")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--skip-existing-trajectories",
        action="store_true",
        help="Skip runs whose trajectory_path already exists.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--finalize-existing-artifacts",
        action="store_true",
        help="Build trajectories from existing agent_trace.json and agent.patch artifacts without invoking the agent.",
    )
    parser.add_argument("--agent-cwd", choices=["root", "repo"], default="root")
    parser.add_argument("--agent-timeout", type=int, default=1800)
    parser.add_argument("--prepare-timeout", type=int, default=2400)
    parser.add_argument(
        "--test-runner",
        choices=["native", "wsl"],
        default="native",
        help="Run prepare/reproduce/final test commands in the native shell or WSL.",
    )
    parser.add_argument("--wsl-distro", default="Ubuntu-24.04")
    parser.add_argument(
        "--wsl-env-prefix",
        default=(
            "export PATH=$HOME/.local/bin:$PATH; "
            "export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple; "
            "export PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn; "
            "export PIP_DEFAULT_TIMEOUT=120; "
            "export PIPENV_PYPI_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple; "
            "export PIPENV_TIMEOUT=120"
        ),
        help="Shell prefix used before WSL prepare/test commands.",
    )
    parser.add_argument("--require-agent-zero", action="store_true")
    parser.add_argument("--allow-initial-pass", action="store_true")
    parser.add_argument("--allow-missing-trace", action="store_true")
    parser.add_argument(
        "--missing-trace-diagnosis",
        default="External agent did not emit a structured diagnosis trace.",
    )
    parser.add_argument("--manifest-schema", type=Path, default=DEFAULT_MANIFEST_SCHEMA)
    parser.add_argument("--task-schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    parser.add_argument("--trace-schema", type=Path, default=DEFAULT_TRACE_SCHEMA)
    parser.add_argument("--trajectory-schema", type=Path, default=DEFAULT_TRAJECTORY_SCHEMA)
    args = parser.parse_args()
    if not args.finalize_existing_artifacts and not args.agent_command:
        parser.error("--agent-command is required unless --finalize-existing-artifacts is set")

    manifest = load_validated(args.manifest, args.manifest_schema)
    selected = select_runs(
        manifest["runs"],
        parse_csv_set(args.methods),
        parse_csv_set(args.run_ids),
        args.limit,
    )
    if not selected:
        print("No runs selected.", file=sys.stderr)
        return 1
    for run in selected:
        if args.finalize_existing_artifacts:
            finalize_existing_artifacts(run, manifest, args)
        else:
            run_one(run, manifest, args)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
