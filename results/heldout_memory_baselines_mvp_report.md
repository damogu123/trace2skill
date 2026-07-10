# Held-Out Memory Baselines MVP Report

Date: 2026-05-18

## Scope

- Manifest: `manifests/heldout_memory_baselines_codex.json`
- Agent model: `gpt-5.3-codex`
- Tasks: 3 held-out local test-failure triage tasks
- Methods: `no_memory`, `generic_checklist`, `reflexion`, `length_matched_reflexion`, `raw_trajectory_retrieval`, `format_shuffled_skill`, `auto_skill`
- Completed trajectories: 21/21

## Validation

- All trajectory files under `trajectories/heldout_memory_baselines/` validate against `schemas/trajectory.schema.json`.
- All completed runs pass the narrow failing test and full test command.
- Token counts were backfilled from Codex CLI `tokens used` lines with `scripts/repair_codex_token_counts.py`.

## Aggregate Metrics

| Method | Runs | Solved | Solve Rate | Cycles / Solved | Tokens / Solved | Negative Transfer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| no_memory | 3 | 3 | 1.0 | 1.0 | 15795.6667 | 0.0 |
| generic_checklist | 3 | 3 | 1.0 | 1.0 | 16919.3333 | 0.0 |
| auto_skill | 3 | 3 | 1.0 | 1.0 | 16963.0 | 0.0 |
| format_shuffled_skill | 3 | 3 | 1.0 | 1.0 | 17756.6667 | 0.0 |
| raw_trajectory_retrieval | 3 | 3 | 1.0 | 1.0 | 18097.3333 | 0.0 |
| length_matched_reflexion | 3 | 3 | 1.0 | 1.0 | 19061.6667 | 0.0 |
| reflexion | 3 | 3 | 1.0 | 1.0 | 21936.6667 | 0.0 |

## Recovery Note

`heldout_memory_baselines_local_whitespace_title_bug_auto_skill_seed1` hit the Codex usage limit after applying the correct patch but before writing `agent_trace.json`. The run was recovered from its agent log:

- The log shows the diagnosis, inspected files, applied patch, and `tokens used = 13,081`.
- The harness reran narrow and full tests after recovery; both passed.
- The recovered trace uses one cycle with `test_command`/`test_passed` delegated to harness final evaluation.

## Interpretation

This MVP confirms that the harness, schemas, prompt packs, memory artifacts, Codex runner, token repair, and metric pipeline work end to end. It does not yet provide evidence that Auto-SKILL outperforms baselines, because these three local held-out tasks are too easy: every method solves every task in one cycle.

## Recommended Next Step

Add harder within-family held-out tasks where no-memory and generic-checklist baselines are less likely to solve in one step. Prioritize tasks requiring multi-file diagnosis, misleading surface symptoms, or a failed first patch opportunity so process-efficiency and negative-transfer metrics become informative.
