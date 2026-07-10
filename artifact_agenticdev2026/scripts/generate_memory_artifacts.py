from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance
from make_format_shuffled_skill import build_shuffled_markdown, extract_units, word_count


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAJECTORY_SCHEMA = ROOT / "schemas" / "trajectory.schema.json"
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
PATH_RE = re.compile(r"(?:(?:[A-Za-z]:)?[A-Za-z0-9_.-]+[\\/])+[A-Za-z0-9_.-]+")
PY_FILE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\.py\b")
TEST_NAME_RE = re.compile(r"\btest_[A-Za-z0-9_]+\b")
CODE_SPAN_RE = re.compile(r"`[^`]+`")
SNAKE_IDENTIFIER_RE = re.compile(r"\b(?!test_)[A-Za-z_][A-Za-z0-9]*_[A-Za-z0-9_]*\b")


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


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    if not slug:
        raise ValueError(f"Cannot create slug from {value!r}")
    return slug


def redact_text(value: Any) -> Any:
    if value is None or not isinstance(value, str):
        return value
    value = CODE_SPAN_RE.sub("`<code>`", value)
    value = PATH_RE.sub("<path>", value)
    value = PY_FILE_RE.sub("<file>", value)
    value = TEST_NAME_RE.sub("<test>", value)
    value = SNAKE_IDENTIFIER_RE.sub("<identifier>", value)
    return value


def load_validated(paths: list[Path], schema_path: Path) -> list[tuple[Path, dict[str, Any]]]:
    schema = load_json(schema_path)
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for path in iter_json_files(paths):
        data = load_json(path)
        validate_instance(data, schema)
        loaded.append((path, data))
    return loaded


def load_task_index(paths: list[Path], schema_path: Path) -> dict[str, dict[str, Any]]:
    return {data["task_id"]: data for _path, data in load_validated(paths, schema_path)}


def select_k(items: list[tuple[Path, dict[str, Any]]], k: int | None, seed: int) -> list[tuple[Path, dict[str, Any]]]:
    if k is None or k >= len(items):
        return items
    rng = random.Random(seed)
    selected = sorted(rng.sample(range(len(items)), k))
    return [items[index] for index in selected]


