from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "run_manifest.schema.json"
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


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def parse_methods(value: str | None) -> set[str] | None:
    if not value:
        return None
    methods = {item.strip() for item in value.split(",") if item.strip()}
    unknown = sorted(methods - set(METHODS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown methods: {', '.join(unknown)}")
    return methods


def load_manifest(path: Path, schema_path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    validate_instance(manifest, load_json(schema_path))
    return manifest


def selected_runs(
    manifest: dict[str, Any],
    methods: set[str] | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    runs = [
        run
        for run in manifest["runs"]
        if methods is None or run["method"] in methods
    ]
    if limit is not None:
        runs = runs[:limit]
    return runs


def prepare_command(run: dict[str, Any], force: bool, verify_reference: bool, dry_run: bool) -> list[str]:
    workspace_path = resolve_project_path(run["workspace_path"])
    workspace_dir = workspace_path.parent.parent
    command = [
        sys.executable,
        str(ROOT / "scripts" / "prepare_task.py"),
        str(resolve_project_path(run["task_path"])),
        "--workspace",
        str(workspace_dir),
        "--checkout-id",
        run["run_id"],
    ]
    if force:
        command.append("--force")
    if verify_reference:
        command.append("--verify-reference")
    if dry_run:
        command.append("--dry-run")
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare clean run workspaces for each selected run in a run manifest."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--methods", type=parse_methods, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verify-reference", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest, args.schema)
    runs = selected_runs(manifest, args.methods, args.limit)
    if not runs:
        print("No runs selected.", file=sys.stderr)
        return 1

    failures = 0
    for index, run in enumerate(runs, start=1):
        print(f"[{index}/{len(runs)}] prepare {run['run_id']} ({run['method']})")
        command = prepare_command(run, args.force, args.verify_reference, args.dry_run)
        process = subprocess.run(command, cwd=ROOT)
        if process.returncode != 0:
            failures += 1
            print(f"FAILED {run['run_id']} returncode={process.returncode}", file=sys.stderr)
            if not args.dry_run:
                break

    if failures:
        return 1
    print(f"Prepared {len(runs)} run workspace(s)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
