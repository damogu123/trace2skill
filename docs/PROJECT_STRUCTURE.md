# Project Structure

This workspace contains both the publishable code repository and local research
artifacts. They should not all be committed to GitHub.

## Commit-Friendly Source

- `scripts/`: reproducibility harness and analysis scripts.
- `schemas/`: JSON schemas and dependency-free validators.
- `tasks/`: task records consumed by the harness.
- `manifests/`: experiment manifests.
- `memory/`: frozen experimental memory conditions.
- `patches/`: dataset/reference patch material referenced by tasks.
- `fixtures/`: synthetic local harness tests.
- `docs/`: operating notes.
- `paper/`: manuscript source, bibliography, figure source, tables, reviews, and
  literature-review notes.

## Small Evidence Artifacts Worth Keeping

- `trajectories/`: validated JSON trajectory records.
- `results/*.csv`, `results/*.json`, and `results/*.md`: aggregate reports and
  reproducibility notes.
- `data/pybughive/` and `data/pybughive_hard/`: curated metadata derived for the
  project.

## Local-Only Or Release Artifacts

- `runs/`: raw logs, traces, final patches, and test logs. Keep locally or attach
  to a release/archive; do not commit by default.
- `workspaces/`: reconstructable isolated task checkouts.
- `logs/`: process logs and PID files.
- `data/external/`: third-party benchmark source data. Check redistribution
  permissions before sharing publicly.
- `paper/*.pdf`: compiled PDFs. Prefer attaching final PDFs to releases unless
  the target repository intentionally includes them.
- `paper/svg-inkscape/`, `paper/render*/`, `results/*.png`: generated visual
  inspection or LaTeX conversion artifacts.

## Frozen-Artifacts Rule

Do not edit frozen memory artifacts and reuse old results. If a file under
`memory/pybughive/test_failure_triage/` changes, create a new condition name,
new manifest, and new trajectories.

## Current Evidence Boundary

The main paper result is based on the first six PyBugHive `black` hard-smoke
tasks under the same model setting. The seventh `black_234` task and the
`gpt-5.5` structural control are supplementary evidence. Preserve that boundary
in documentation and release notes.
