from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import import_pybughive_tasks as importer
from _schema_validate import load_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "data" / "external" / "pybughive" / "dataset" / "pybughive_current.json"
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
DEFAULT_RESULTS_CSV = ROOT / "results" / "pybughive_hard_subset_candidates.csv"
DEFAULT_RESULTS_MD = ROOT / "results" / "pybughive_hard_subset_plan.md"
DEFAULT_OUTPUT_ROOT = ROOT / "tasks" / "pybughive_hard"
DEFAULT_PATCH_ROOT = ROOT / "patches" / "pybughive_hard"
DEFAULT_METADATA_ROOT = ROOT / "data" / "pybughive_hard"
DEFAULT_EXISTING_TASK_ROOTS = [
    ROOT / "tasks" / "pybughive" / "train",
    ROOT / "tasks" / "pybughive" / "heldout",
    ROOT / "tasks" / "pybughive_hard" / "heldout",
]
DEFAULT_LIGHT_PROJECTS = ["black", "cookiecutter", "discord.py", "scrapy", "poetry"]

HARD_TITLE_TERMS = {
    "internal error": 16,
    "traceback": 14,
    "crash": 14,
    "exception": 12,
    "regression": 12,
    "incorrect": 10,
    "wrong": 10,
    "invalid": 9,
    "unstable": 9,
    "nested": 8,
    "unicode": 8,
    "import": 8,
    "comment": 7,
    "parse": 7,
    "line length": 7,
    "second pass": 7,
}


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def discover_existing_task_ids(paths: list[Path]) -> set[str]:
    task_ids: set[str] = set()
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*.json"))
        for path in files:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(data, dict) and isinstance(data.get("task_id"), str):
                task_ids.add(data["task_id"])
            else:
                task_ids.add(path.stem)
    return task_ids


def has_warning(candidate: dict[str, Any], warning: str) -> bool:
    return warning in candidate.get("warnings", [])


def hard_score(candidate: dict[str, Any]) -> int:
    title = f"{candidate['title']} {candidate.get('labels') or ''}".lower()
    source_count = len(candidate["source_files"])
    test_count = len(candidate["test_files"])
    score = 0

    score += source_count * 12
    score += test_count * 6
    score += min(candidate["changed_lines"], 100)
    score += min(candidate["test_changed_lines"], 80) // 2

    if candidate.get("full_test_steps"):
        score += 20
    if candidate.get("python_version"):
        score += 8
    if importer.classify_root_cause(candidate["raw_issue"], candidate["source_files"]) == "cross_file_behavior_regression":
        score += 18
    if importer.requires_api_knowledge(candidate["project"], candidate["raw_issue"]):
        score += 10

    for term, weight in HARD_TITLE_TERMS.items():
        if term in title:
            score += weight

    if source_count == 1 and candidate["changed_lines"] <= 10:
        score -= 15
    if test_count == 1 and candidate["test_changed_lines"] <= 5:
        score -= 8
    if has_warning(candidate, "test_command_may_need_manual_review"):
        score -= 25
    if has_warning(candidate, "text_based_issue"):
        score -= 10
    if has_warning(candidate, "heavy_install_steps"):
        score -= 30
    if has_warning(candidate, "heavy_project"):
        score -= 35

    return score


