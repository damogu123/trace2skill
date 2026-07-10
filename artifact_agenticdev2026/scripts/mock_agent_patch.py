from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PRESETS = {
    "local_empty_input_bug": {
        "target_file": "src/sample_parser/parser.py",
        "old_text": "return None",
        "new_text": "return []",
        "diagnosis": "The failing assertion indicates a missing empty-input branch.",
        "inspection_reason": "This implementation owns the failing behavior.",
        "patch_summary": "Return an empty list for whitespace-only input.",
    }
}


def choose(value: str | None, preset: dict[str, str], key: str) -> str:
    if value is not None:
        return value
    return preset[key]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mock external agent for runner smoke tests. Not for experiments."
    )
    parser.add_argument("--repo-dir", type=Path, required=True)
    parser.add_argument("--trace-path", type=Path, required=True)
    parser.add_argument("--preset", choices=sorted(PRESETS), default=None)
    parser.add_argument("--target-file", default=None)
    parser.add_argument("--old-text", default=None)
    parser.add_argument("--new-text", default=None)
    parser.add_argument("--diagnosis", default=None)
    parser.add_argument("--inspection-reason", default=None)
    parser.add_argument("--patch-summary", default=None)
    parser.add_argument("--input-tokens", type=int, default=1000)
    parser.add_argument("--output-tokens", type=int, default=200)
    args = parser.parse_args()

    preset = PRESETS.get(args.preset or "", {})
    target_file = choose(args.target_file, preset, "target_file")
    old_text = choose(args.old_text, preset, "old_text")
    new_text = choose(args.new_text, preset, "new_text")
    diagnosis = choose(args.diagnosis, preset, "diagnosis")
    inspection_reason = choose(args.inspection_reason, preset, "inspection_reason")
    patch_summary = choose(args.patch_summary, preset, "patch_summary")

    target = args.repo_dir / target_file
    source = target.read_text(encoding="utf-8")
    if old_text not in source:
        raise ValueError(f"Old text not found in {target}")
    target.write_text(source.replace(old_text, new_text, 1), encoding="utf-8", newline="\n")

    trace = {
        "llm_turns": 4,
        "tool_calls": 6,
        "input_tokens": args.input_tokens,
        "output_tokens": args.output_tokens,
        "cycles": [
            {
                "cycle_id": 1,
                "diagnosis": diagnosis,
                "file_inspections": [
                    {
                        "path": target_file,
                        "reason": inspection_reason,
                    }
                ],
                "modified_files": [target_file],
                "patch_summary": patch_summary,
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
    args.trace_path.parent.mkdir(parents=True, exist_ok=True)
    args.trace_path.write_text(json.dumps(trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"mock patched {target}")
    print(f"mock trace {args.trace_path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
