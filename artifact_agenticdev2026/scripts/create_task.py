from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "task.schema.json"


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def build_task(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "task_id": args.task_id,
        "bug_family": args.bug_family,
        "split": args.split,
        "repo": {
            "name": args.repo_name,
            "source": args.source,
            "url": args.repo_url,
            "commit": args.commit,
            "language": args.language,
        },
        "environment": {
            "python_version": args.python_version,
            "install_command": args.install_command,
            "test_command": args.test_command,
            "full_test_command": args.full_test_command,
            "timeout_seconds": args.timeout_seconds,
        },
        "failure": {
            "failing_tests": parse_csv(args.failing_tests),
            "error_type": args.error_type,
            "error_message": args.error_message,
            "failure_log_path": args.failure_log_path,
        },
        "ground_truth": {
            "patch_path": args.patch_path,
            "modified_files": parse_csv(args.modified_files),
            "bug_summary": args.bug_summary,
        },
        "labels": {
            "surface_pattern": args.surface_pattern,
            "root_cause": args.root_cause,
            "requires_api_knowledge": args.requires_api_knowledge,
            "adversarial_reason": args.adversarial_reason,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a task JSON file from CLI fields.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--bug-family", default="test_failure_triage")
    parser.add_argument("--split", choices=["train", "heldout", "adversarial"], required=True)
    parser.add_argument("--repo-name", required=True)
    parser.add_argument(
        "--source",
        choices=["bugsinpy", "pybughive", "swebench_lite", "swegym", "defects4j", "synthetic", "local"],
        required=True,
    )
    parser.add_argument("--repo-url", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--language", default="python")
    parser.add_argument("--python-version", default=None)
    parser.add_argument("--install-command", required=True)
    parser.add_argument("--test-command", required=True)
    parser.add_argument("--full-test-command", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--failing-tests", required=True, help="Comma-separated failing test ids")
    parser.add_argument("--error-type", required=True)
    parser.add_argument("--error-message", default=None)
    parser.add_argument("--failure-log-path", default="logs/initial_failure.txt")
    parser.add_argument("--patch-path", default=None)
    parser.add_argument("--modified-files", default="")
    parser.add_argument("--bug-summary", default=None)
    parser.add_argument("--surface-pattern", required=True)
    parser.add_argument("--root-cause", required=True)
    parser.add_argument("--requires-api-knowledge", action="store_true")
    parser.add_argument("--adversarial-reason", default=None)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    task = build_task(args)
    validate_instance(task, load_json(args.schema))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(task, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
