from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifact_agenticdev2026"

TEXT_SUFFIXES = {
    ".bib",
    ".csv",
    ".json",
    ".md",
    ".patch",
    ".py",
    ".svg",
    ".tex",
    ".txt",
    ".yaml",
    ".yml",
}

EXCLUDED_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    "svg-inkscape",
}

EXCLUDED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pdf",
    ".png",
    ".pyc",
    ".synctex.gz",
    ".xmpi",
}

PRIMARY_FIRST6_TASKS = [
    "pybughive_black_132",
    "pybughive_black_133",
    "pybughive_black_154",
    "pybughive_black_183",
    "pybughive_black_193",
    "pybughive_black_232",
]

EXPLORATORY_ALL7_TASKS = PRIMARY_FIRST6_TASKS + ["pybughive_black_234"]

TRAIN_TASKS = [
    "pybughive_black_297",
    "pybughive_cookiecutter_1513",
    "pybughive_discord_py_7676",
]

PRIMARY_METHODS = [
    "auto_skill",
    "generic_checklist",
    "length_matched_reflexion",
    "no_memory",
    "reflexion",
]

STRUCTURAL_METHODS = [
    "auto_skill",
    "format_shuffled_skill",
]

MANIFEST_FILES = [
    "pybughive_train_trajectories_codex.json",
    "pybughive_hard_smoke_codex.json",
    "pybughive_hard_auto_skill_first6_codex_gpt55.json",
    "pybughive_hard_format_shuffled_first6_codex_gpt55.json",
]

RESULT_PATTERNS = [
    "pybughive_hard_*",
    "pybughive_train_trajectories_metrics.*",
    "pybughive_environment_check.*",
    "pybughive_wsl_*",
    "pybughive_import_report.md",
    "pybughive_reproducibility_status.*",
]

SUPPLEMENTARY_RESULT_FILES = [
    "pybughive_pipeline_status.md",
    "pybughive_results_memo.md",
    "pybughive_task_breakdown.md",
    "pybughive_heldout_final_metrics.csv",
    "pybughive_heldout_final_metrics.json",
]

PAPER_SECTION_FILES = [
    "abstract.md",
    "introduction.md",
    "method.md",
    "results.md",
    "discussion.md",
    "limitations.md",
    "result_claims_guardrails.md",
]

PAPER_REVIEW_FILES = [
    "agenticdev_2026_format_report_2026_06_08.md",
    "full_manuscript_consistency_report_2026_06_08.md",
    "latex_build_report_2026_06_08.md",
    "p0_revision_report_2026_07_10.md",
]


def ensure_within(parent: Path, child: Path) -> None:
    parent_resolved = parent.resolve()
    child_resolved = child.resolve()
    try:
        child_resolved.relative_to(parent_resolved)
    except ValueError as exc:
        raise ValueError(f"Refusing to operate outside workspace: {child_resolved}") from exc


def should_skip(path: Path) -> bool:
    if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
        return True
    name = path.name.lower()
    if name.endswith(".synctex.gz"):
        return True
    return path.suffix.lower() in EXCLUDED_SUFFIXES


def sanitize_text(text: str) -> str:
    wsl_root = ""
    root_posix = ROOT.as_posix()
    if len(root_posix) >= 2 and root_posix[1] == ":":
        drive = root_posix[0].lower()
        wsl_root = f"/mnt/{drive}{root_posix[2:]}"

    local_python = Path.home() / "AppData" / "Local" / "Python"
    local_programs_python = Path.home() / "AppData" / "Local" / "Programs" / "Python"

    replacements = {
        str(ROOT): "<PROJECT_ROOT>",
        str(ROOT).replace("\\", "\\\\"): "<PROJECT_ROOT>",
        root_posix: "<PROJECT_ROOT>",
        str(local_python): "<LOCAL_PYTHON>",
        str(local_python).replace("\\", "\\\\"): "<LOCAL_PYTHON>",
        str(local_programs_python): "<LOCAL_PYTHON>",
        str(local_programs_python).replace("\\", "\\\\"): "<LOCAL_PYTHON>",
    }
    if wsl_root:
        replacements[wsl_root] = "<PROJECT_ROOT>"
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def copy_file(source: Path, destination: Path) -> bool:
    if not source.exists() or should_skip(source.relative_to(ROOT)):
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() in TEXT_SUFFIXES:
        text = source.read_text(encoding="utf-8-sig")
        destination.write_text(sanitize_text(text), encoding="utf-8", newline="\n")
    else:
        shutil.copy2(source, destination)
    return True


