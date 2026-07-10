# PyBugHive Results Memo

Date: 2026-05-27

## Scope

- Dataset: PyBugHive held-out test-failure debugging tasks.
- Family: `test_failure_triage`.
- Train trajectories for induction: 3 solved `no_memory` runs.
- Held-out tasks: 7 tasks across `black`, `discord.py`, and `scrapy`.
- Methods: `no_memory`, `generic_checklist`, `reflexion`, `length_matched_reflexion`, `raw_trajectory_retrieval`, `format_shuffled_skill`, `auto_skill`.
- Completed held-out trajectories: 49/49.
- Agent model: `gpt-5.3-codex`.

## Validation

- All held-out trajectories under `trajectories/pybughive_heldout_memory_baselines/` validate against `schemas/trajectory.schema.json`.
- The two `pybughive_scrapy_2552` runs that were previously interrupted by Codex usage limits were rerun successfully:
  - `pybughive_heldout_memory_baselines_pybughive_scrapy_2552_format_shuffled_skill_seed1`
  - `pybughive_heldout_memory_baselines_pybughive_scrapy_2552_auto_skill_seed1`
- Final metrics are written to:
  - `results/pybughive_heldout_final_metrics.csv`
  - `results/pybughive_heldout_final_metrics.json`
  - `results/pybughive_scrapy2552_all_baselines_metrics.csv`
  - `results/pybughive_scrapy2552_all_baselines_metrics.json`

## Aggregate Metrics

| Method | Runs | Solved | Solve Rate | Cycles / Solved | Tokens / Solved | Negative Transfer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `auto_skill` | 7 | 7 | 1.0000 | 1.7143 | 51,982.4286 | 0.0000 |
| `generic_checklist` | 7 | 7 | 1.0000 | 1.4286 | 51,974.4286 | 0.0000 |
| `length_matched_reflexion` | 7 | 7 | 1.0000 | 1.7143 | 66,289.7143 | 0.1429 |
| `no_memory` | 7 | 7 | 1.0000 | 1.5714 | 47,905.1429 | 0.0000 |
| `format_shuffled_skill` | 7 | 6 | 0.8571 | 1.6667 | 35,310.8333 | 0.0000 |
| `raw_trajectory_retrieval` | 7 | 6 | 0.8571 | 1.0000 | 46,694.3333 | 0.0000 |
| `reflexion` | 7 | 6 | 0.8571 | 1.5000 | 40,230.5000 | 0.0000 |

## Main Readout

The strongest positive result is not that Auto-SKILL is universally best. It is that a low-shot induced procedural artifact is competitive with strong baselines and clearly better than the closest Reflexion-style memory controls on transfer reliability and negative-transfer behavior.

Compared with `length_matched_reflexion`, `auto_skill` reaches the same solve rate and the same cycles per solved task, while using about 21.6% fewer tokens per solved task and showing no negative transfer. `length_matched_reflexion` has one negative-transfer case.

Compared with `reflexion`, `auto_skill` solves one additional held-out task: 7/7 versus 6/7. However, among solved tasks, `reflexion` is more token-efficient. This means the current evidence supports a robustness/coverage claim more than a pure token-efficiency claim against Reflexion.

Compared with `format_shuffled_skill`, `auto_skill` solves one additional task: 7/7 versus 6/7. This is the most direct evidence that the structured Trigger Conditions / Debugging Procedure / Failure Modes format matters beyond merely exposing similar content. The evidence is promising but still small because the sample has only 7 held-out tasks.

The main complication is that `generic_checklist` and `no_memory` are very strong in this MVP. Both solve all 7 held-out tasks. `generic_checklist` has the best cycles per solved task, and `no_memory` has lower tokens per solved task than `auto_skill`. This makes the current PyBugHive setting useful as a pipeline and feasibility study, but insufficient as the final main experiment.

## Task-Level Signals

`pybughive_black_59` is the most informative differentiating task. `auto_skill`, `generic_checklist`, `length_matched_reflexion`, and `no_memory` solve it, while `reflexion`, `raw_trajectory_retrieval`, and `format_shuffled_skill` fail. This task supports the claim that structured procedural memory can avoid some failures seen in unstructured memory or shuffled content controls.

