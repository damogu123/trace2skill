from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_SCHEMA = ROOT / "schemas" / "run_manifest.schema.json"
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
DEFAULT_TRAJECTORY_SCHEMA = ROOT / "schemas" / "trajectory.schema.json"


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def estimate_tokens(text: str) -> int:
    # Rough smoke-test estimate only. Real experiments must use model-reported usage.
    return max(1, (len(text) + 3) // 4) if text else 0


def load_validated_json(path: Path, schema_path: Path) -> dict[str, Any]:
    data = load_json(path)
    validate_instance(data, load_json(schema_path))
    return data


def run_command(command: str, cwd: Path, log_path: Path, timeout: int) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    src_path = str((cwd / "src").resolve())
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path
        if not existing_pythonpath
        else src_path + os.pathsep + existing_pythonpath
    )
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        process = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            env=env,
        )
    return process.returncode


def write_patch(old_text: str, new_text: str, display_path: str, patch_path: Path) -> None:
    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=f"a/{display_path}",
        tofile=f"b/{display_path}",
    )
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_text("".join(diff), encoding="utf-8", newline="\n")


def apply_text_replacement(file_path: Path, old: str, new: str, patch_path: Path, display_path: str) -> None:
    source = file_path.read_text(encoding="utf-8")
    if old not in source:
        raise ValueError(f"Old text not found in {file_path}. Reprepare the workspace before rerunning.")
    updated = source.replace(old, new, 1)
    write_patch(source, updated, display_path, patch_path)
    file_path.write_text(updated, encoding="utf-8", newline="\n")


def context_tokens(run: dict[str, Any]) -> int:
    total = 0
    for key in ("baseline_context_path", "memory_path"):
        path_text = run.get(key)
        if path_text:
            total += estimate_tokens(resolve_project_path(path_text).read_text(encoding="utf-8"))
    return total


def build_trajectory(
    run: dict[str, Any],
    task: dict[str, Any],
    prompt_tokens: int,
    prompt_overhead_tokens: int,
    narrow_code: int,
    full_code: int | None,
    args: argparse.Namespace,
) -> dict[str, Any]:
    solved = narrow_code == 0 and (full_code in (0, None))
    output_text = "\n".join([args.diagnosis, args.patch_summary])
    output_tokens = estimate_tokens(output_text)
    total_tokens = prompt_tokens + output_tokens
    full_test_passed = None if full_code is None else full_code == 0
    broke_existing = None
    if full_code is not None:
        broke_existing = narrow_code == 0 and full_code != 0

    return {
        "run_id": run["run_id"],
        "task_id": run["task_id"],
        "method": run["method"],
        "model": args.model,
        "temperature": 0.0,
        "budget": {
            "max_turns": args.max_turns,
            "max_tokens": args.max_tokens,
            "max_cycles": args.max_cycles,
        },
        "final_outcome": {
            "solved": solved,
            "final_test_passed": narrow_code == 0,
            "full_test_passed": full_test_passed,
            "broke_existing_tests": broke_existing,
            "timeout": False,
            "cycles_used": 1,
            "llm_turns": 4,
            "tool_calls": 6 if full_code is not None else 5,
            "input_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "prompt_overhead_tokens": prompt_overhead_tokens,
            "active_debugging_tokens": max(total_tokens - prompt_overhead_tokens, 0),
            "failed_patch_count": 0 if narrow_code == 0 else 1,
        },
        "cycles": [
            {
                "cycle_id": 1,
                "diagnosis": args.diagnosis,
                "file_inspections": [
                    {
                        "path": args.target_file,
                        "reason": args.inspection_reason,
                    }
                ],
                "patch_attempt": {
                    "modified_files": [args.target_file],
                    "patch_path": str((resolve_project_path(run["artifacts_dir"]) / "cycle_1.patch").relative_to(ROOT)).replace("\\", "/"),
                    "patch_summary": args.patch_summary,
                },
                "test_rerun": {
                    "command": task["environment"]["test_command"],
                    "passed": narrow_code == 0,
                    "log_path": str((resolve_project_path(run["artifacts_dir"]) / "cycle_1.log").relative_to(ROOT)).replace("\\", "/"),
                },
                "mistakes": [],
            }
        ],
        "negative_transfer": {
            "detected": False,
            "category": None,
            "reason": None,
        },
    }


def run_one(run: dict[str, Any], args: argparse.Namespace) -> None:
    task = load_validated_json(resolve_project_path(run["task_path"]), args.task_schema)
    repo_dir = resolve_project_path(run["workspace_path"])
    artifacts_dir = resolve_project_path(run["artifacts_dir"])
    trajectory_path = resolve_project_path(run["trajectory_path"])
    prompt_path = resolve_project_path(run["prompt_path"])
    target_file = repo_dir / args.target_file
    timeout = int(task["environment"]["timeout_seconds"])

    if not repo_dir.exists():
        raise FileNotFoundError(f"Workspace missing for {run['run_id']}: {repo_dir}")
    if trajectory_path.exists() and not args.force:
        raise FileExistsError(f"Trajectory exists: {trajectory_path}. Use --force to overwrite.")

    reproduce_code = run_command(
        task["environment"]["test_command"],
        repo_dir,
        artifacts_dir / "reproduce.log",
        timeout,
    )
    if reproduce_code == 0 and not args.allow_initial_pass:
        raise RuntimeError(f"Initial failure did not reproduce for {run['run_id']}")

    apply_text_replacement(
        target_file,
        args.old_text,
        args.new_text,
        artifacts_dir / "cycle_1.patch",
        args.target_file,
    )

    narrow_code = run_command(
        task["environment"]["test_command"],
        repo_dir,
        artifacts_dir / "cycle_1.log",
        timeout,
    )
    full_command = task["environment"].get("full_test_command")
    full_code = None
    if full_command:
        full_code = run_command(full_command, repo_dir, artifacts_dir / "full_test.log", timeout)

    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_tokens = estimate_tokens(prompt_text)
    prompt_overhead_tokens = context_tokens(run)
    trajectory = build_trajectory(
        run,
        task,
        prompt_tokens,
        prompt_overhead_tokens,
        narrow_code,
        full_code,
        args,
    )
    validate_instance(trajectory, load_json(args.trajectory_schema))
    trajectory_path.parent.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text(
        json.dumps(trajectory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"{run['run_id']}: reproduce={reproduce_code} narrow={narrow_code} "
        f"full={full_code} trajectory={trajectory_path}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run a deterministic manual smoke pilot over a manifest. "
            "This is for harness validation only, not paper evidence."
        )
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--target-file", required=True)
    parser.add_argument("--old-text", required=True)
    parser.add_argument("--new-text", required=True)
    parser.add_argument("--diagnosis", required=True)
    parser.add_argument("--inspection-reason", required=True)
    parser.add_argument("--patch-summary", required=True)
    parser.add_argument("--model", default="manual-smoke-agent")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--max-tokens", type=int, default=60000)
    parser.add_argument("--max-cycles", type=int, default=10)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--allow-initial-pass", action="store_true")
    parser.add_argument("--manifest-schema", type=Path, default=DEFAULT_MANIFEST_SCHEMA)
    parser.add_argument("--task-schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    parser.add_argument("--trajectory-schema", type=Path, default=DEFAULT_TRAJECTORY_SCHEMA)
    args = parser.parse_args()

    manifest = load_validated_json(args.manifest, args.manifest_schema)
    for run in manifest["runs"]:
        run_one(run, args)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
