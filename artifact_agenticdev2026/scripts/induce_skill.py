from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "trajectory.schema.json"
DEFAULT_TEMPLATE = ROOT / "prompts" / "induction_prompt_v2.md"


PATH_RE = re.compile(r"(?:(?:[A-Za-z]:)?[A-Za-z0-9_.-]+[\\/])+[A-Za-z0-9_.-]+")
PY_FILE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\.py\b")
TEST_NAME_RE = re.compile(r"\btest_[A-Za-z0-9_]+\b")
CODE_SPAN_RE = re.compile(r"`[^`]+`")
DOTTED_IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\b")
SNAKE_IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9]*_[A-Za-z0-9_]*\b")
ISSUE_REF_RE = re.compile(r"\b(issue|bug|ticket)\s+#?\d+\b", re.IGNORECASE)
KNOWN_PROJECT_TERM_RE = re.compile(r"\bpoyo\b", re.IGNORECASE)


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


def redact_text(text: Any) -> Any:
    if text is None or not isinstance(text, str):
        return text
    text = CODE_SPAN_RE.sub("`<code>`", text)
    text = PATH_RE.sub("<path>", text)
    text = PY_FILE_RE.sub("<file>", text)
    text = TEST_NAME_RE.sub("<test>", text)
    text = DOTTED_IDENTIFIER_RE.sub("<identifier>", text)
    text = SNAKE_IDENTIFIER_RE.sub("<identifier>", text)
    text = ISSUE_REF_RE.sub(lambda match: f"{match.group(1).lower()} <number>", text)
    text = KNOWN_PROJECT_TERM_RE.sub("<project>", text)
    return text


def summarize_trajectory(data: dict[str, Any], index: int) -> dict[str, Any]:
    outcome = data.get("final_outcome", {})
    cycles = []
    for cycle in data.get("cycles", []):
        cycles.append(
            {
                "cycle_id": cycle.get("cycle_id"),
                "diagnosis": redact_text(cycle.get("diagnosis")),
                "file_inspection_reasons": [
                    redact_text(item.get("reason"))
                    for item in cycle.get("file_inspections", [])
                    if isinstance(item, dict)
                ],
                "modified_file_count": len(cycle.get("patch_attempt", {}).get("modified_files", [])),
                "patch_summary": redact_text(cycle.get("patch_attempt", {}).get("patch_summary")),
                "test_passed": cycle.get("test_rerun", {}).get("passed"),
                "mistakes": [
                    {
                        "type": mistake.get("type"),
                        "description": redact_text(mistake.get("description")),
                    }
                    for mistake in cycle.get("mistakes", [])
                    if isinstance(mistake, dict)
                ],
            }
        )

    return {
        "trajectory_index": index,
        "method": data.get("method"),
        "solved": outcome.get("solved"),
        "cycles_used": outcome.get("cycles_used"),
        "failed_patch_count": outcome.get("failed_patch_count"),
        "negative_transfer": data.get("negative_transfer", {}).get("detected"),
        "cycles": cycles,
    }


def load_and_validate(files: list[Path], schema_path: Path) -> list[tuple[Path, dict[str, Any]]]:
    schema = load_json(schema_path)
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for file_path in files:
        data = load_json(file_path)
        validate_instance(data, schema)
        loaded.append((file_path, data))
    return loaded


def select_trajectories(
    loaded: list[tuple[Path, dict[str, Any]]],
    k: int | None,
    seed: int,
) -> list[tuple[Path, dict[str, Any]]]:
    if k is None or k >= len(loaded):
        return loaded
    rng = random.Random(seed)
    indices = sorted(rng.sample(range(len(loaded)), k))
    return [loaded[index] for index in indices]


def render_prompt(template: str, selected: list[tuple[Path, dict[str, Any]]], seed: int) -> str:
    summaries = [
        summarize_trajectory(data, index=index)
        for index, (_path, data) in enumerate(selected, start=1)
    ]
    metadata = {
        "trajectory_count": len(selected),
        "selection_seed": seed,
        "source_files": [
            f"trajectory_{index}.json"
            for index, (_path, _data) in enumerate(selected, start=1)
        ],
        "redaction": {
            "paths": "<path>",
            "python_files": "<file>",
            "test_names": "<test>",
            "inline_code": "`<code>`",
            "identifiers": "<identifier>",
            "issue_references": "issue <number>",
            "project_terms": "<project>",
        },
    }
    return (
        template.rstrip()
        + "\n\n---\n\n"
        + "# Induction Input Package\n\n"
        + "The following trajectories are redacted summaries. Do not infer or recreate hidden file, function, test, repository, or patch details.\n\n"
        + "## Package Metadata\n\n"
        + "```json\n"
        + json.dumps(metadata, indent=2, ensure_ascii=False)
        + "\n```\n\n"
        + "## Redacted Trajectory Summaries\n\n"
        + "```json\n"
        + json.dumps(summaries, indent=2, ensure_ascii=False)
        + "\n```\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a redacted SKILL.md induction prompt from trajectory JSON files."
    )
    parser.add_argument("trajectories", nargs="+", type=Path, help="Trajectory JSON files or directories")
    parser.add_argument("--output", type=Path, required=True, help="Output Markdown prompt path")
    parser.add_argument("--k", type=int, default=None, help="Number of trajectories to sample")
    parser.add_argument("--seed", type=int, default=1, help="Deterministic sampling seed")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Trajectory schema path")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Induction prompt template path")
    args = parser.parse_args()

    files = iter_json_files(args.trajectories)
    if not files:
        print("No trajectory JSON files found.", file=sys.stderr)
        return 1

    loaded = load_and_validate(files, args.schema)
    selected = select_trajectories(loaded, args.k, args.seed)
    template = args.template.read_text(encoding="utf-8")
    prompt = render_prompt(template, selected, args.seed)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(prompt, encoding="utf-8", newline="\n")
    print(f"Wrote {args.output}")
    print(f"selected={len(selected)} total={len(loaded)} seed={args.seed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