`pybughive_scrapy_2552` is a clean post-rerun sanity check. All methods solve it in one cycle. This task is useful for validating that the harness and rerun path are clean, but it does not separate methods strongly.

The `black` tasks provide the only multi-task repository family in this held-out set. They show mixed process behavior: Auto-SKILL is efficient on some tasks but over-invests on `pybughive_black_389` and `pybughive_black_59`. This suggests that procedural memory can guide transfer, but may also induce extra diagnosis when the local bug is easier than the learned procedure expects.

## Claims Supported by Current Evidence

1. Low-shot trajectory-to-SKILL induction is feasible: three solved trajectories produce a reusable natural-language `SKILL.md` that transfers to seven held-out tasks.
2. Auto-SKILL is competitive with strong agent-memory baselines on held-out test-failure debugging.
3. Auto-SKILL improves over length-matched Reflexion memory on token efficiency and negative-transfer rate at equal solve rate and cycle count.
4. Auto-SKILL improves over format-shuffled skill content on solve rate, supporting the value of structured procedural organization.
5. The current benchmark slice is too easy to establish that Auto-SKILL is better than all general debugging guidance or no-memory agents.

## Reviewer Risks

| Risk | Why it matters | Defensive framing |
| --- | --- | --- |
| `generic_checklist` is too strong | It matches Auto-SKILL solve rate and has better cycles. | Present PyBugHive as MVP evidence, not the final decisive benchmark. Add harder tasks where generic guidance is insufficient. |
| `no_memory` is too strong | It also solves 7/7 and uses fewer tokens than Auto-SKILL. | Emphasize that current tasks are localized test-failure repairs. Add tasks requiring longer diagnosis, misleading symptoms, or multi-file reasoning. |
| Small held-out set | 7 tasks cannot support broad claims. | Treat current results as pilot / feasibility. Expand to at least 20-30 held-out tasks or add a harder benchmark slice. |
| Single seed / single agent | Results may be sensitive to model sampling and transient tool behavior. | Add repeated seeds for a smaller hard subset, or explicitly scope this as a fixed-agent evaluation protocol. |
| Prompt-engineering criticism | `SKILL.md` may look like a better prompt. | Keep the paper framing as procedural memory artifact plus induction/evaluation protocol. Use `format_shuffled_skill` and `length_matched_reflexion` as controls. |
| Token metric ambiguity | Token totals include varying prompt overhead and agent behavior. | Report both total tokens and active-debugging tokens. Keep process metrics separate from solve-rate metrics. |

## Recommended Next Experiments

1. Build a hard held-out subset from PyBugHive where `no_memory` or `generic_checklist` is less likely to solve in one cycle. Selection criteria should include multi-file diagnosis, misleading failure messages, or cases where a naive local patch can pass a narrow assertion but break broader behavior.
2. Add an adversarial within-family split. Use tasks that superficially match the SKILL trigger conditions but require a different repair pattern. This directly tests negative transfer.
3. Add a cross-repository transfer slice. Keep the same broad test-failure family, but move beyond `black`-heavy held-out tasks to avoid repository-specific artifacts.
4. Run a small SWE-bench Lite or Defects4J-style extension only after the PyBugHive hard subset is stable. The current harness should first prove it can separate methods on cheaper tasks.
5. Add a paper-ready analysis table with per-task method outcomes, highlighting `black_59` as a differentiating case and `scrapy_2552` as a rerun sanity check.

## Paper Positioning

Use this result as the MVP evidence for an evaluation protocol, not as the final empirical claim.

Recommended wording:

> In a PyBugHive pilot with 3 induction trajectories and 7 held-out test-failure debugging tasks, Auto-SKILL matched the best solve-rate baselines and outperformed Reflexion-style memory controls on robustness and negative-transfer behavior. However, generic debugging guidance and no-memory agents remained highly competitive, indicating that stronger hard-subset construction is necessary before claiming broad superiority.

This wording preserves the main contribution: evaluating low-shot procedural skill transfer, not selling `SKILL.md` as a universally better prompt.
