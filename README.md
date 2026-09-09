# Trace2Skill

**Low-shot procedural skill transfer for language-agent debugging.**

Trace2Skill is the reproducibility artifact and evaluation harness for the
paper **"Evaluating Low-Shot Procedural Skill Transfer in Language-Agent
Debugging."** The project studies whether a language agent can induce a reusable
natural-language `SKILL.md` artifact from only a few successful debugging
trajectories and transfer that procedural memory to held-out PyBugHive bug-fix
tasks.

The repository includes the manuscript source, cleaned trajectory records,
experiment manifests, validation scripts, metrics, and a compact
AgenticDev/ASE Workshop artifact package.

## Project Page And Paper

- Project page: https://damogu123.github.io/trace2skill/
- Paper DOI: https://doi.org/10.1145/3843282.3844421
- Camera-ready project-page copy: `docs/static/pdfs/trace2skill-paper.pdf`

## Start Here

- Reviewing the artifact: start with `artifact_agenticdev2026/README.md`,
  then `artifact_agenticdev2026/DATA_SELECTION.md` and
  `artifact_agenticdev2026/REPRODUCE.md`.
- Checking the paper claims: see `paper/sections/results.md`,
  `paper/tables/`, and the aggregate files under `results/`.
- Running schema checks: use the commands in [Quick Validation](#quick-validation).
- Inspecting the latest project state: read `SESSION_HANDOFF.md`.

## Key Result Snapshot

The primary empirical claim is intentionally narrow:

- Primary evidence uses the first six PyBugHive `black` hard-smoke tasks under
  the same-model `gpt-5.3-codex` setting.
- Auto `SKILL.md` solves 5/6 primary tasks, tied with the strongest primary
  baselines.
- The main signal is process efficiency rather than universal solve-rate
  dominance.
- One explicit negative-transfer case is recorded and preserved.
- The supplementary `gpt-5.5` structural-control rerun should not be read as
  proof that the canonical `SKILL.md` format is required for solvability.

## Repository Layout

- `artifact_agenticdev2026/`: compact upload-ready artifact for the AgenticDev
  2026 submission, including curated task sets, trajectory sets, scripts,
  schemas, metrics, paper tables, and reproduction notes.
- `scripts/`: task import, validation, manifest construction, agent execution
  wrappers, trajectory recording, metric computation, and paper-result
  generation.
- `schemas/`: JSON schemas for tasks, run manifests, trajectories, and agent
  traces.
- `tasks/`: benchmark task definitions used by the harness.
- `memory/`: frozen memory artifacts used as experimental conditions.
- `manifests/`: runnable experiment manifests.
- `prompts/`: prompt templates and generated prompt packs.
- `trajectories/`: validated trajectory JSON records used for analysis.
- `results/`: aggregate metrics, setup reports, and cleanup reports.
- `paper/`: manuscript source, bibliography, figure source, tables, reviews,
  and build notes.
- `docs/`: operational documentation for the harness and repository packaging.

Large generated or local-only artifacts are intentionally excluded from Git:
raw `runs/`, temporary `workspaces/`, process `logs/`, LaTeX intermediates,
rendered screenshots, compiled PDFs, and `data/external/`.

## Quick Validation

The harness scripts use only the Python standard library. Use Python 3.12+ for
the repository-level scripts. The commands below use the Windows `py` launcher;
on Linux/macOS, replace `py` with `python` or `python3`. Some benchmark
checkouts may require their own pinned Python environments or
WSL/Linux-compatible execution.

Validate the top-level records:

```powershell
py scripts/validate_task.py tasks
py scripts/validate_trajectory.py trajectories
py scripts/validate_run_manifest.py manifests
```

Validate the compact AgenticDev artifact:

```powershell
py scripts/validate_task.py artifact_agenticdev2026/tasks
py scripts/validate_trajectory.py artifact_agenticdev2026/trajectory_sets/primary_first6
py scripts/validate_trajectory.py artifact_agenticdev2026/trajectory_sets/structural_control_gpt55
py scripts/validate_run_manifest.py artifact_agenticdev2026/manifests
```

Recompute the main first-six aggregate:

```powershell
py scripts/compute_metrics.py artifact_agenticdev2026/trajectory_sets/primary_first6 --tasks artifact_agenticdev2026/task_sets/primary_first6 --group-by method --output-json results/recomputed_primary_first6_by_method.json --output-csv results/recomputed_primary_first6_by_method.csv
```

## Running Agent Experiments

Run a Codex-backed agent experiment after preparing a model-specific manifest:

```powershell
py scripts/run_external_agent.py manifests/pybughive_hard_smoke_codex.json --agent-command "py scripts/run_codex_agent.py --prompt-path {prompt_path} --repo-dir {repo_dir} --artifacts-dir {artifacts_dir} --trace-path {trace_path} --model gpt-5.3-codex" --require-agent-zero --prepare --skip-existing-trajectories
```

Read `docs/codex_agent_runner.md` and
`docs/real_agent_execution_checklist.md` before launching paid or long-running
runs.

## Manuscript Build

The AgenticDev/ASE Workshop version is built from `paper/main.tex` with ACM
`acmart` and SVG conversion through Inkscape:

```powershell
cd paper
latexmk -pdf -jobname=main_agenticdev -shell-escape -interaction=nonstopmode -file-line-error main.tex
```

Full build notes are in `paper/BUILD.md`. Compiled PDFs are excluded from the
Git repository by default.

## Reproducibility Notes

- The canonical process evidence for the paper is in `trajectories/` and
  `artifact_agenticdev2026/trajectory_sets/`.
- Frozen files under `memory/pybughive/test_failure_triage/` should not be
  edited and reused with old results. Any changed memory artifact needs a new
  condition name, manifest, and rerun.
- Raw `runs/` logs were removed from the cleaned workspace after the validated
  trajectory JSON records and `artifact_agenticdev2026/` package were created.
- `data/external/` was removed from the cleaned workspace. Curated PyBugHive
  task metadata remains under `data/pybughive/` and `data/pybughive_hard/`.
- Reference patches are used to verify task reproducibility and solvability;
  they are not shown to the held-out repair agent.

## Citation

```bibtex
@inproceedings{sun2026trace2skill,
  author = {Sun, Jiachen},
  title = {Evaluating Low-Shot Procedural Skill Transfer in Language-Agent Debugging},
  year = {2026},
  booktitle = {Proceedings of the 1st International Workshop on Agentic AI for Next-Generation Software Development},
  doi = {10.1145/3843282.3844421}
}
```

## License

The camera-ready paper is licensed under CC BY 4.0. The project-page layout and
code under `docs/` are licensed under CC BY-SA 4.0; see
`docs/PROJECT_PAGE_LICENSE.md`. No repository-wide software or data license has
been selected, so all other material remains all rights reserved by default.
