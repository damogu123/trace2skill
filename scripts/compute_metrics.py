from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAJECTORY_SCHEMA = ROOT / "schemas" / "trajectory.schema.json"
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
GROUP_FIELDS = {"method", "task_id", "split", "bug_family", "source"}


def iter_json_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(item for item in path.rglob("*.json") if item.is_file()))
        else:
            raise FileNotFoundError(path)
    return sorted(files)


def load_validated_files(paths: list[Path], schema_path: Path) -> list[tuple[Path, dict[str, Any]]]:
    schema = load_json(schema_path)
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for file_path in iter_json_files(paths):
        data = load_json(file_path)
        validate_instance(data, schema)
        loaded.append((file_path, data))
    return loaded


def load_task_index(paths: list[Path], schema_path: Path) -> dict[str, dict[str, Any]]:
    if not paths:
        return {}
    return {data["task_id"]: data for _path, data in load_validated_files(paths, schema_path)}


def parse_group_fields(value: str) -> list[str]:
    fields = [item.strip() for item in value.split(",") if item.strip()]
    unknown = sorted(set(fields) - GROUP_FIELDS)
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown group fields: {', '.join(unknown)}")
    return fields or ["method"]


def safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def round_or_none(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def is_repeated_mistake(mistake_type: str) -> bool:
    lowered = mistake_type.lower()
    return "repeat" in lowered or "same_patch" in lowered or "retry" in lowered


def run_stats(trajectory: dict[str, Any]) -> dict[str, Any]:
    outcome = trajectory["final_outcome"]
    input_tokens = outcome["input_tokens"]
    output_tokens = outcome["output_tokens"]
    total_tokens = input_tokens + output_tokens
    prompt_overhead_tokens = outcome.get("prompt_overhead_tokens", 0)
    active_tokens = outcome.get("active_debugging_tokens")
    if active_tokens is None:
        active_tokens = max(total_tokens - prompt_overhead_tokens, 0)

    total_cycles = len(trajectory["cycles"])
    mistake_count = 0
    repeated_mistake_count = 0
    for cycle in trajectory["cycles"]:
        for mistake in cycle.get("mistakes", []):
            mistake_count += 1
            if is_repeated_mistake(str(mistake.get("type", ""))):
                repeated_mistake_count += 1

    negative_transfer = trajectory.get("negative_transfer", {}).get("detected", False)
    broke_existing = outcome.get("broke_existing_tests")

    return {
        "task_id": trajectory["task_id"],
        "solved": bool(outcome["solved"]),
        "cycles_used": outcome["cycles_used"],
        "total_tokens": total_tokens,
        "active_debugging_tokens": active_tokens,
        "prompt_overhead_tokens": prompt_overhead_tokens,
        "failed_patch_count": outcome.get("failed_patch_count", 0),
        "cycle_records": total_cycles,
        "mistake_count": mistake_count,
        "repeated_mistake_count": repeated_mistake_count,
        "negative_transfer": bool(negative_transfer),
        "broke_existing_tests": broke_existing,
    }


def group_key(
    trajectory: dict[str, Any],
    task: dict[str, Any] | None,
    fields: list[str],
) -> tuple[str, ...]:
    values: list[str] = []
    for field in fields:
        if field == "method":
            values.append(trajectory["method"])
        elif field == "task_id":
            values.append(trajectory["task_id"])
        elif field == "split":
            values.append(task.get("split", "unknown") if task else "unknown")
        elif field == "bug_family":
            values.append(task.get("bug_family", "unknown") if task else "unknown")
        elif field == "source":
            values.append(task.get("repo", {}).get("source", "unknown") if task else "unknown")
    return tuple(values)


def summarize_group(group_runs: list[dict[str, Any]]) -> dict[str, Any]:
    n_runs = len(group_runs)
    solved_runs = [run for run in group_runs if run["solved"]]
    n_solved = len(solved_runs)
    total_cycles = sum(run["cycle_records"] for run in group_runs)
    broke_applicable = [
        run for run in group_runs if run["broke_existing_tests"] is not None
    ]

    return {
        "n_runs": n_runs,
        "n_tasks": len({run["task_id"] for run in group_runs}),
        "solved": n_solved,
        "solve_rate": round_or_none(safe_divide(n_solved, n_runs)),
        "cycles_per_solved_task": round_or_none(
            safe_divide(sum(run["cycles_used"] for run in solved_runs), n_solved)
        ),
        "tokens_per_solved_task": round_or_none(
            safe_divide(sum(run["total_tokens"] for run in solved_runs), n_solved)
        ),
        "active_tokens_per_solved_task": round_or_none(
            safe_divide(sum(run["active_debugging_tokens"] for run in solved_runs), n_solved)
        ),
        "prompt_overhead_ratio": round_or_none(
            safe_divide(
                sum(run["prompt_overhead_tokens"] for run in group_runs),
                sum(run["total_tokens"] for run in group_runs),
            )
        ),
        "failed_patches_per_run": round_or_none(
            safe_divide(sum(run["failed_patch_count"] for run in group_runs), n_runs)
        ),
        "mistakes_per_cycle": round_or_none(
            safe_divide(sum(run["mistake_count"] for run in group_runs), total_cycles)
        ),
        "repeated_mistake_rate": round_or_none(
            safe_divide(sum(run["repeated_mistake_count"] for run in group_runs), total_cycles)
        ),
        "negative_transfer_rate": round_or_none(
            safe_divide(sum(1 for run in group_runs if run["negative_transfer"]), n_runs)
        ),
        "broke_existing_tests_rate": round_or_none(
            safe_divide(
                sum(1 for run in broke_applicable if run["broke_existing_tests"] is True),
                len(broke_applicable),
            )
        ),
    }


def build_summary(
    trajectories: list[tuple[Path, dict[str, Any]]],
    tasks: dict[str, dict[str, Any]],
    fields: list[str],
) -> dict[str, Any]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for _path, trajectory in trajectories:
        task = tasks.get(trajectory["task_id"])
        groups[group_key(trajectory, task, fields)].append(run_stats(trajectory))

    rows: list[dict[str, Any]] = []
    for key in sorted(groups):
        row = {field: value for field, value in zip(fields, key)}
        row.update(summarize_group(groups[key]))
        rows.append(row)
    return {"group_by": fields, "groups": rows}


def print_table(summary: dict[str, Any]) -> None:
    fields = list(summary["group_by"])
    metric_fields = [
        "n_runs",
        "n_tasks",
        "solved",
        "solve_rate",
        "cycles_per_solved_task",
        "tokens_per_solved_task",
        "negative_transfer_rate",
        "repeated_mistake_rate",
    ]
    columns = fields + metric_fields
    print("\t".join(columns))
    for row in summary["groups"]:
        print("\t".join("" if row.get(column) is None else str(row.get(column)) for column in columns))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute MVP efficiency and transfer metrics from trajectory JSON files."
    )
    parser.add_argument("trajectories", nargs="+", type=Path, help="Trajectory JSON files or directories")
    parser.add_argument("--tasks", nargs="*", type=Path, default=[], help="Optional task JSON files or directories")
    parser.add_argument(
        "--group-by",
        type=parse_group_fields,
        default=["method"],
        help="Comma-separated group fields: method,task_id,split,bug_family,source",
    )
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-csv", type=Path, default=None)
    parser.add_argument("--schema", type=Path, default=DEFAULT_TRAJECTORY_SCHEMA)
    parser.add_argument("--task-schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    args = parser.parse_args()

    trajectories = load_validated_files(args.trajectories, args.schema)
    if not trajectories:
        print("No trajectory JSON files found.", file=sys.stderr)
        return 1

    tasks = load_task_index(args.tasks, args.task_schema)
    summary = build_summary(trajectories, tasks, args.group_by)

    print_table(summary)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {args.output_json}")
    if args.output_csv:
        write_csv(args.output_csv, summary["groups"])
        print(f"Wrote {args.output_csv}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