def copy_tree(source: Path, destination: Path) -> tuple[int, int]:
    copied = 0
    skipped = 0
    for item in sorted(source.rglob("*")):
        relative_to_source = item.relative_to(source)
        relative_to_root = item.relative_to(ROOT)
        if item.is_dir():
            if should_skip(relative_to_root):
                skipped += 1
                continue
            (destination / relative_to_source).mkdir(parents=True, exist_ok=True)
            continue
        if should_skip(relative_to_root):
            skipped += 1
            continue
        if copy_file(item, destination / relative_to_source):
            copied += 1
        else:
            skipped += 1
    return copied, skipped


def copy_glob(source_dir: Path, pattern: str, destination_dir: Path) -> tuple[int, int]:
    copied = 0
    skipped = 0
    for source in sorted(source_dir.glob(pattern)):
        if source.is_file():
            if copy_file(source, destination_dir / source.name):
                copied += 1
            else:
                skipped += 1
    return copied, skipped


def copy_named_files(source_dir: Path, names: list[str], destination_dir: Path) -> tuple[int, int]:
    copied = 0
    skipped = 0
    for name in names:
        source = source_dir / name
        if copy_file(source, destination_dir / name):
            copied += 1
        else:
            skipped += 1
    return copied, skipped


def copy_task_set(output: Path, names: list[str], destination: Path, source_base: Path) -> int:
    copied = 0
    for task_id in names:
        source = source_base / f"{task_id}.json"
        if copy_file(source, output / destination / f"{task_id}.json"):
            copied += 1
    return copied


def copy_trajectory_files(
    output: Path,
    source_dir: Path,
    destination_dir: Path,
    task_ids: list[str],
    methods: list[str],
) -> int:
    copied = 0
    for task_id in task_ids:
        for method in methods:
            matches = sorted(source_dir.glob(f"*_{task_id}_{method}_seed1.json"))
            for source in matches:
                if copy_file(source, output / destination_dir / source.name):
                    copied += 1
    return copied


def copy_training_trajectories(output: Path, destination_dir: Path) -> int:
    source_dir = ROOT / "trajectories" / "pybughive_train_trajectories"
    copied = 0
    for task_id in TRAIN_TASKS:
        matches = sorted(source_dir.glob(f"*_{task_id}_no_memory_seed1.json"))
        for source in matches:
            if copy_file(source, output / destination_dir / source.name):
                copied += 1
    return copied


def write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")


def raw_runs_inventory() -> str:
    rows = ["run_dir\tfiles\tbytes\tincluded_in_artifact"]
    runs_dir = ROOT / "runs"
    if not runs_dir.exists():
        return "\n".join(rows)
    for child in sorted(runs_dir.iterdir()):
        if not child.is_dir():
            continue
        files = [item for item in child.rglob("*") if item.is_file()]
        bytes_total = sum(item.stat().st_size for item in files)
        rows.append(f"{child.name}\t{len(files)}\t{bytes_total}\tno")
    return "\n".join(rows)


def file_inventory(output: Path) -> str:
    rows = ["path\tbytes\tsha256"]
    for file_path in sorted(item for item in output.rglob("*") if item.is_file()):
        if file_path.name == "FILE_INVENTORY.tsv":
            continue
        relative = file_path.relative_to(output).as_posix()
        data = file_path.read_bytes()
        rows.append(f"{relative}\t{len(data)}\t{hashlib.sha256(data).hexdigest()}")
    return "\n".join(rows)


