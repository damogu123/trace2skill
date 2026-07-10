# PyBugHive Pipeline Status

## Completed

- Collected 3 PyBugHive train trajectories with `no_memory`.
- All 3 train runs solved the task and passed both narrow and full tests.
- Validated all generated trajectory JSON files against `schemas/trajectory.schema.json`.
- Generated PyBugHive memory artifacts under `memory/pybughive/test_failure_triage/`.
- Generated a redacted induction prompt package at `prompts/induction/pybughive_test_failure_triage_k3_seed1.md`.
- Generated held-out evaluation manifest at `manifests/pybughive_heldout_memory_baselines_codex.json`.
- Built 49 held-out prompt packs for 7 tasks x 7 methods.
- Preflighted the first held-out task in WSL and confirmed the initial failure reproduces.
- Ran a first held-out smoke comparison on `pybughive_black_1493` for `no_memory` and `auto_skill`.
- Completed the full single-task held-out baseline comparison on `pybughive_black_1493` across all 7 methods.
- Completed the full single-task held-out baseline comparison on `pybughive_black_185` across all 7 methods.
- Audited the PyBugHive induction prompt and frozen Auto-SKILL quality.
- Completed the full single-task held-out baseline comparison on `pybughive_black_389` across all 7 methods.
- Completed the full single-task held-out baseline comparison on `pybughive_black_59` across all 7 methods.
- Completed the full single-task held-out baseline comparison on `pybughive_discord_py_7818` across all 7 methods.
- Completed the full single-task held-out baseline comparison on `pybughive_scrapy_1265` across all 7 methods.
- Completed the final held-out batch for `pybughive_scrapy_2552`; the 2 runs that were previously interrupted by Codex usage limits (`format_shuffled_skill`, `auto_skill`) were rerun successfully on 2026-05-27.
- Wrote the PyBugHive results memo and task-level breakdown for paper drafting.

## Train Summary

| Task | Solved | Narrow | Full | Cycles | Modified files |
| --- | --- | --- | --- | --- | --- |
| `pybughive_black_297` | yes | pass | pass | 1 | 1 |
| `pybughive_cookiecutter_1513` | yes | pass | pass | 1 | 1 |
| `pybughive_discord_py_7676` | yes | pass | pass | 1 | 1 |

Aggregate metrics are written to:

- `results/pybughive_train_trajectories_metrics.json`
- `results/pybughive_train_trajectories_metrics.csv`

Note: token usage for `pybughive_black_297` is unavailable because it used the older adapter before `codex_stdout.log` capture was added. The other two runs have token usage restored from Codex stdout.

## Memory Artifacts

- `memory/pybughive/test_failure_triage/auto_skill.md`
- `memory/pybughive/test_failure_triage/reflexion.md`
- `memory/pybughive/test_failure_triage/length_matched_reflexion.md`
- `memory/pybughive/test_failure_triage/raw_trajectory_retrieval.md`
- `memory/pybughive/test_failure_triage/format_shuffled_skill.md`
- `memory/pybughive/test_failure_triage/oracle_skill_template.md`

## Runner Fixes

- `scripts/run_codex_agent.py` now captures Codex stdout to `codex_stdout.log`.
- `scripts/run_codex_agent.py` now uses UTF-8 stdout/stderr to avoid Windows GBK crashes.
- `scripts/run_codex_agent.py` now terminates a lingering Codex CLI process after final message and trace are written.
- `scripts/create_run_manifest.py` now emits `python3 scripts/prepare_task.py` for PyBugHive tasks.
- `scripts/induce_skill.py` now anonymizes source file labels in induction prompts.
- `scripts/induce_skill.py` now redacts dotted identifiers, snake-case identifiers, issue references, and known project/package terms in induction prompt summaries.
- `scripts/run_external_agent.py` now normalizes string-valued agent mistake entries into `{type, description}` objects before schema validation.
- `scripts/run_external_agent.py` now normalizes non-schema negative-transfer categories emitted by agents, mapping invalid process-style categories to `performance` when negative transfer is detected.
- `scripts/prepare_task.py` now reuses an existing same-URL local checkout when preparing repeated PyBugHive runs, then checks out the task commit, reducing repeated GitHub clone overhead without changing task contents.
- `scripts/prepare_task.py` now tries shallow fetch of the exact task commit before falling back to full clone, which avoided repeated GitHub RPC resets on `scrapy`.

## Prompt and Skill QA

- Quality audit written to `results/pybughive_prompt_skill_quality_audit.md`.
- `memory/pybughive/test_failure_triage/auto_skill.md` is frozen as Auto-SKILL v1 for the current held-out run.
- The regenerated induction prompt removes concrete function, issue, and project/package leakage from redacted training summaries.
- Existing held-out results remain comparable because the frozen memory artifacts were not edited mid-run.

## Held-out Single-task Smoke Result