def hard_reasons(candidate: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    source_count = len(candidate["source_files"])
    test_count = len(candidate["test_files"])
    title = f"{candidate['title']} {candidate.get('labels') or ''}".lower()

    if source_count > 1:
        reasons.append(f"{source_count} source files")
    if candidate["changed_lines"] >= 25:
        reasons.append(f"{candidate['changed_lines']} source changed lines")
    if test_count > 1:
        reasons.append(f"{test_count} test files")
    if candidate["test_changed_lines"] >= 25:
        reasons.append(f"{candidate['test_changed_lines']} test changed lines")
    if candidate.get("full_test_steps"):
        reasons.append("has broader full-test command")
    if importer.classify_root_cause(candidate["raw_issue"], candidate["source_files"]) == "cross_file_behavior_regression":
        reasons.append("cross-file reference patch")
    for term in HARD_TITLE_TERMS:
        if term in title:
            reasons.append(f"title mentions {term!r}")
            break
    if importer.requires_api_knowledge(candidate["project"], candidate["raw_issue"]):
        reasons.append("requires API/domain knowledge")

    return reasons or ["metadata-screened localized behavior regression"]


def tier_for(candidate: dict[str, Any], light_projects: set[str], include_heavy: bool) -> str | None:
    if candidate["exclusions"]:
        return None
    is_heavy = has_warning(candidate, "heavy_install_steps") or has_warning(candidate, "heavy_project")
    if candidate["project"] in light_projects and not is_heavy:
        return "pilot_light"
    if include_heavy and is_heavy:
        return "full_study_heavy"
    return None


def select_ranked_candidates(
    candidates: list[dict[str, Any]],
    *,
    existing_task_ids: set[str],
    light_projects: set[str],
    include_heavy: bool,
    per_project: int,
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    counts: dict[tuple[str, str], int] = defaultdict(int)

    scored = []
    for candidate in candidates:
        task_id = importer.task_id_for(candidate)
        if task_id in existing_task_ids:
            continue
        tier = tier_for(candidate, light_projects, include_heavy)
        if tier is None:
            continue
        scored.append((hard_score(candidate), task_id, tier, candidate))

    for score, task_id, tier, candidate in sorted(scored, key=lambda item: (-item[0], item[2], item[1])):
        key = (tier, candidate["project"])
        if counts[key] >= per_project:
            continue
        counts[key] += 1
        item = dict(candidate)
        item["task_id"] = task_id
        item["hard_score"] = score
        item["selection_tier"] = tier
        item["hard_reasons"] = hard_reasons(candidate)
        ranked.append(item)

    return ranked


def write_csv(path: Path, candidates: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "rank",
        "selection_tier",
        "task_id",
        "project",
        "issue_id",
        "hard_score",
        "title",
        "source_file_count",
        "changed_lines",
        "test_file_count",
        "test_changed_lines",
        "python_version",
        "has_full_test",
        "warnings",
        "hard_reasons",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for rank, candidate in enumerate(candidates, start=1):
            writer.writerow(
                {
                    "rank": rank,
                    "selection_tier": candidate["selection_tier"],
                    "task_id": candidate["task_id"],
                    "project": candidate["project"],
                    "issue_id": candidate["issue_id"],
                    "hard_score": candidate["hard_score"],
                    "title": candidate["title"],
                    "source_file_count": len(candidate["source_files"]),
                    "changed_lines": candidate["changed_lines"],
                    "test_file_count": len(candidate["test_files"]),
                    "test_changed_lines": candidate["test_changed_lines"],
                    "python_version": candidate["python_version"] or "",
                    "has_full_test": bool(candidate.get("full_test_steps")),
                    "warnings": ";".join(candidate["warnings"]),
                    "hard_reasons": "; ".join(candidate["hard_reasons"]),
                }
            )


def write_markdown(path: Path, candidates: list[dict[str, Any]], selected_for_tasks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(candidate["selection_tier"] for candidate in candidates)
    lines = [
        "# PyBugHive Hard-Subset Plan",
        "",
        "## Goal",
        "",
        "Select a harder held-out subset that can separate Auto-SKILL from `generic_checklist` and `no_memory`.",
        "The current MVP is useful but too easy because both generic baselines solve 7/7 held-out tasks.",
        "",
        "## Selection Heuristic",
        "",
        "Candidates are ranked higher when metadata suggests harder debugging:",
        "",
        "- multiple source files or larger reference patches;",
        "- multiple or large test patches;",
        "- broader full-test command is available;",
        "- title suggests crash, internal error, parse failure, unstable formatting, import behavior, or nested edge cases;",
        "- cross-file behavior regression or API/domain knowledge may be involved.",
        "",
        "Candidates are penalized for heavy projects, heavy install steps, text-only issues, very tiny patches, and test commands requiring manual review.",
        "",
        "## Candidate Counts",
        "",
        f"- Ranked candidates: {len(candidates)}",
        f"- Pilot-light candidates: {counts.get('pilot_light', 0)}",
        f"- Full-study-heavy candidates: {counts.get('full_study_heavy', 0)}",
        f"- Task JSONs written in this run: {len(selected_for_tasks)}",
        "",
        "## Recommended Pilot-Light Candidates",
        "",
        "| Rank | Task ID | Project | Score | Source files | Changed lines | Test files | Test changed lines | Why hard |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    pilot = [candidate for candidate in candidates if candidate["selection_tier"] == "pilot_light"][:12]
    for rank, candidate in enumerate(pilot, start=1):
        lines.append(
            "| {rank} | `{task_id}` | {project} | {score} | {source_count} | {changed_lines} | {test_count} | {test_changed_lines} | {reasons} |".format(
                rank=rank,
                task_id=candidate["task_id"],
                project=candidate["project"],
                score=candidate["hard_score"],
                source_count=len(candidate["source_files"]),
                changed_lines=candidate["changed_lines"],
                test_count=len(candidate["test_files"]),
                test_changed_lines=candidate["test_changed_lines"],
                reasons="; ".join(candidate["hard_reasons"][:3]),
            )
        )
    lines.extend(
        [
            "",
            "## Full-Study Heavy Candidates",
            "",
            "These may be useful later, but should not be first because environment setup is likely expensive.",
            "",
            "| Rank | Task ID | Project | Score | Warnings | Title |",
            "| ---: | --- | --- | ---: | --- | --- |",
        ]
    )
    heavy = [candidate for candidate in candidates if candidate["selection_tier"] == "full_study_heavy"][:12]
    for rank, candidate in enumerate(heavy, start=1):
        lines.append(
            "| {rank} | `{task_id}` | {project} | {score} | {warnings} | {title} |".format(
                rank=rank,
                task_id=candidate["task_id"],
                project=candidate["project"],
                score=candidate["hard_score"],
                warnings=", ".join(candidate["warnings"]) or "none",
                title=candidate["title"].replace("|", "\\|"),
            )
        )
    lines.extend(
        [
            "",
            "## Execution Protocol",
            "",
            "1. Verify the written pilot-light task JSONs with `scripts/verify_pybughive_tasks.py` before running agent baselines.",
            "2. Keep only tasks where initial failure reproduces and the reference patch passes.",
            "3. First run only `no_memory`, `generic_checklist`, `auto_skill`, `reflexion`, and `length_matched_reflexion` on the verified hard subset.",
            "4. Add `format_shuffled_skill` and `raw_trajectory_retrieval` after the first hard-subset smoke run is stable.",
            "",
            "## Suggested First Commands",
            "",
            "```powershell",
            "python scripts\\verify_pybughive_tasks.py tasks\\pybughive_hard\\heldout --workspace workspaces\\verify_pybughive_hard --force --timeout 900 --output-json results\\pybughive_hard_verify.json --output-csv results\\pybughive_hard_verify.csv --output-md results\\pybughive_hard_verify.md",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_task_jsons(
    candidates: list[dict[str, Any]],
    *,
    output_root: Path,
    patch_root: Path,
    metadata_root: Path,
    schema_path: Path,
    count: int,
    dry_run: bool,
) -> list[dict[str, Any]]:
    schema = load_json(schema_path)
    selected = [candidate for candidate in candidates if candidate["selection_tier"] == "pilot_light"][:count]
    for candidate in selected:
        candidate["split"] = "heldout"
        importer.write_candidate_artifacts(
            candidate,
            "heldout",
            output_root,
            patch_root,
            metadata_root,
            schema,
            dry_run,
        )
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank PyBugHive candidates for a harder held-out subset.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_RESULTS_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_RESULTS_MD)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--patch-root", type=Path, default=DEFAULT_PATCH_ROOT)
    parser.add_argument("--metadata-root", type=Path, default=DEFAULT_METADATA_ROOT)
    parser.add_argument("--existing-task-roots", default=",".join(str(path) for path in DEFAULT_EXISTING_TASK_ROOTS))
    parser.add_argument("--light-projects", default=",".join(DEFAULT_LIGHT_PROJECTS))
    parser.add_argument("--per-project", type=int, default=12)
    parser.add_argument("--write-task-count", type=int, default=8)
    parser.add_argument("--include-heavy", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.per_project < 1:
        parser.error("--per-project must be >= 1")
    if args.write_task_count < 0:
        parser.error("--write-task-count must be >= 0")

    existing_roots = [Path(path) for path in parse_csv(args.existing_task_roots)]
    existing_task_ids = discover_existing_task_ids(existing_roots)
    light_projects = set(parse_csv(args.light_projects))
    candidates = importer.load_candidates(args.dataset)
    ranked = select_ranked_candidates(
        candidates,
        existing_task_ids=existing_task_ids,
        light_projects=light_projects,
        include_heavy=args.include_heavy,
        per_project=args.per_project,
    )
    if not ranked:
        print("No candidates selected.", file=sys.stderr)
        return 1

    selected_for_tasks = write_task_jsons(
        ranked,
        output_root=args.output_root,
        patch_root=args.patch_root,
        metadata_root=args.metadata_root,
        schema_path=args.schema,
        count=args.write_task_count,
        dry_run=args.dry_run,
    )
    write_csv(args.output_csv, ranked)
    write_markdown(args.output_md, ranked, selected_for_tasks)

    action = "would write" if args.dry_run else "wrote"
    print(f"{action} {len(selected_for_tasks)} pilot-light task JSONs under {args.output_root / 'heldout'}")
    print(f"ranked_candidates={len(ranked)} csv={args.output_csv} report={args.output_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