def readme_text() -> str:
    return """
# AgenticDev 2026 Artifact Package

This folder is a curated, GitHub-ready artifact for the paper:

**Evaluating Low-Shot Procedural Skill Transfer in Language-Agent Debugging**

It contains the data and process records used for the AgenticDev 2026 submission:

- the `K=3` induction trajectories;
- the primary same-model PyBugHive hard-smoke experiment;
- the model-mixed all-seven exploratory record;
- the `gpt-5.5` structural-control rerun;
- scripts, schemas, prompts, memory artifacts, task metadata, patches, metrics,
  paper tables, and process reports needed to audit the claims.

## Quick Validation

From this artifact folder:

```powershell
py scripts\\validate_task.py tasks
py scripts\\validate_trajectory.py trajectories
py scripts\\validate_run_manifest.py manifests
py scripts\\validate_task.py task_sets\\primary_first6
py scripts\\validate_trajectory.py trajectory_sets\\primary_first6
py scripts\\validate_run_manifest.py manifests
```

Recompute the main first-six aggregate:

```powershell
py scripts\\compute_metrics.py trajectory_sets\\primary_first6 --tasks task_sets\\primary_first6 --group-by method --output-csv results\\recomputed_primary_first6_by_method.csv --output-json results\\recomputed_primary_first6_by_method.json
```

Recompute the `gpt-5.5` structural control:

```powershell
py scripts\\compute_metrics.py trajectory_sets\\structural_control_gpt55 --tasks task_sets\\primary_first6 --group-by method --output-csv results\\recomputed_structural_control_gpt55_by_method.csv --output-json results\\recomputed_structural_control_gpt55_by_method.json
```

## Main Experimental Sets

| Set | Location | Role |
|---|---|---|
| `K=3` induction training | `trajectory_sets/induction_train_k3/` | Source trajectories used to induce `memory/pybughive/test_failure_triage/auto_skill.md` |
| Primary first-six hard smoke | `trajectory_sets/primary_first6/` | Main quantitative evidence in the paper |
| Exploratory all-seven hard smoke | `trajectory_sets/exploratory_all7/` | Supplementary model-mixed robustness check |
| Structural control `gpt-5.5` | `trajectory_sets/structural_control_gpt55/` | Auto SKILL.md vs. format-shuffled SKILL.md |

The full curated trajectory directories are also available under `trajectories/`.

## What Is Not Included

The local `runs/` directory is not copied. It is about 250 MB and contains raw
agent stdout, temporary checkout paths, and machine-specific run logs. The
validated trajectory JSON files in this artifact are the canonical cleaned
process records used for metrics and paper claims.

The external PyBugHive source dump under `data/external/` is not copied. This
artifact includes the curated task metadata and patches derived from it.
"""


def reproduce_text() -> str:
    return """
# Reproduction Notes

## Validation

The artifact is designed so the schema validators work from this folder without
additional path configuration:

```powershell
py scripts\\validate_task.py tasks
py scripts\\validate_trajectory.py trajectories
py scripts\\validate_run_manifest.py manifests
```

## Metrics

Primary first-six hard-smoke result:

```powershell
py scripts\\compute_metrics.py trajectory_sets\\primary_first6 --tasks task_sets\\primary_first6 --group-by method --output-csv results\\recomputed_primary_first6_by_method.csv --output-json results\\recomputed_primary_first6_by_method.json
```

Structural-control result:

```powershell
py scripts\\compute_metrics.py trajectory_sets\\structural_control_gpt55 --tasks task_sets\\primary_first6 --group-by method --output-csv results\\recomputed_structural_control_gpt55_by_method.csv --output-json results\\recomputed_structural_control_gpt55_by_method.json
```

Paper-ready tables and figures can be regenerated with:

```powershell
py scripts\\make_paper_results.py
```

That script uses the precomputed CSV files in `results/` and writes to
`paper/tables/` and `paper/figures/`.

## Rerunning Agents

The original agent executions used isolated workspaces, WSL-compatible Python
environments for PyBugHive tasks, and an external-agent contract implemented by
`scripts/run_external_agent.py` and `scripts/run_codex_agent.py`.

The artifact preserves manifests and prompts for auditability, but it is not
intended to replay the exact paid/interactive agent runs without configuring an
equivalent model endpoint and local benchmark environment.
"""