def family_for_trajectory(trajectory: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> str:
    task = tasks.get(trajectory["task_id"])
    if task is None:
        raise KeyError(f"Task metadata missing for trajectory task_id={trajectory['task_id']!r}")
    return task["bug_family"]


def summarize_cycle(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "cycle_id": cycle["cycle_id"],
        "diagnosis": redact_text(cycle["diagnosis"]),
        "inspection_reasons": [
            redact_text(item["reason"])
            for item in cycle.get("file_inspections", [])
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
        ],
    }


def summarize_trajectory(path: Path, trajectory: dict[str, Any], index: int) -> dict[str, Any]:
    outcome = trajectory["final_outcome"]
    return {
        "trajectory_index": index,
        "source_file": redact_text(path.as_posix()),
        "method": trajectory["method"],
        "solved": outcome["solved"],
        "cycles_used": outcome["cycles_used"],
        "failed_patch_count": outcome.get("failed_patch_count", 0),
        "negative_transfer": trajectory.get("negative_transfer", {}).get("detected", False),
        "cycles": [summarize_cycle(cycle) for cycle in trajectory["cycles"]],
    }


def collect_text_units(summaries: list[dict[str, Any]]) -> dict[str, list[str]]:
    diagnoses: list[str] = []
    inspections: list[str] = []
    patch_summaries: list[str] = []
    mistakes: list[str] = []

    for summary in summaries:
        for cycle in summary["cycles"]:
            if cycle["diagnosis"]:
                diagnoses.append(cycle["diagnosis"])
            inspections.extend(reason for reason in cycle["inspection_reasons"] if reason)
            if cycle["patch_summary"]:
                patch_summaries.append(cycle["patch_summary"])
            for mistake in cycle["mistakes"]:
                description = mistake.get("description") or mistake.get("type")
                if description:
                    mistakes.append(str(description))

    return {
        "diagnoses": unique_preserve_order(diagnoses),
        "inspections": unique_preserve_order(inspections),
        "patch_summaries": unique_preserve_order(patch_summaries),
        "mistakes": unique_preserve_order(mistakes),
    }


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            output.append(normalized)
    return output


def bullets(values: list[str], fallback: str) -> str:
    items = values or [fallback]
    return "\n".join(f"- {item}" for item in items)


def render_auto_skill(family: str, summaries: list[dict[str, Any]], seed: int) -> str:
    units = collect_text_units(summaries)
    trigger_values = [
        "A failing test points to a narrow behavioral edge case rather than an installation or infrastructure error.",
        "The assertion or traceback implies that one input shape is not handled consistently with nearby expected behavior.",
    ]
    trigger_values.extend(units["diagnoses"][:3])

    procedure_values = [
        "Start from the failing assertion and restate the smallest expected behavior before opening implementation files.",
        "Inspect the implementation path most directly connected to the observed behavior, then compare it with nearby tests or call sites.",
        "Add the smallest general branch or normalization step that handles the missing case without hard-coding the visible assertion.",
        "Rerun the narrow failing test after each patch; when it passes, run the broader test command if available.",
    ]
    procedure_values.extend(units["inspections"][:2])
    procedure_values.extend(units["patch_summaries"][:2])

    failure_values = [
        "Do not overfit to a single visible literal from the failing assertion.",
        "Do not keep retrying the same patch shape after a failed test rerun; return to the original failure log.",
        "Do not edit unrelated modules unless the traceback or direct call path justifies the change.",
    ]
    failure_values.extend(units["mistakes"][:3])

    return f"""# Auto-SKILL.md

## Trigger Conditions

{bullets(trigger_values, "Use this skill when a test failure indicates a localized behavioral mismatch.")}

## Debugging Procedure

{bullets(procedure_values, "Diagnose the failure, make one minimal patch, and rerun the narrow test.")}

## Failure Modes

{bullets(failure_values, "Avoid broad unrelated edits and repeated unvalidated patch attempts.")}
"""


def render_reflexion(family: str, summaries: list[dict[str, Any]], seed: int) -> str:
    units = collect_text_units(summaries)
    reflections = [
        "I should begin with the failing test output and identify the smallest behavior it specifies.",
        "I should inspect the code path that directly owns the failed behavior before changing broader modules.",
        "I should prefer a minimal general fix and rerun the narrow failing test after each edit.",
    ]
    reflections.extend(f"I observed: {item}" for item in units["diagnoses"][:3])
    reflections.extend(f"I should remember this patch pattern: {item}" for item in units["patch_summaries"][:3])
    reflections.extend(f"I should avoid: {item}" for item in units["mistakes"][:3])

    return f"""# Reflexion Memory

## Reflections

{bullets(reflections, "I should debug from the failure log and avoid unnecessary edits.")}
"""


def extend_to_word_count(text: str, target_words: int) -> str:
    if target_words <= 0:
        return text
    current = word_count(text)
    if current >= target_words * 0.9:
        return text

    fillers = [
        "I should keep checking whether the current edit directly follows from the failure evidence.",
        "I should avoid adding unrelated abstractions when a small behavioral fix is enough.",
        "I should stop and reread the failure log when repeated attempts do not change the result.",
        "I should separate diagnosis, edit, and test rerun so the run log remains auditable.",
    ]
    lines = [text.rstrip(), "", "## Additional Length-Matching Reflections", ""]
    index = 0
    while word_count("\n".join(lines)) < target_words * 0.95:
        lines.append(f"- {fillers[index % len(fillers)]}")
        index += 1
    return "\n".join(lines) + "\n"


def render_raw_retrieval(family: str, summaries: list[dict[str, Any]], seed: int) -> str:
    metadata = {
        "bug_family": family,
        "trajectory_count": len(summaries),
        "selection_seed": seed,
        "redaction": {
            "paths": "<path>",
            "python_files": "<file>",
            "test_names": "<test>",
            "inline_code": "`<code>`",
        },
    }
    return (
        "# Raw Trajectory Retrieval\n\n"
        "Use these redacted prior trajectory summaries as retrieved episodic memory. Do not infer hidden file, function, test, repository, or patch details.\n\n"
        "## Retrieval Metadata\n\n"
        "```json\n"
        + json.dumps(metadata, indent=2, ensure_ascii=False)
        + "\n```\n\n"
        "## Retrieved Trajectories\n\n"
        "```json\n"
        + json.dumps(summaries, indent=2, ensure_ascii=False)
        + "\n```\n"
    )


def render_oracle_template(family: str, summaries: list[dict[str, Any]], seed: int) -> str:
    return f"""# Oracle SKILL.md Template

This is a human-authoring template for bug family `{family}` using the same {len(summaries)} redacted trajectory summary/summaries selected with seed {seed}.

Do not use this file as an oracle baseline until a human annotator has replaced every TODO and confirmed that no task-specific file names, function names, test names, literal patches, or answer leakage remain.

## Trigger Conditions

- TODO: Write abstract conditions under which this skill should be used.

## Debugging Procedure

- TODO: Write ordered procedural steps inferred from the trajectories.

## Failure Modes

- TODO: Write common mistakes and negative-transfer risks.
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {path}")


def generate_for_family(
    family: str,
    selected: list[tuple[Path, dict[str, Any]]],
    output_root: Path,
    seed: int,
    include_oracle_template: bool,
) -> None:
    family_dir = output_root / slugify(family)
    summaries = [
        summarize_trajectory(path, trajectory, index)
        for index, (path, trajectory) in enumerate(selected, start=1)
    ]

    auto_skill = render_auto_skill(family, summaries, seed)
    reflexion = render_reflexion(family, summaries, seed)
    length_matched = extend_to_word_count(reflexion, word_count(auto_skill))
    raw_retrieval = render_raw_retrieval(family, summaries, seed)
    shuffled_units = extract_units(auto_skill)
    shuffled = build_shuffled_markdown(shuffled_units, seed)

    write(family_dir / "auto_skill.md", auto_skill)
    write(family_dir / "reflexion.md", reflexion)
    write(family_dir / "length_matched_reflexion.md", length_matched)
    write(family_dir / "raw_trajectory_retrieval.md", raw_retrieval)
    write(family_dir / "format_shuffled_skill.md", shuffled)
    if include_oracle_template:
        write(family_dir / "oracle_skill_template.md", render_oracle_template(family, summaries, seed))

    print(
        "word_counts "
        f"auto_skill={word_count(auto_skill)} "
        f"reflexion={word_count(reflexion)} "
        f"length_matched_reflexion={word_count(length_matched)} "
        f"format_shuffled_skill={word_count(shuffled)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate pilot memory artifacts for baseline conditions from training trajectories."
    )
    parser.add_argument("trajectories", nargs="+", type=Path, help="Trajectory JSON files or directories")
    parser.add_argument("--tasks", nargs="+", type=Path, required=True, help="Task JSON files or directories")
    parser.add_argument("--output-root", type=Path, default=ROOT / "memory")
    parser.add_argument("--k", type=int, default=None, help="Trajectories per bug family")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--include-oracle-template", action="store_true")
    parser.add_argument("--trajectory-schema", type=Path, default=DEFAULT_TRAJECTORY_SCHEMA)
    parser.add_argument("--task-schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    args = parser.parse_args()

    tasks = load_task_index(args.tasks, args.task_schema)
    trajectories = load_validated(args.trajectories, args.trajectory_schema)
    if not trajectories:
        print("No trajectory JSON files found.", file=sys.stderr)
        return 1

    by_family: dict[str, list[tuple[Path, dict[str, Any]]]] = defaultdict(list)
    for path, trajectory in trajectories:
        by_family[family_for_trajectory(trajectory, tasks)].append((path, trajectory))

    for family in sorted(by_family):
        selected = select_k(by_family[family], args.k, args.seed)
        generate_for_family(family, selected, args.output_root, args.seed, args.include_oracle_template)

    print(f"families={len(by_family)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
