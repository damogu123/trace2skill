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