def selection_text() -> str:
    return """
# Data Selection

## Included In The Main Artifact

- `tasks/pybughive/train/`: the three induction-source tasks.
- `tasks/pybughive_hard/heldout/`: the verified hard-smoke held-out tasks,
  including the excluded verification-failure candidate `pybughive_black_1632`
  for provenance.
- `trajectories/pybughive_train_trajectories/`: `K=3` no-memory induction
  trajectories.
- `trajectories/pybughive_hard_smoke/`: seven hard-smoke tasks x five methods.
  The first six tasks are the primary same-model result; `black_234` is
  exploratory model-mixed evidence.
- `trajectories/pybughive_hard_auto_skill_first6/` and
  `trajectories/pybughive_hard_format_shuffled_first6/`: `gpt-5.5`
  structural-control reruns.
- `trajectory_sets/`: convenience subsets used in the paper.
- `memory/`, `baselines/`, `prompts/`, `annotation/`, `schemas/`, `scripts/`,
  `results/`, `paper/tables/`, and `paper/figures/`.

## Included Separately

`supplementary_harness_validation/` contains the earlier easy PyBugHive MVP
records. These runs validate the harness but are not the paper's primary
quantitative evidence.

## Excluded

- `runs/`: raw run logs and temporary execution artifacts. Excluded for size and
  machine-specific paths.
- `workspaces/`: reconstructable isolated checkouts.
- `data/external/`: external PyBugHive source dump. Curated task metadata and
  patches are included instead.
- PDFs and LaTeX build intermediates.
"""


