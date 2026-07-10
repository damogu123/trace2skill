from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_SCHEMA = ROOT / "schemas" / "run_manifest.schema.json"
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
REQUIRED_AGENT_PLACEHOLDERS = ["{prompt_path}", "{repo_dir}", "{trace_path}"]
FORBIDDEN_COMMAND_FRAGMENTS = [
    "mock_agent_patch.py",
    "run_manual_smoke_pilot.py",
    "manual-smoke",
]
FORBIDDEN_PROMPT_MARKERS = [
    "MEMORY ARTIFACT MISSING",
]


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def load_validated(path: Path, schema_path: Path) -> dict[str, Any]:
    data = load_json(path)
    validate_instance(data, load_json(schema_path))
    return data


def add(messages: list[str], text: str) -> None:
    messages.append(text)


def check_agent_command(
    command: str | None,
    errors: list[str],
    warnings: list[str],
    require_agent_command: bool,
) -> None:
    if not command:
        message = "No --agent-command provided; execution command has not been checked."
        if require_agent_command:
            add(errors, message)
        else:
            add(warnings, message)
        return
    for placeholder in REQUIRED_AGENT_PLACEHOLDERS:
        if placeholder not in command:
            add(errors, f"Agent command is missing required placeholder {placeholder}.")
    for fragment in FORBIDDEN_COMMAND_FRAGMENTS:
        if fragment.lower() in command.lower():
            add(errors, f"Agent command contains smoke/mock fragment: {fragment}.")


def check_manifest_metadata(
    manifest: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    require_real_model: bool,
) -> None:
    model = str(manifest.get("model", ""))
    if "placeholder" in model.lower():
        message = f"Manifest model is still a placeholder: {model!r}."
        if require_real_model:
            add(errors, message)
        else:
            add(warnings, message)
    if manifest.get("temperature") != 0:
        add(warnings, "Temperature is not 0; deterministic comparison may be harder.")


def check_task(
    task_path_text: str,
    task_schema: Path,
    require_split: str | None,
    errors: list[str],
) -> dict[str, Any] | None:
    task_path = resolve_project_path(task_path_text)
    if not task_path.exists():
        add(errors, f"Task file missing: {task_path_text}")
        return None
    try:
        task = load_validated(task_path, task_schema)
    except Exception as exc:
        add(errors, f"Task validation failed for {task_path_text}: {exc}")
        return None
    if require_split and task.get("split") != require_split:
        add(errors, f"Task {task['task_id']} split is {task.get('split')!r}, expected {require_split!r}.")
    return task


def check_text_markers(path: Path, markers: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [marker for marker in markers if marker in text]


def check_prepare_summary(
    run: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    workspace_path = resolve_project_path(run["workspace_path"])
    checkout_root = workspace_path.parent
    summary_path = checkout_root / "prepare_summary.json"
    if not workspace_path.exists():
        add(errors, f"Workspace missing for {run['run_id']}: {run['workspace_path']}")
        return
    if not summary_path.exists():
        add(errors, f"Prepare summary missing for {run['run_id']}: {summary_path}")
        return
    try:
        summary = load_json(summary_path)
    except Exception as exc:
        add(errors, f"Prepare summary unreadable for {run['run_id']}: {exc}")
        return
    if summary.get("install_returncode") != 0:
        add(errors, f"Install failed for {run['run_id']}: {summary.get('install_returncode')}")
    if summary.get("initial_failure_reproduced") is not True:
        add(errors, f"Initial failure not reproduced for {run['run_id']}.")
    if summary.get("reference_patch_applied") is True:
        add(warnings, f"{run['run_id']} workspace summary includes reference patch verification; ensure run workspace was re-prepared after reference checks.")


def check_run(
    run: dict[str, Any],
    task_schema: Path,
    require_split: str | None,
    allow_existing_trajectories: bool,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    status = {
        "run_id": run["run_id"],
        "method": run["method"],
        "task_id": run["task_id"],
        "ready": True,
    }
    task = check_task(run["task_path"], task_schema, require_split, errors)
    if task and task["task_id"] != run["task_id"]:
        add(errors, f"Run {run['run_id']} task_id mismatch: manifest={run['task_id']} task={task['task_id']}")

    if run.get("prompt_status") != "ready":
        add(errors, f"Run {run['run_id']} prompt_status is {run.get('prompt_status')!r}.")

    prompt_path = resolve_project_path(run["prompt_path"])
    if not prompt_path.exists():
        add(errors, f"Prompt missing for {run['run_id']}: {run['prompt_path']}")
    else:
        markers = check_text_markers(prompt_path, FORBIDDEN_PROMPT_MARKERS)
        for marker in markers:
            add(errors, f"Prompt for {run['run_id']} contains marker: {marker}")

    memory_path_text = run.get("memory_path")
    if run.get("requires_memory_artifact") and not memory_path_text:
        add(errors, f"Run {run['run_id']} requires memory but memory_path is null.")
    if memory_path_text and not resolve_project_path(memory_path_text).exists():
        add(errors, f"Memory artifact missing for {run['run_id']}: {memory_path_text}")

    baseline_context_path = run.get("baseline_context_path")
    if baseline_context_path and not resolve_project_path(baseline_context_path).exists():
        add(errors, f"Baseline context missing for {run['run_id']}: {baseline_context_path}")

    check_prepare_summary(run, errors, warnings)

    trajectory_path = resolve_project_path(run["trajectory_path"])
    if trajectory_path.exists() and not allow_existing_trajectories:
        add(errors, f"Trajectory already exists for {run['run_id']}: {run['trajectory_path']}")

    return status


def summarize_counts(manifest: dict[str, Any]) -> dict[str, Any]:
    methods: dict[str, int] = {}
    tasks: dict[str, int] = {}
    for run in manifest["runs"]:
        methods[run["method"]] = methods.get(run["method"], 0) + 1
        tasks[run["task_id"]] = tasks.get(run["task_id"], 0) + 1
    return {
        "runs": len(manifest["runs"]),
        "methods": methods,
        "tasks": tasks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight-check a manifest before running real external-agent experiments."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--agent-command", default=None)
    parser.add_argument("--require-split", choices=["train", "heldout", "adversarial"], default=None)
    parser.add_argument("--require-real-model", action="store_true")
    parser.add_argument("--require-agent-command", action="store_true")
    parser.add_argument("--allow-existing-trajectories", action="store_true")
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--manifest-schema", type=Path, default=DEFAULT_MANIFEST_SCHEMA)
    parser.add_argument("--task-schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    manifest = load_validated(args.manifest, args.manifest_schema)
    check_manifest_metadata(manifest, errors, warnings, args.require_real_model)
    check_agent_command(args.agent_command, errors, warnings, args.require_agent_command)

    run_statuses = []
    for run in manifest["runs"]:
        before_error_count = len(errors)
        status = check_run(
            run,
            args.task_schema,
            args.require_split,
            args.allow_existing_trajectories,
            errors,
            warnings,
        )
        if len(errors) > before_error_count:
            status["ready"] = False
        run_statuses.append(status)

    report = {
        "manifest": str(args.manifest),
        "experiment_id": manifest["experiment_id"],
        "summary": summarize_counts(manifest),
        "ready": not errors,
        "errors": errors,
        "warnings": warnings,
        "runs": run_statuses,
    }

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {args.output_json}")

    print(f"experiment_id={manifest['experiment_id']}")
    print(f"runs={report['summary']['runs']} ready={report['ready']}")
    print(f"errors={len(errors)} warnings={len(warnings)}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
