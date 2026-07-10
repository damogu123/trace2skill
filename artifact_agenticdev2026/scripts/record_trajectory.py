from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAJECTORY_SCHEMA = ROOT / "schemas" / "trajectory.schema.json"
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
METHODS = [
    "no_memory",
    "reflexion",
    "length_matched_reflexion",
    "generic_checklist",
    "raw_trajectory_retrieval",
    "format_shuffled_skill",
    "oracle_skill",
    "auto_skill",
]


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_nullable_bool(value: str) -> bool | None:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    raise argparse.ArgumentTypeError("expected true, false, or null")


def parse_bool(value: str) -> bool:
    parsed = parse_nullable_bool(value)
    if parsed is None:
        raise argparse.ArgumentTypeError("expected true or false")
    return parsed


def parse_key_description(value: str) -> tuple[str, str]:
    if "::" in value:
        key, description = value.split("::", 1)
        return key.strip(), description.strip()
    return value.strip(), ""


def load_task(task_path: Path | None, task_schema_path: Path) -> dict[str, Any] | None:
    if task_path is None:
        return None
    task = load_json(task_path)
    validate_instance(task, load_json(task_schema_path))
    return task


def load_cycle_file(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    raise ValueError(f"Cycle file must contain an object or array: {path}")


def load_cycles(paths: list[Path]) -> list[dict[str, Any]]:
    cycles: list[dict[str, Any]] = []
    for path in paths:
        cycles.extend(load_cycle_file(path))
    return cycles


def build_single_cycle(args: argparse.Namespace, task: dict[str, Any] | None) -> dict[str, Any]:
    test_command = args.test_command
    if test_command is None and task is not None:
        test_command = task["environment"]["test_command"]
    if test_command is None:
        raise ValueError("--test-command is required when --cycle-json is not provided")

    inspections = []
    for value in args.inspection:
        path, reason = parse_key_description(value)
        inspections.append({"path": path, "reason": reason})

    mistakes = []
    for value in args.mistake:
        mistake_type, description = parse_key_description(value)
        mistakes.append({"type": mistake_type, "description": description})

    test_passed = args.test_passed
    if test_passed is None:
        test_passed = args.solved

    return {
        "cycle_id": 1,
        "diagnosis": args.diagnosis,
        "file_inspections": inspections,
        "patch_attempt": {
            "modified_files": parse_csv(args.modified_files),
            "patch_path": args.patch_path,
            "patch_summary": args.patch_summary,
        },
        "test_rerun": {
            "command": test_command,
            "passed": test_passed,
            "log_path": args.test_log_path,
        },
        "mistakes": mistakes,
    }


def infer_failed_patch_count(cycles: list[dict[str, Any]]) -> int:
    failed = 0
    for cycle in cycles:
        patch_attempt = cycle.get("patch_attempt", {})
        modified_files = patch_attempt.get("modified_files", [])
        test_rerun = cycle.get("test_rerun", {})
        if modified_files and test_rerun.get("passed") is False:
            failed += 1
    return failed


def build_trajectory(args: argparse.Namespace, task: dict[str, Any] | None) -> dict[str, Any]:
    task_id = args.task_id
    if task_id is None and task is not None:
        task_id = task["task_id"]
    if task_id is None:
        raise ValueError("Provide --task or --task-id")

    if args.cycle_json:
        cycles = load_cycles(args.cycle_json)
    else:
        cycles = [build_single_cycle(args, task)]

    cycles_used = args.cycles_used if args.cycles_used is not None else len(cycles)
    failed_patch_count = (
        args.failed_patch_count
        if args.failed_patch_count is not None
        else infer_failed_patch_count(cycles)
    )
    total_tokens = args.input_tokens + args.output_tokens
    active_debugging_tokens = args.active_debugging_tokens
    if active_debugging_tokens is None:
        active_debugging_tokens = max(total_tokens - args.prompt_overhead_tokens, 0)

    final_test_passed = args.final_test_passed
    if final_test_passed is None:
        final_test_passed = args.solved

    negative_category = args.negative_transfer_category
    negative_reason = args.negative_transfer_reason
    if not args.negative_transfer:
        negative_category = None
        negative_reason = None
    elif negative_category is None:
        negative_category = "performance"

    return {
        "run_id": args.run_id,
        "task_id": task_id,
        "method": args.method,
        "model": args.model,
        "temperature": args.temperature,
        "budget": {
            "max_turns": args.max_turns,
            "max_tokens": args.max_tokens,
            "max_cycles": args.max_cycles,
        },
        "final_outcome": {
            "solved": args.solved,
            "final_test_passed": final_test_passed,
            "full_test_passed": args.full_test_passed,
            "broke_existing_tests": args.broke_existing_tests,
            "timeout": args.timeout,
            "cycles_used": cycles_used,
            "llm_turns": args.llm_turns,
            "tool_calls": args.tool_calls,
            "input_tokens": args.input_tokens,
            "output_tokens": args.output_tokens,
            "prompt_overhead_tokens": args.prompt_overhead_tokens,
            "active_debugging_tokens": active_debugging_tokens,
            "failed_patch_count": failed_patch_count,
        },
        "cycles": cycles,
        "negative_transfer": {
            "detected": args.negative_transfer,
            "category": negative_category,
            "reason": negative_reason,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create and validate one trajectory JSON record for a debugging-agent run."
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--task", type=Path, default=None, help="Optional task JSON; supplies task_id and test command")
    parser.add_argument("--task-id", default=None, help="Required if --task is omitted")
    parser.add_argument("--method", choices=METHODS, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--max-tokens", type=int, default=60000)
    parser.add_argument("--max-cycles", type=int, default=10)
    parser.add_argument("--solved", action="store_true")
    parser.add_argument("--final-test-passed", type=parse_bool, default=None)
    parser.add_argument("--full-test-passed", type=parse_nullable_bool, default=None)
    parser.add_argument("--broke-existing-tests", type=parse_nullable_bool, default=None)
    parser.add_argument("--timeout", action="store_true")
    parser.add_argument("--cycles-used", type=int, default=None)
    parser.add_argument("--llm-turns", type=int, default=0)
    parser.add_argument("--tool-calls", type=int, default=0)
    parser.add_argument("--input-tokens", type=int, default=0)
    parser.add_argument("--output-tokens", type=int, default=0)
    parser.add_argument("--prompt-overhead-tokens", type=int, default=0)
    parser.add_argument("--active-debugging-tokens", type=int, default=None)
    parser.add_argument("--failed-patch-count", type=int, default=None)
    parser.add_argument(
        "--cycle-json",
        type=Path,
        action="append",
        default=[],
        help="Cycle JSON object or array. Repeat to merge multiple files.",
    )
    parser.add_argument("--diagnosis", default="Manual trajectory record.")
    parser.add_argument(
        "--inspection",
        action="append",
        default=[],
        metavar="PATH::REASON",
        help="File inspection for generated single-cycle records. Repeatable.",
    )
    parser.add_argument("--modified-files", default="", help="Comma-separated modified files")
    parser.add_argument("--patch-path", default=None)
    parser.add_argument("--patch-summary", default=None)
    parser.add_argument("--test-command", default=None)
    parser.add_argument("--test-passed", type=parse_bool, default=None)
    parser.add_argument("--test-log-path", default="logs/final_test.log")
    parser.add_argument(
        "--mistake",
        action="append",
        default=[],
        metavar="TYPE::DESCRIPTION",
        help="Mistake annotation for generated single-cycle records. Repeatable.",
    )
    parser.add_argument("--negative-transfer", action="store_true")
    parser.add_argument(
        "--negative-transfer-category",
        choices=["performance", "behavioral", "self_contradictory"],
        default=None,
    )
    parser.add_argument("--negative-transfer-reason", default=None)
    parser.add_argument("--schema", type=Path, default=DEFAULT_TRAJECTORY_SCHEMA)
    parser.add_argument("--task-schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    args = parser.parse_args()

    task = load_task(args.task, args.task_schema)
    trajectory = build_trajectory(args, task)
    validate_instance(trajectory, load_json(args.schema))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(trajectory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