def build_artifact(output: Path, force: bool) -> dict[str, int]:
    output = output.resolve()
    ensure_within(ROOT, output)

    if output.exists():
        if not force:
            raise FileExistsError(f"{output} exists; pass --force to recreate it")
        shutil.rmtree(output)
    output.mkdir(parents=True)

    copied = 0
    skipped = 0

    for root_file in [".gitattributes", ".gitignore", "requirements.txt"]:
        if copy_file(ROOT / root_file, output / root_file):
            copied += 1

    for source_name in ["scripts", "schemas", "annotation", "baselines"]:
        c, s = copy_tree(ROOT / source_name, output / source_name)
        copied += c
        skipped += s

    c, s = copy_tree(
        ROOT / "memory" / "pybughive" / "test_failure_triage",
        output / "memory" / "pybughive" / "test_failure_triage",
    )
    copied += c
    skipped += s

    c, s = copy_tree(ROOT / "patches" / "pybughive", output / "patches" / "pybughive")
    copied += c
    skipped += s
    c, s = copy_tree(ROOT / "patches" / "pybughive_hard", output / "patches" / "pybughive_hard")
    copied += c
    skipped += s

    copied += copy_task_set(output, TRAIN_TASKS, Path("tasks") / "pybughive" / "train", ROOT / "tasks" / "pybughive" / "train")
    copied += copy_task_set(output, EXPLORATORY_ALL7_TASKS + ["pybughive_black_1632"], Path("tasks") / "pybughive_hard" / "heldout", ROOT / "tasks" / "pybughive_hard" / "heldout")

    copied += copy_task_set(output, TRAIN_TASKS, Path("task_sets") / "induction_train_k3", ROOT / "tasks" / "pybughive" / "train")
    copied += copy_task_set(output, PRIMARY_FIRST6_TASKS, Path("task_sets") / "primary_first6", ROOT / "tasks" / "pybughive_hard" / "heldout")
    copied += copy_task_set(output, EXPLORATORY_ALL7_TASKS, Path("task_sets") / "exploratory_all7", ROOT / "tasks" / "pybughive_hard" / "heldout")

    for source_name in [
        "pybughive_train_trajectories",
        "pybughive_hard_smoke",
        "pybughive_hard_auto_skill_first6",
        "pybughive_hard_format_shuffled_first6",
    ]:
        c, s = copy_tree(ROOT / "trajectories" / source_name, output / "trajectories" / source_name)
        copied += c
        skipped += s

    copied += copy_training_trajectories(output, Path("trajectory_sets") / "induction_train_k3")
    copied += copy_trajectory_files(
        output,
        ROOT / "trajectories" / "pybughive_hard_smoke",
        Path("trajectory_sets") / "primary_first6",
        PRIMARY_FIRST6_TASKS,
        PRIMARY_METHODS,
    )
    copied += copy_trajectory_files(
        output,
        ROOT / "trajectories" / "pybughive_hard_smoke",
        Path("trajectory_sets") / "exploratory_all7",
        EXPLORATORY_ALL7_TASKS,
        PRIMARY_METHODS,
    )
    copied += copy_trajectory_files(
        output,
        ROOT / "trajectories" / "pybughive_hard_auto_skill_first6",
        Path("trajectory_sets") / "structural_control_gpt55",
        PRIMARY_FIRST6_TASKS,
        ["auto_skill"],
    )
    copied += copy_trajectory_files(
        output,
        ROOT / "trajectories" / "pybughive_hard_format_shuffled_first6",
        Path("trajectory_sets") / "structural_control_gpt55",
        PRIMARY_FIRST6_TASKS,
        ["format_shuffled_skill"],
    )

    c, s = copy_named_files(ROOT / "manifests", MANIFEST_FILES, output / "manifests")
    copied += c
    skipped += s

    if copy_file(ROOT / "prompts" / "induction_prompt_v2.md", output / "prompts" / "induction_prompt_v2.md"):
        copied += 1
    c, s = copy_tree(ROOT / "prompts" / "induction", output / "prompts" / "induction")
    copied += c
    skipped += s
    for run_prompt_dir in [
        "pybughive_train_trajectories",
        "pybughive_hard_smoke",
        "pybughive_hard_auto_skill_first6",
        "pybughive_hard_format_shuffled_first6",
    ]:
        c, s = copy_tree(ROOT / "prompts" / "runs" / run_prompt_dir, output / "prompts" / "runs" / run_prompt_dir)
        copied += c
        skipped += s

    c, s = copy_tree(ROOT / "data" / "pybughive", output / "data" / "pybughive")
    copied += c
    skipped += s
    c, s = copy_tree(ROOT / "data" / "pybughive_hard", output / "data" / "pybughive_hard")
    copied += c
    skipped += s
    if copy_file(ROOT / "data" / "pilot_task_selection_guide.md", output / "data" / "pilot_task_selection_guide.md"):
        copied += 1

    for pattern in RESULT_PATTERNS:
        c, s = copy_glob(ROOT / "results", pattern, output / "results")
        copied += c
        skipped += s

    c, s = copy_tree(ROOT / "paper" / "tables", output / "paper" / "tables")
    copied += c
    skipped += s
    c, s = copy_tree(ROOT / "paper" / "figures", output / "paper" / "figures")
    copied += c
    skipped += s
    c, s = copy_named_files(ROOT / "paper" / "sections", PAPER_SECTION_FILES, output / "paper" / "sections")
    copied += c
    skipped += s
    c, s = copy_named_files(ROOT / "paper" / "reviews", PAPER_REVIEW_FILES, output / "paper" / "reviews")
    copied += c
    skipped += s
    for paper_file in ["main.tex", "BUILD.md", "references.bib", "manuscript_index.md"]:
        if copy_file(ROOT / "paper" / paper_file, output / "paper" / paper_file):
            copied += 1

    # Supplementary easy-MVP harness validation, separated from paper evidence.
    c, s = copy_tree(
        ROOT / "trajectories" / "pybughive_heldout_memory_baselines",
        output / "supplementary_harness_validation" / "trajectories" / "pybughive_heldout_memory_baselines",
    )
    copied += c
    skipped += s
    c, s = copy_tree(
        ROOT / "tasks" / "pybughive" / "heldout",
        output / "supplementary_harness_validation" / "tasks" / "pybughive" / "heldout",
    )
    copied += c
    skipped += s
    if copy_file(
        ROOT / "manifests" / "pybughive_heldout_memory_baselines_codex.json",
        output / "supplementary_harness_validation" / "manifests" / "pybughive_heldout_memory_baselines_codex.json",
    ):
        copied += 1
    c, s = copy_named_files(ROOT / "results", SUPPLEMENTARY_RESULT_FILES, output / "supplementary_harness_validation" / "results")
    copied += c
    skipped += s

    write_text_file(output / "README.md", readme_text())
    write_text_file(output / "REPRODUCE.md", reproduce_text())
    write_text_file(output / "DATA_SELECTION.md", selection_text())
    write_text_file(output / "process" / "raw_runs_inventory.tsv", raw_runs_inventory())
    write_text_file(output / "FILE_INVENTORY.tsv", file_inventory(output))

    return {"copied_files": copied, "skipped_files": skipped}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the curated AgenticDev 2026 artifact folder.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    stats = build_artifact(args.output, args.force)
    print(f"Wrote {args.output.resolve()}")
    print(f"Copied files: {stats['copied_files']}")
    print(f"Skipped files/directories: {stats['skipped_files']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
