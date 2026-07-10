from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance
from run_codex_agent import parse_total_tokens


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_SCHEMA = ROOT / "schemas" / "run_manifest.schema.json"
DEFAULT_TRACE_SCHEMA = ROOT / "schemas" / "agent_trace.schema.json"
DEFAULT_TRAJECTORY_SCHEMA = ROOT / "schemas" / "trajectory.schema.json"


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def parse_csv_set(value: str | None) -> set[str] | None:
    if value is None:
        return None
    return {item.strip() for item in value.split(",") if item.strip()}


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


def update_trace(path: Path, total_tokens: int, schema: dict[str, Any], dry_run: bool) -> None:
    data = load_json(path)
    data["input_tokens"] = total_tokens
    data["output_tokens"] = 0
    validate_instance(data, schema)
    if not dry_run:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_trajectory(path: Path, total_tokens: int, schema: dict[str, Any], dry_run: bool) -> None:
    data = load_json(path)
    outcome = data["final_outcome"]
    prompt_overhead_tokens = int(outcome.get("prompt_overhead_tokens", 0))
    outcome["input_tokens"] = total_tokens
    outcome["output_tokens"] = 0
    outcome["active_debugging_tokens"] = max(total_tokens - prompt_overhead_tokens, 0)
    validate_instance(data, schema)
    if not dry_run:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def repair_run(run: dict[str, Any], trace_schema: dict[str, Any], trajectory_schema: dict[str, Any], dry_run: bool) -> bool:
    artifacts_dir = resolve_project_path(run["artifacts_dir"])
    log_path = artifacts_dir / "agent.log"
    trace_path = artifacts_dir / "agent_trace.json"
    trajectory_path = resolve_project_path(run["trajectory_path"])

    if not log_path.exists():
        print(f"WARN {run['run_id']}: missing log {log_path}")
        return False
    output = log_path.read_text(encoding="utf-8", errors="replace")
    total_tokens = parse_total_tokens(output)
    if total_tokens is None:
        print(f"WARN {run['run_id']}: could not parse total tokens")
        return False
    if not trace_path.exists():
        print(f"WARN {run['run_id']}: missing trace {trace_path}")
        return False
    if not trajectory_path.exists():
        print(f"WARN {run['run_id']}: missing trajectory {trajectory_path}")
        return False

    update_trace(trace_path, total_tokens, trace_schema, dry_run)
    update_trajectory(trajectory_path, total_tokens, trajectory_schema, dry_run)
    action = "WOULD-UPDATE" if dry_run else "UPDATED"
    print(f"{action} {run['run_id']}: total_tokens={total_tokens}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Backfill Codex CLI total token counts into agent traces and trajectories."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--methods", default=None, help="Comma-separated method filter")
    parser.add_argument("--run-ids", default=None, help="Comma-separated run_id filter")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest-schema", type=Path, default=DEFAULT_MANIFEST_SCHEMA)
    parser.add_argument("--trace-schema", type=Path, default=DEFAULT_TRACE_SCHEMA)
    parser.add_argument("--trajectory-schema", type=Path, default=DEFAULT_TRAJECTORY_SCHEMA)
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    validate_instance(manifest, load_json(args.manifest_schema))
    trace_schema = load_json(args.trace_schema)
    trajectory_schema = load_json(args.trajectory_schema)
    selected = select_runs(
        manifest["runs"],
        parse_csv_set(args.methods),
        parse_csv_set(args.run_ids),
        args.limit,
    )
    if not selected:
        print("No runs selected.", file=sys.stderr)
        return 1

    repaired = 0
    for run in selected:
        if repair_run(run, trace_schema, trajectory_schema, args.dry_run):
            repaired += 1
    print(f"Repaired {repaired}/{len(selected)} selected runs.")
    return 0 if repaired else 1


if __name__ == "__main__":
    sys.exit(main())
