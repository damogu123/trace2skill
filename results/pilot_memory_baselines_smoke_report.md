# Pilot Memory Baselines Smoke Report

## Status

This run validates the evaluation harness, not the research hypothesis.

The 7 non-oracle pilot conditions were executed on the local toy fixture:

- no_memory
- generic_checklist
- reflexion
- length_matched_reflexion
- raw_trajectory_retrieval
- format_shuffled_skill
- auto_skill

All runs reproduced the initial failing test, applied one deterministic manual smoke patch, passed the narrow failing test, and passed the full test command.

## Artifacts

- Manifest: `manifests/pilot_memory_baselines.json`
- Prompt packs: `prompts/runs/pilot_memory_baselines/`
- Run logs and patches: `runs/pilot_memory_baselines/`
- Trajectories: `trajectories/pilot_memory_baselines/`
- Metrics JSON: `results/pilot_memory_baselines_metrics.json`
- Metrics CSV: `results/pilot_memory_baselines_metrics.csv`

## Harness Findings

- Per-run workspaces are isolated by checkout path.
- Test execution now prepends the active checkout's `src` directory to `PYTHONPATH`.
- This fixed cross-run contamination caused by repeated editable installs of the same package name.
- Trajectory validation passes for all 7 runs.
- Metrics computation succeeds for all 7 runs grouped by method, split, and bug family.

## Evidence Boundary

These results must not be used as paper evidence for SKILL.md transfer because:

- The task is a single toy training fixture, not a held-out benchmark task.
- The patch was applied by a deterministic manual smoke runner, not an independent language agent.
- Token counts are rough smoke estimates from prompt text length, not model-reported usage.
- All methods receive the same one-cycle manual fix, so method comparisons are not meaningful.

The next valid experiment step is to replace `manual-smoke-agent` with a real agent runner and run on held-out tasks from the same bug family.
