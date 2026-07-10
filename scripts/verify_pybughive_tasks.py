from __future__ import annotations

import argparse
import csv
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance
from check_pybughive_environment import summarize as summarize_environment


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
DEFAULT_WSL_ENV_PREFIX = (
    "export PATH=$HOME/.local/bin:$PATH; "
    "export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple; "
    "export PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn; "
    "export PIP_DEFAULT_TIMEOUT=120; "
    "export PIPENV_PYPI_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple; "
    "export PIPENV_TIMEOUT=120"
)


def iter_json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(item for item in path.rglob("*.json") if item.is_file())
    raise FileNotFoundError(path)


def load_pybughive_tasks(paths: list[Path], schema_path: Path) -> list[tuple[Path, dict[str, Any]]]:
    schema = load_json(schema_path)
    tasks: list[tuple[Path, dict[str, Any]]] = []
    for path in paths:
        for file_path in iter_json_files(path):
            data = load_json(file_path)
            validate_instance(data, schema)
            if data["repo"]["source"] == "pybughive":
                tasks.append((file_path, data))
    return tasks


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


def command_for_task(
    task_path: Path,
    task: dict[str, Any],
    workspace: Path,
    force: bool,
    runner: str,
) -> str | list[str]:
    if runner == "wsl":
        parts = [
            "python3",
            "scripts/prepare_task.py",
            shlex.quote(project_relative(task_path)),
            "--workspace",
            shlex.quote(project_relative(workspace)),
            "--checkout-id",
            shlex.quote(task["task_id"]),
            "--verify-reference",
        ]
        if force:
            parts.append("--force")
        return " ".join(parts)

    command: list[str] = [
        sys.executable,
        str(ROOT / "scripts" / "prepare_task.py"),
        str(task_path),
        "--workspace",
        str(workspace),
        "--checkout-id",
        task["task_id"],
        "--verify-reference",
    ]
    if force:
        command.append("--force")
    return command


