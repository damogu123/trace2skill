from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "data" / "external" / "pybughive" / "dataset" / "pybughive_current.json"
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
DEFAULT_OUTPUT_ROOT = ROOT / "tasks" / "pybughive"
DEFAULT_PATCH_ROOT = ROOT / "patches" / "pybughive"
DEFAULT_METADATA_ROOT = ROOT / "data" / "pybughive"
DEFAULT_RESULTS_ROOT = ROOT / "results"

HEAVY_INSTALL_PATTERNS = [
    "sudo ",
    "apt ",
    "apt-get",
    "conda ",
    "wget ",
    "curl ",
    "ta-lib",
    "build/build.py",
    "python3 build",
    "nox ",
    "pipx ",
]
HEAVY_PROJECTS = {"freqtrade", "jax", "numpy", "pandas", "salt", "spacy"}
DEFAULT_PROJECT_ALLOWLIST = ["black", "cookiecutter", "discord.py", "scrapy", "poetry"]


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return slug or "unknown"


def repo_url(username: str, repository: str) -> str:
    return f"https://github.com/{username}/{repository}.git"


def relative_to_task(task_path: Path, target: Path) -> str:
    return Path(os.path.relpath(target.resolve(), task_path.parent.resolve())).as_posix()


def infer_python_version(install_steps: str) -> str | None:
    match = re.search(
        r"(?:pipenv|poetry\s+env\s+use)\s+(?:--python\s+)?(?:python)?([0-9]+(?:\.[0-9]+)?)",
        install_steps,
    )
    if match:
        return match.group(1)
    return None


def split_steps(steps: str) -> list[str]:
    return [line.strip() for line in steps.splitlines() if line.strip()]


def normalize_install_steps(steps: str) -> str:
    normalized = []
    for step in split_steps(steps):
        if step == "pipenv run python setup.py install":
            normalized.append("pipenv run python -m pip install .")
        elif step.startswith("pipenv install "):
            normalized.append(f"pipenv run python -m pip install {step.removeprefix('pipenv install ')}")
        else:
            normalized.append(step)
    return "\n".join(normalized)


def command_is_explicit_pytest(command: str) -> bool:
    lowered = command.lower()
    return "pytest" in lowered or "setup.py test" in lowered or "runtests.py" in lowered


def patch_supported(file_info: dict[str, Any]) -> bool:
    status = file_info.get("status")
    return status in {"added", "modified", "removed"} and bool(file_info.get("patch"))