| Method | Task | Solved | Cycles | Tokens | Negative transfer |
| --- | --- | --- | --- | --- | --- |
| `auto_skill` | `pybughive_black_1493` | yes | 1 | 24,520 | no |
| `format_shuffled_skill` | `pybughive_black_1493` | yes | 2 | 48,228 | no |
| `generic_checklist` | `pybughive_black_1493` | yes | 1 | 27,688 | no |
| `length_matched_reflexion` | `pybughive_black_1493` | yes | 1 | 15,223 | no |
| `no_memory` | `pybughive_black_1493` | yes | 2 | 71,879 | no |
| `raw_trajectory_retrieval` | `pybughive_black_1493` | yes | 1 | 45,117 | no |
| `reflexion` | `pybughive_black_1493` | yes | 2 | 32,977 | no |

Single-task smoke metrics are written to:

- `results/pybughive_black1493_all_baselines_metrics.json`
- `results/pybughive_black1493_all_baselines_metrics.csv`

Interpretation: all methods solved this one held-out task. `auto_skill` improves over `no_memory`, `reflexion`, `format_shuffled_skill`, and `raw_trajectory_retrieval` on process efficiency, but `length_matched_reflexion` used fewer tokens on this single task. This is a useful pilot signal, not enough evidence for the paper claim until more held-out tasks are run.

## Held-out Final Result

Current held-out progress: 49 / 49 trajectories valid. All previously interrupted `pybughive_scrapy_2552` conditions have been rerun and now contain real agent traces, patches, and final test results.

| Task | Completed runs |
| --- | ---: |
| `pybughive_black_1493` | 7 / 7 |
| `pybughive_black_185` | 7 / 7 |
| `pybughive_black_389` | 7 / 7 |
| `pybughive_black_59` | 7 / 7 |
| `pybughive_discord_py_7818` | 7 / 7 |
| `pybughive_scrapy_1265` | 7 / 7 |
| `pybughive_scrapy_2552` | 7 / 7 |

`pybughive_scrapy_2552` final single-task metrics:

| Method | Solved | Cycles | Tokens | Negative transfer |
| --- | ---: | ---: | ---: | ---: |
| `auto_skill` | 1 | 1.0 | 31,151 | 0.0 |
| `format_shuffled_skill` | 1 | 1.0 | 20,881 | 0.0 |
| `generic_checklist` | 1 | 1.0 | 27,754 | 0.0 |
| `length_matched_reflexion` | 1 | 1.0 | 20,131 | 0.0 |
| `no_memory` | 1 | 1.0 | 14,736 | 0.0 |
| `raw_trajectory_retrieval` | 1 | 1.0 | 65,335 | 0.0 |
| `reflexion` | 1 | 1.0 | 14,635 | 0.0 |

Final aggregate metrics across all held-out trajectories:

| Method | Runs | Solved | Solve rate | Cycles / solved | Tokens / solved | Negative transfer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `auto_skill` | 7 | 7 | 1.0 | 1.7143 | 51,982.4286 | 0.0 |
| `format_shuffled_skill` | 7 | 6 | 0.8571 | 1.6667 | 35,310.8333 | 0.0 |
| `generic_checklist` | 7 | 7 | 1.0 | 1.4286 | 51,974.4286 | 0.0 |
| `length_matched_reflexion` | 7 | 7 | 1.0 | 1.7143 | 66,289.7143 | 0.1429 |
| `no_memory` | 7 | 7 | 1.0 | 1.5714 | 47,905.1429 | 0.0 |
| `raw_trajectory_retrieval` | 7 | 6 | 0.8571 | 1.0 | 46,694.3333 | 0.0 |
| `reflexion` | 7 | 6 | 0.8571 | 1.5 | 40,230.5 | 0.0 |

Metrics are written to:

- `results/pybughive_scrapy2552_all_baselines_metrics.json`
- `results/pybughive_scrapy2552_all_baselines_metrics.csv`
- `results/pybughive_heldout_final_metrics.json`
- `results/pybughive_heldout_final_metrics.csv`
- `results/pybughive_results_memo.md`
- `results/pybughive_task_breakdown.md`

Existing single-task metrics are written to:

- `results/pybughive_black1493_all_baselines_metrics.json`
- `results/pybughive_black1493_all_baselines_metrics.csv`
- `results/pybughive_black185_all_baselines_metrics.json`
- `results/pybughive_black185_all_baselines_metrics.csv`
- `results/pybughive_black389_all_baselines_metrics.json`
- `results/pybughive_black389_all_baselines_metrics.csv`
- `results/pybughive_black59_all_baselines_metrics.json`
- `results/pybughive_black59_all_baselines_metrics.csv`
- `results/pybughive_discord7818_all_baselines_metrics.json`
- `results/pybughive_discord7818_all_baselines_metrics.csv`
- `results/pybughive_scrapy1265_all_baselines_metrics.json`
- `results/pybughive_scrapy1265_all_baselines_metrics.csv`

## Next Step

Use `results/pybughive_results_memo.md` and `results/pybughive_task_breakdown.md` to draft the paper Results subsection. Then design the next hard-subset experiment, because the current PyBugHive MVP is informative but still too easy: `generic_checklist` and `no_memory` both solve all 7 held-out tasks.
