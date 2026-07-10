# Held-Out Codex First Run Report

## Status

One real Codex held-out run completed successfully.

Run:

```text
heldout_memory_baselines_local_empty_average_bug_no_memory_seed1
```

Condition:

```text
no_memory
```

## Outcome

- Initial failing test reproduced before agent execution.
- Codex edited the isolated checkout.
- Narrow failing test passed after the patch.
- Full test suite passed after the patch.
- `agent_trace.json` was produced and copied into the harness artifacts directory.
- Harness-generated trajectory validated against `schemas/trajectory.schema.json`.
- Patch capture now records the actual code diff.

## Key Artifacts

- Trace: `runs/heldout_memory_baselines/heldout_memory_baselines_local_empty_average_bug_no_memory_seed1/agent_trace.json`
- Patch: `runs/heldout_memory_baselines/heldout_memory_baselines_local_empty_average_bug_no_memory_seed1/agent.patch`
- Trajectory: `trajectories/heldout_memory_baselines/heldout_memory_baselines_local_empty_average_bug_no_memory_seed1.json`
- Partial metrics: `results/heldout_memory_baselines_partial_metrics.json`

## Harness Fixes Made During This Run

- `scripts/run_codex_agent.py` now asks Codex to write trace inside the repo and copies it to the harness artifact path afterward. This avoids Codex sandbox write restrictions on external directories.
- `scripts/run_external_agent.py` now applies snapshot exclusion rules to paths relative to the checkout root, not absolute paths. This prevents `workspaces/runs/...` from accidentally excluding the entire repo.
- Experiment docs now include `--prepare` for real runs so each execution starts from a fresh failing checkout.

## Current Metrics

The single completed run has:

- solve rate: 1.0
- cycles per solved task: 1.0
- tokens per solved task: 3500.0
- negative transfer rate: 0.0

This is still only one held-out run. It verifies the real-agent pipeline, not the paper claim.