def build_git_patch(files: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for file_info in files:
        filename = file_info["filename"]
        status = file_info.get("status")
        if not patch_supported(file_info):
            raise ValueError(f"unsupported or missing patch for {filename}")

        old_path = "/dev/null" if status == "added" else f"a/{filename}"
        new_path = "/dev/null" if status == "removed" else f"b/{filename}"
        chunks.append(f"diff --git a/{filename} b/{filename}\n")
        if status == "added":
            chunks.append("new file mode 100644\n")
        elif status == "removed":
            chunks.append("deleted file mode 100644\n")
        chunks.append(f"--- {old_path}\n")
        chunks.append(f"+++ {new_path}\n")
        patch = file_info["patch"]
        chunks.append(patch if patch.endswith("\n") else patch + "\n")
    return "".join(chunks)


def classify_surface_pattern(issue: dict[str, Any]) -> str:
    text = f"{issue.get('title', '')} {issue.get('labels', '')}".lower()
    if any(term in text for term in ["crash", "exception", "error", "traceback", "internal error"]):
        return "exception_or_crash"
    if any(term in text for term in ["wrong", "incorrect", "regression", "fails", "failure", "bug"]):
        return "assertion_or_behavior_mismatch"
    return "test_failure"


def classify_root_cause(issue: dict[str, Any], files: list[dict[str, Any]]) -> str:
    text = issue.get("title", "").lower()
    if any(term in text for term in ["empty", "none", "null", "missing", "skip", "unicode"]):
        return "missing_edge_case_handling"
    if len(files) > 1:
        return "cross_file_behavior_regression"
    return "localized_behavior_regression"


def requires_api_knowledge(project: str, issue: dict[str, Any]) -> bool:
    text = f"{project} {issue.get('title', '')} {issue.get('labels', '')}".lower()
    return any(term in text for term in ["api", "protocol", "exchange", "s3", "cloudfront", "discord", "jax", "numpy", "pandas"])


def issue_to_candidate(project: dict[str, Any], issue: dict[str, Any]) -> dict[str, Any]:
    commit = issue["commits"][0]
    stat = commit["stat"]
    source_files = [item for item in stat.get("files", []) if item.get("status") != "removed"]
    test_files = [item for item in stat.get("tests", []) if item.get("status") != "removed"]
    install_steps = issue.get("installSteps") or project.get("installSteps") or ""
    test_steps = issue.get("testSteps") or ""
    full_test_steps = issue.get("testStepsFull") or None
    changed_lines = sum(int(item.get("changes") or 0) for item in source_files)
    test_changed_lines = sum(int(item.get("changes") or 0) for item in test_files)
    repository = project["repository"]

    exclusions: list[str] = []
    warnings: list[str] = []
    if len(issue.get("commits", [])) != 1:
        exclusions.append("multiple_commits")
    if not commit.get("parents"):
        exclusions.append("missing_buggy_parent_commit")
    if len(source_files) > 3:
        exclusions.append("too_many_modified_files")
    if changed_lines > 100:
        exclusions.append("large_reference_patch")
    if not test_files:
        exclusions.append("no_test_files")
    if not test_steps:
        exclusions.append("no_test_steps")
    if not command_is_explicit_pytest(test_steps):
        warnings.append("test_command_may_need_manual_review")
    if any(not patch_supported(item) for item in source_files):
        exclusions.append("unsupported_source_patch")
    if any(not patch_supported(item) for item in test_files):
        exclusions.append("unsupported_test_patch")
    lowered_install = install_steps.lower()
    if any(pattern in lowered_install for pattern in HEAVY_INSTALL_PATTERNS):
        warnings.append("heavy_install_steps")
    if repository in HEAVY_PROJECTS:
        warnings.append("heavy_project")
    if issue.get("raceCondition"):
        exclusions.append("race_condition")
    if issue.get("text_based"):
        warnings.append("text_based_issue")

    score = (
        len(source_files) * 100
        + changed_lines
        + len(test_files) * 3
        + test_changed_lines
        + (500 if "heavy_project" in warnings else 0)
        + (250 if "heavy_install_steps" in warnings else 0)
    )
    return {
        "project": repository,
        "username": project["username"],
        "issue_id": issue["id"],
        "title": issue["title"],
        "labels": issue.get("labels") or "",
        "buggy_commit": commit["parents"],
        "fix_commit": commit["hash"],
        "source_files": source_files,
        "test_files": test_files,
        "changed_lines": changed_lines,
        "test_changed_lines": test_changed_lines,
        "install_steps": install_steps,
        "test_steps": test_steps,
        "full_test_steps": full_test_steps,
        "python_version": infer_python_version(install_steps),
        "exclusions": exclusions,
        "warnings": warnings,
        "score": score,
        "raw_issue": issue,
    }


def load_candidates(dataset_path: Path) -> list[dict[str, Any]]:
    projects = load_json(dataset_path)
    candidates: list[dict[str, Any]] = []
    for project in projects:
        for issue in project.get("issues", []):
            candidates.append(issue_to_candidate(project, issue))
    return candidates


def select_candidates(
    candidates: list[dict[str, Any]],
    project_allowlist: set[str] | None,
    limit: int,
    max_per_project: int,
    include_heavy: bool,
) -> list[dict[str, Any]]:
    eligible = []
    for candidate in candidates:
        if candidate["exclusions"]:
            continue
        if project_allowlist is not None and candidate["project"] not in project_allowlist:
            continue
        if not include_heavy and (
            "heavy_install_steps" in candidate["warnings"] or "heavy_project" in candidate["warnings"]
        ):
            continue
        eligible.append(candidate)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in sorted(eligible, key=lambda item: (item["score"], item["project"], item["issue_id"])):
        grouped[candidate["project"]].append(candidate)

    selected: list[dict[str, Any]] = []
    project_counts: dict[str, int] = defaultdict(int)
    while len(selected) < limit and grouped:
        progressed = False
        for project in sorted(list(grouped)):
            if project_counts[project] >= max_per_project:
                grouped.pop(project, None)
                continue
            if not grouped[project]:
                grouped.pop(project, None)
                continue
            selected.append(grouped[project].pop(0))
            project_counts[project] += 1
            progressed = True
            if len(selected) >= limit:
                break
        if not progressed:
            break
    return selected


def split_for_index(index: int, train_count: int) -> str:
    return "train" if index < train_count else "heldout"


def task_id_for(candidate: dict[str, Any]) -> str:
    return f"pybughive_{slugify(candidate['project'])}_{candidate['issue_id']}"


def write_candidate_artifacts(
    candidate: dict[str, Any],
    split: str,
    output_root: Path,
    patch_root: Path,
    metadata_root: Path,
    schema: dict[str, Any],
    dry_run: bool,
) -> dict[str, Path]:
    task_id = task_id_for(candidate)
    task_path = output_root / split / f"{task_id}.json"
    fix_patch_path = patch_root / f"{task_id}_fix.patch"
    test_patch_path = patch_root / f"{task_id}_tests.patch"
    metadata_path = metadata_root / task_id / "metadata.json"
    task_dir = task_path.parent

    fix_patch = build_git_patch(candidate["source_files"])
    test_patch = build_git_patch(candidate["test_files"])
    metadata = {
        "source": "pybughive",
        "project": candidate["project"],
        "issue_id": candidate["issue_id"],
        "title": candidate["title"],
        "labels": candidate["labels"],
        "buggy_commit": candidate["buggy_commit"],
        "fix_commit": candidate["fix_commit"],
        "warnings": candidate["warnings"],
        "score": candidate["score"],
        "raw_issue": candidate["raw_issue"],
    }
    source_files = [item["filename"] for item in candidate["source_files"]]
    test_files = [item["filename"] for item in candidate["test_files"]]
    task = {
        "task_id": task_id,
        "bug_family": "test_failure_triage",
        "split": split,
        "repo": {
            "name": candidate["project"],
            "source": "pybughive",
            "url": repo_url(candidate["username"], candidate["project"]),
            "commit": candidate["buggy_commit"],
            "language": "python",
        },
        "environment": {
            "python_version": candidate["python_version"],
            "install_command": normalize_install_steps(candidate["install_steps"]),
            "test_command": candidate["test_steps"],
            "full_test_command": candidate["full_test_steps"],
            "timeout_seconds": 300,
        },
        "failure": {
            "failing_tests": test_files or split_steps(candidate["test_steps"]),
            "error_type": "PyBugHiveTestFailure",
            "error_message": candidate["title"],
            "failure_log_path": "logs/initial_failure.txt",
        },
        "ground_truth": {
            "patch_path": relative_to_task(task_path, fix_patch_path),
            "modified_files": source_files,
            "bug_summary": candidate["title"],
        },
        "benchmark": {
            "name": "pybughive",
            "project": candidate["project"],
            "issue_id": candidate["issue_id"],
            "buggy_commit": candidate["buggy_commit"],
            "fix_commit": candidate["fix_commit"],
            "test_patch_path": relative_to_task(task_path, test_patch_path),
            "metadata_path": relative_to_task(task_path, metadata_path),
            "original_install_steps": candidate["install_steps"],
            "original_test_steps": candidate["test_steps"],
            "original_full_test_steps": candidate["full_test_steps"],
        },
        "labels": {
            "surface_pattern": classify_surface_pattern(candidate["raw_issue"]),
            "root_cause": classify_root_cause(candidate["raw_issue"], candidate["source_files"]),
            "requires_api_knowledge": requires_api_knowledge(candidate["project"], candidate["raw_issue"]),
            "adversarial_reason": None,
        },
    }
    validate_instance(task, schema)
    if not dry_run:
        task_dir.mkdir(parents=True, exist_ok=True)
        patch_root.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text(json.dumps(task, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        fix_patch_path.write_text(fix_patch, encoding="utf-8", newline="\n")
        test_patch_path.write_text(test_patch, encoding="utf-8", newline="\n")
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "task_path": task_path,
        "fix_patch_path": fix_patch_path,
        "test_patch_path": test_patch_path,
        "metadata_path": metadata_path,
    }


def write_candidate_csv(path: Path, candidates: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "task_id",
        "split",
        "project",
        "issue_id",
        "title",
        "buggy_commit",
        "fix_commit",
        "source_files",
        "test_files",
        "changed_lines",
        "test_changed_lines",
        "python_version",
        "warnings",
        "score",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for candidate in candidates:
            writer.writerow(
                {
                    "task_id": candidate["task_id"],
                    "split": candidate["split"],
                    "project": candidate["project"],
                    "issue_id": candidate["issue_id"],
                    "title": candidate["title"],
                    "buggy_commit": candidate["buggy_commit"],
                    "fix_commit": candidate["fix_commit"],
                    "source_files": ";".join(item["filename"] for item in candidate["source_files"]),
                    "test_files": ";".join(item["filename"] for item in candidate["test_files"]),
                    "changed_lines": candidate["changed_lines"],
                    "test_changed_lines": candidate["test_changed_lines"],
                    "python_version": candidate["python_version"] or "",
                    "warnings": ";".join(candidate["warnings"]),
                    "score": candidate["score"],
                }
            )


def write_report(path: Path, selected: list[dict[str, Any]], all_candidates: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    eligible = [candidate for candidate in all_candidates if not candidate["exclusions"]]
    lines = [
        "# PyBugHive Import Report",
        "",
        "## Summary",
        "",
        f"- Source issues: {len(all_candidates)}",
        f"- Metadata-eligible issues: {len(eligible)}",
        f"- Selected first-batch tasks: {len(selected)}",
        "- Reproducibility status: metadata-screened; environment execution still needs PyBugHive-compatible Python/pipenv setup.",
        "",
        "## Selected Tasks",
        "",
        "| Split | Task ID | Project | Issue | Source Files | Test Files | Warnings |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for candidate in selected:
        lines.append(
            "| {split} | `{task_id}` | {project} | {issue_id} | {source_count} | {test_count} | {warnings} |".format(
                split=candidate["split"],
                task_id=candidate["task_id"],
                project=candidate["project"],
                issue_id=candidate["issue_id"],
                source_count=len(candidate["source_files"]),
                test_count=len(candidate["test_files"]),
                warnings=", ".join(candidate["warnings"]) or "none",
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Each task includes a PyBugHive test patch under `patches/pybughive/` because PyBugHive exposes many bugs by copying tests from the fixing commit onto the buggy parent commit.",
            "- `scripts/prepare_task.py` now applies `benchmark.test_patch_path` before installing and reproducing the initial failure.",
            "- The generated `ground_truth.patch_path` contains only the reference source-code patch, separate from the test patch.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import metadata-screened PyBugHive tasks into the local debugging task schema."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--patch-root", type=Path, default=DEFAULT_PATCH_ROOT)
    parser.add_argument("--metadata-root", type=Path, default=DEFAULT_METADATA_ROOT)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--train-count", type=int, default=3)
    parser.add_argument("--max-per-project", type=int, default=6)
    parser.add_argument(
        "--project-allowlist",
        default=",".join(DEFAULT_PROJECT_ALLOWLIST),
        help="Comma-separated project allowlist. Use an empty string to allow all projects.",
    )
    parser.add_argument("--include-heavy", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be >= 1")
    if args.train_count < 0 or args.train_count > args.limit:
        parser.error("--train-count must be between 0 and --limit")

    project_allowlist = {
        item.strip() for item in args.project_allowlist.split(",") if item.strip()
    }
    candidates = load_candidates(args.dataset)
    selected = select_candidates(
        candidates,
        project_allowlist or None,
        args.limit,
        args.max_per_project,
        args.include_heavy,
    )
    if not selected:
        print("No PyBugHive candidates selected.", file=sys.stderr)
        return 1

    schema = load_json(args.schema)
    for index, candidate in enumerate(selected):
        split = split_for_index(index, args.train_count)
        candidate["split"] = split
        candidate["task_id"] = task_id_for(candidate)
        paths = write_candidate_artifacts(
            candidate,
            split,
            args.output_root,
            args.patch_root,
            args.metadata_root,
            schema,
            args.dry_run,
        )
        action = "WOULD-WRITE" if args.dry_run else "WROTE"
        print(f"{action} {candidate['task_id']} -> {paths['task_path']}")

    if not args.dry_run:
        write_candidate_csv(args.results_root / "pybughive_first_batch_candidates.csv", selected)
        write_report(args.results_root / "pybughive_import_report.md", selected, candidates)
        print(f"Wrote {args.results_root / 'pybughive_first_batch_candidates.csv'}")
        print(f"Wrote {args.results_root / 'pybughive_import_report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
