from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "task.schema.json"


def parse_checkout_id(value: str) -> str:
    if not value or value in {".", ".."}:
        raise argparse.ArgumentTypeError("checkout id must be a non-empty path segment")
    if "/" in value or "\\" in value:
        raise argparse.ArgumentTypeError("checkout id must not contain path separators")
    return value


def ensure_within(parent: Path, child: Path) -> None:
    parent_resolved = parent.resolve()
    child_resolved = child.resolve()
    try:
        child_resolved.relative_to(parent_resolved)
    except ValueError as exc:
        raise ValueError(f"Refusing to operate outside workspace: {child_resolved}") from exc


def remove_tree(path: Path) -> None:
    def make_writable_and_retry(function: Any, target: str, exc_info: Any) -> None:
        try:
            os.chmod(target, stat.S_IWRITE)
            function(target)
        except Exception as retry_error:
            raise retry_error

    shutil.rmtree(path, onexc=make_writable_and_retry)


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


def cleanup_pipenv_environment(cwd: Path, log_path: Path, timeout: int) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        subprocess.run(
            "pipenv --rm",
            cwd=cwd,
            shell=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            env=os.environ.copy(),
        )


def test_command_environment_failed(log_path: Path) -> bool:
    if not log_path.exists():
        return False
    text = log_path.read_text(encoding="utf-8", errors="replace").lower()
    environment_markers = [
        "the command pytest could not be found",
        "no module named pytest",
        "pytest: not found",
        "command not found: pytest",
        "not found within path or pipfile's [scripts]",
    ]
    return any(marker in text for marker in environment_markers)


def run_git(args: list[str], cwd: Path | None = None, attempts: int = 3) -> None:
    last_error: subprocess.CalledProcessError | None = None
    for attempt in range(1, attempts + 1):
        process = subprocess.run(["git", *args], cwd=cwd)
        if process.returncode == 0:
            return
        last_error = subprocess.CalledProcessError(process.returncode, process.args)
        if attempt < attempts:
            time.sleep(attempt * 2)
    if last_error is not None:
        raise last_error


def git_remote_origin(repo_dir: Path) -> str | None:
    process = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=repo_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if process.returncode != 0:
        return None
    return process.stdout.strip() or None


def find_reusable_checkout(url: str, target_dir: Path) -> Path | None:
    workspace = target_dir.parent.parent
    if not workspace.exists():
        return None

    candidates = sorted(
        workspace.glob("*/repo"),
        key=lambda path: path.stat().st_mtime if path.exists() else 0,
        reverse=True,
    )
    target_resolved = target_dir.resolve()
    for candidate in candidates:
        if not (candidate / ".git").exists():
            continue
        if candidate.resolve() == target_resolved:
            continue
        if git_remote_origin(candidate) == url:
            return candidate
    return None


def shallow_fetch_checkout(url: str, commit: str, target_dir: Path) -> None:
    run_git(["init", str(target_dir)])
    run_git(["remote", "add", "origin", url], cwd=target_dir)
    run_git(["fetch", "--depth=1", "origin", commit], cwd=target_dir)
    run_git(["checkout", "--detach", "FETCH_HEAD"], cwd=target_dir)


def checkout_commit(repo_dir: Path, commit: str, url: str | None = None) -> None:
    try:
        run_git(["checkout", commit], cwd=repo_dir)
    except subprocess.CalledProcessError:
        if not url:
            raise
        run_git(["fetch", "--depth=1", url, commit], cwd=repo_dir)
        run_git(["checkout", "--detach", "FETCH_HEAD"], cwd=repo_dir)


def materialize_repo(task: dict[str, Any], task_file: Path, target_dir: Path) -> None:
    repo = task["repo"]
    url = repo.get("url")
    if not url:
        raise ValueError("repo.url is required for prepare_task.py")
    commit = repo["commit"]

    if repo["source"] == "local":
        source_path = Path(url).expanduser()
        if not source_path.is_absolute():
            source_path = (task_file.parent / source_path).resolve()
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        shutil.copytree(source_path, target_dir)
    else:
        reusable_checkout = find_reusable_checkout(url, target_dir)
        if reusable_checkout is None:
            try:
                shallow_fetch_checkout(url, commit, target_dir)
            except subprocess.CalledProcessError:
                if target_dir.exists():
                    remove_tree(target_dir)
                run_git(["clone", url, str(target_dir)])
        else:
            try:
                run_git(["clone", "--no-hardlinks", str(reusable_checkout), str(target_dir)], attempts=1)
            except subprocess.CalledProcessError:
                if target_dir.exists():
                    remove_tree(target_dir)
                try:
                    shallow_fetch_checkout(url, commit, target_dir)
                except subprocess.CalledProcessError:
                    if target_dir.exists():
                        remove_tree(target_dir)
                    run_git(["clone", url, str(target_dir)])

    if not (repo["source"] == "local" and commit.upper() == "WORKTREE"):
        checkout_commit(target_dir, commit, url)