def run_prepare_command(
    command: str | list[str],
    *,
    runner: str,
    log_path: Path,
    timeout: int,
    wsl_distro: str,
    wsl_env_prefix: str,
) -> int:
    if runner == "wsl":
        bash_parts = []
        if wsl_env_prefix.strip():
            bash_parts.append(wsl_env_prefix.strip())
        bash_parts.append(f"cd {shlex.quote(to_wsl_path(ROOT))}")
        bash_parts.append(str(command))
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
        cwd = None
    else:
        process_command = command
        shell = False
        cwd = ROOT

    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        process = subprocess.run(
            process_command,
            cwd=cwd,
            shell=shell,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
    return process.returncode


def run_task(
    task_path: Path,
    task: dict[str, Any],
    workspace: Path,
    force: bool,
    timeout: int,
    runner: str,
    wsl_distro: str,
    wsl_env_prefix: str,
) -> dict[str, Any]:
    checkout_root = workspace / task["task_id"]
    log_path = checkout_root / "verify_task.log"
    summary_path = checkout_root / "prepare_summary.json"
    command = command_for_task(task_path, task, workspace, force, runner)
    checkout_root.mkdir(parents=True, exist_ok=True)
    returncode = run_prepare_command(
        command,
        runner=runner,
        log_path=log_path,
        timeout=timeout,
        wsl_distro=wsl_distro,
        wsl_env_prefix=wsl_env_prefix,
    )
    summary: dict[str, Any] = {}
    if summary_path.exists():
        summary = load_json(summary_path)
    return {
        "task_id": task["task_id"],
        "split": task["split"],
        "project": task["benchmark"]["project"],
        "issue_id": task["benchmark"]["issue_id"],
        "returncode": returncode,
        "runner": runner,
        "status": summary.get("status", "missing_summary"),
        "failure_stage": summary.get("failure_stage"),
        "install_returncode": summary.get("install_returncode"),
        "initial_test_returncode": summary.get("initial_test_returncode"),
        "initial_failure_reproduced": summary.get("initial_failure_reproduced"),
        "initial_test_environment_failed": summary.get("initial_test_environment_failed"),
        "dataset_test_patch_applied": summary.get("dataset_test_patch_applied"),
        "reference_patch_applied": summary.get("reference_patch_applied"),
        "reference_test_returncode": summary.get("reference_test_returncode"),
        "reference_test_passed": summary.get("reference_test_passed"),
        "reference_test_environment_failed": summary.get("reference_test_environment_failed"),
        "log_path": str(log_path),
        "summary_path": str(summary_path),
    }


def blocked_rows(tasks: list[tuple[Path, dict[str, Any]]], reason: str, runner: str) -> list[dict[str, Any]]:
    rows = []
    for _path, task in tasks:
        rows.append(
            {
                "task_id": task["task_id"],
                "split": task["split"],
                "project": task["benchmark"]["project"],
                "issue_id": task["benchmark"]["issue_id"],
                "runner": runner,
                "returncode": None,
                "status": "environment_blocked",
                "failure_stage": "environment",
                "install_returncode": None,
                "initial_test_returncode": None,
                "initial_failure_reproduced": None,
                "dataset_test_patch_applied": None,
                "reference_patch_applied": None,
                "reference_test_returncode": None,
                "reference_test_passed": None,
                "log_path": None,
                "summary_path": None,
                "block_reason": reason,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]], env_report: dict[str, Any], runner: str) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status"))
        counts[status] = counts.get(status, 0) + 1
    lines = [
        "# PyBugHive Reproducibility Verification",
        "",
        f"- Tasks: {len(rows)}",
        f"- Runner: `{runner}`",
        f"- Environment ready: `{str(env_report['ready']).lower()}`",
        f"- Recommended path: `{env_report['recommended_path']}`",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(
        [
            "",
            "## Task Results",
            "",
            "| Task | Split | Project | Issue | Status | Failure Stage |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| `{task_id}` | {split} | {project} | {issue_id} | `{status}` | {failure_stage} |".format(
                task_id=row.get("task_id"),
                split=row.get("split"),
                project=row.get("project"),
                issue_id=row.get("issue_id"),
                status=row.get("status"),
                failure_stage=row.get("failure_stage") or "",
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run prepare_task.py --verify-reference over PyBugHive tasks and summarize reproducibility."
    )
    parser.add_argument("tasks", nargs="*", type=Path, default=[ROOT / "tasks" / "pybughive"])
    parser.add_argument("--schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    parser.add_argument("--workspace", type=Path, default=ROOT / "workspaces" / "pybughive_verify")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--execute-when-env-blocked", action="store_true")
    parser.add_argument("--runner", choices=["native", "wsl"], default="native")
    parser.add_argument("--wsl-distro", default="Ubuntu-24.04")
    parser.add_argument("--wsl-env-prefix", default=DEFAULT_WSL_ENV_PREFIX)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--output-json", type=Path, default=ROOT / "results" / "pybughive_reproducibility_status.json")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "results" / "pybughive_reproducibility_status.csv")
    parser.add_argument("--output-md", type=Path, default=ROOT / "results" / "pybughive_reproducibility_status.md")
    args = parser.parse_args()

    tasks = load_pybughive_tasks(args.tasks, args.schema)
    if args.limit is not None:
        tasks = tasks[: args.limit]
    if not tasks:
        print("No PyBugHive tasks found.", file=sys.stderr)
        return 1

    env_report = summarize_environment([task for _path, task in tasks])
    if args.runner == "native" and not env_report["ready"] and not args.execute_when_env_blocked:
        reason = "environment is missing Docker or native pipenv plus required Python versions"
        rows = blocked_rows(tasks, reason, args.runner)
    else:
        rows = [
            run_task(
                task_path,
                task,
                args.workspace,
                args.force,
                args.timeout,
                args.runner,
                args.wsl_distro,
                args.wsl_env_prefix,
            )
            for task_path, task in tasks
        ]

    output = {
        "environment": env_report,
        "runner": args.runner,
        "n_tasks": len(tasks),
        "results": rows,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows, env_report, args.runner)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if all(row.get("status") == "pilot_ready" for row in rows) else 2


if __name__ == "__main__":
    sys.exit(main())