def apply_reference_patch(task: dict[str, Any], task_file: Path, repo_dir: Path) -> bool:
    patch_path = task.get("ground_truth", {}).get("patch_path")
    if not patch_path:
        raise ValueError("ground_truth.patch_path is required for --verify-reference")
    resolved_patch = (task_file.parent / patch_path).resolve()
    if not resolved_patch.exists():
        raise FileNotFoundError(resolved_patch)
    process = subprocess.run(
        ["git", "apply", str(resolved_patch)],
        cwd=repo_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if process.returncode != 0:
        print(process.stdout, file=sys.stderr)
        return False
    return True


def apply_dataset_patch(task: dict[str, Any], task_file: Path, repo_dir: Path) -> bool:
    patch_path = task.get("benchmark", {}).get("test_patch_path")
    if not patch_path:
        return True
    resolved_patch = (task_file.parent / patch_path).resolve()
    if not resolved_patch.exists():
        raise FileNotFoundError(resolved_patch)
    process = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", str(resolved_patch)],
        cwd=repo_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if process.returncode != 0:
        print(process.stdout, file=sys.stderr)
        return False
    return True


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare and reproducibility-check a debugging task from task.schema.json."
    )
    parser.add_argument("task", type=Path, help="Task JSON file")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=ROOT / "workspaces",
        help="Directory where task checkouts are created",
    )
    parser.add_argument(
        "--checkout-id",
        type=parse_checkout_id,
        default=None,
        help="Optional checkout directory name under --workspace; defaults to task_id",
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Task schema path")
    parser.add_argument(
        "--verify-reference",
        action="store_true",
        help="Apply ground_truth.patch_path and verify the failing test passes after the patch",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print planned actions without cloning or running commands",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove an existing checkout for this task before preparing it",
    )
    args = parser.parse_args()

    task = load_json(args.task)
    validate_instance(task, load_json(args.schema))

    task_id = task["task_id"]
    checkout_id = args.checkout_id or task_id
    checkout_root = args.workspace / checkout_id
    repo_dir = checkout_root / "repo"
    log_dir = checkout_root / "logs"
    summary_path = checkout_root / "prepare_summary.json"
    timeout = int(task["environment"]["timeout_seconds"])

    if args.dry_run:
        print(f"Task {task_id} is valid.")
        print(f"Would materialize repo at {repo_dir}")
        print(f"Would run install command: {task['environment']['install_command']}")
        print(f"Would run failing test command: {task['environment']['test_command']}")
        if args.verify_reference:
            print("Would apply reference patch and rerun failing test.")
        return 0

    if repo_dir.exists():
        if not args.force:
            print(f"Checkout already exists: {repo_dir}. Use --force to recreate it.", file=sys.stderr)
            return 1
        ensure_within(args.workspace, checkout_root)
        remove_tree(checkout_root)

    checkout_root.mkdir(parents=True, exist_ok=True)
    materialize_repo(task, args.task, repo_dir)
    dataset_patch_applied = apply_dataset_patch(task, args.task, repo_dir)
    if not dataset_patch_applied:
        print("Dataset test patch did not apply.", file=sys.stderr)
        return 1

    if "pipenv" in task["environment"]["install_command"]:
        cleanup_pipenv_environment(repo_dir, log_dir / "pipenv_cleanup.log", timeout)

    install_code = run_command(
        task["environment"]["install_command"],
        repo_dir,
        log_dir / "install.log",
        timeout,
    )
    initial_code = None
    initial_log_path = log_dir / "initial_failure.log"
    if install_code == 0:
        initial_code = run_command(
            task["environment"]["test_command"],
            repo_dir,
            initial_log_path,
            timeout,
        )
    initial_environment_failed = (
        initial_code is not None
        and initial_code != 0
        and test_command_environment_failed(initial_log_path)
    )

    summary: dict[str, Any] = {
        "task_id": task_id,
        "repo_dir": str(repo_dir.resolve()),
        "status": None,
        "failure_stage": None,
        "install_returncode": install_code,
        "initial_test_returncode": initial_code,
        "initial_failure_reproduced": initial_code is not None and initial_code != 0 and not initial_environment_failed,
        "initial_test_environment_failed": initial_environment_failed,
        "dataset_test_patch_applied": dataset_patch_applied,
        "reference_patch_applied": None,
        "reference_test_returncode": None,
        "reference_test_passed": None,
    }

    if install_code != 0:
        summary["status"] = "install_failed"
        summary["failure_stage"] = "install"
    elif initial_environment_failed:
        summary["status"] = "test_command_failed"
        summary["failure_stage"] = "initial_test_environment"
    elif initial_code == 0:
        summary["status"] = "initial_failure_not_reproduced"
        summary["failure_stage"] = "initial_test"
    elif args.verify_reference:
        applied = apply_reference_patch(task, args.task, repo_dir)
        summary["reference_patch_applied"] = applied
        if applied:
            reference_code = run_command(
                task["environment"]["test_command"],
                repo_dir,
                log_dir / "reference_test.log",
                timeout,
            )
            reference_environment_failed = test_command_environment_failed(log_dir / "reference_test.log")
            summary["reference_test_returncode"] = reference_code
            summary["reference_test_passed"] = reference_code == 0
            summary["reference_test_environment_failed"] = reference_environment_failed
            if reference_code == 0:
                summary["status"] = "pilot_ready"
            elif reference_environment_failed:
                summary["status"] = "reference_test_command_failed"
                summary["failure_stage"] = "reference_test_environment"
            else:
                summary["status"] = "reference_test_failed"
                summary["failure_stage"] = "reference_test"
        else:
            summary["status"] = "reference_patch_failed"
            summary["failure_stage"] = "reference_patch"
    else:
        summary["status"] = "initial_failure_reproduced"

    write_summary(summary_path, summary)
    print(f"Wrote {summary_path}")

    if install_code != 0:
        print("Install command failed.", file=sys.stderr)
        return 1
    if initial_code == 0:
        print("Initial failing test did not fail.", file=sys.stderr)
        return 1
    if args.verify_reference and not summary["reference_test_passed"]:
        print("Reference patch did not make the failing test pass.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
