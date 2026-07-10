# PyBugHive Hard First-Six Format-Shuffled Control

Date: 2026-06-02

## Purpose

This run evaluates `format_shuffled_skill` as a structural prompt-control baseline on the first six PyBugHive Black hard-smoke tasks:

- `pybughive_black_132`
- `pybughive_black_133`
- `pybughive_black_154`
- `pybughive_black_183`
- `pybughive_black_193`
- `pybughive_black_232`

The control keeps the skill content available but disrupts the intended `Trigger Conditions`, `Debugging Procedure`, and `Failure Modes` organization. It is meant to test whether the SKILL.md artifact is merely extra text or whether its procedural structure matters.

## Important Model Caveat

These six runs used `gpt-5.5` because `gpt-5.3-codex` is unavailable for this ChatGPT-account Codex CLI session. The original first-six hard-smoke baselines used the earlier `gpt-5.3-codex` setup.

Therefore, this report is model-mixed relative to the original first-six main table. It should be treated as exploratory structural-control evidence, not inserted directly into the same-model primary comparison.

## Artifacts

- Manifest: `manifests/pybughive_hard_format_shuffled_first6_codex_gpt55.json`
- Prompts: `prompts/runs/pybughive_hard_format_shuffled_first6/`
- Trajectories: `trajectories/pybughive_hard_format_shuffled_first6/`
- Aggregate metrics CSV: `results/pybughive_hard_format_shuffled_first6_gpt55_metrics.csv`
- Aggregate metrics JSON: `results/pybughive_hard_format_shuffled_first6_gpt55_metrics.json`
- By-task metrics CSV: `results/pybughive_hard_format_shuffled_first6_gpt55_by_task_metrics.csv`
- By-task metrics JSON: `results/pybughive_hard_format_shuffled_first6_gpt55_by_task_metrics.json`

## Aggregate Result

| Method | Model | Solved | Solve rate | Cycles per solved task | Tokens per solved task | Failed patches per run | Mistakes per cycle | Negative transfer |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `format_shuffled_skill` | `gpt-5.5` | 6/6 | 1.0000 | 2.1667 | 102005.8333 | 0.8333 | 0.6923 | 0.0000 |

## By-Task Result

| Task | Solved | Cycles | Tokens | Failed patches | Mistakes per cycle | Negative transfer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `pybughive_black_132` | 1 | 2 | 107759 | 1 | 1.5000 | 0 |
| `pybughive_black_133` | 1 | 2 | 58483 | 0 | 0.5000 | 0 |
| `pybughive_black_154` | 1 | 2 | 65245 | 1 | 0.5000 | 0 |
| `pybughive_black_183` | 1 | 1 | 133830 | 0 | 1.0000 | 0 |
| `pybughive_black_193` | 1 | 4 | 184255 | 2 | 0.5000 | 0 |
| `pybughive_black_232` | 1 | 2 | 62463 | 1 | 0.5000 | 0 |

## Context Against Original First-Six Table

The clean same-model first-six table remains:

| Method | Solved | Solve rate | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: | ---: |
| `auto_skill` | 5/6 | 0.8333 | 2.0000 | 56866.8000 | 0.1667 |
| `generic_checklist` | 5/6 | 0.8333 | 2.0000 | 71694.4000 | 0.0000 |
| `reflexion` | 5/6 | 0.8333 | 2.6000 | 65914.6000 | 0.0000 |
| `length_matched_reflexion` | 4/6 | 0.6667 | 2.7500 | 75231.2500 | 0.0000 |
| `no_memory` | 4/6 | 0.6667 | 3.0000 | 92030.7500 | 0.0000 |

Because of the model mismatch, the new `format_shuffled_skill` row should not be compared as a direct causal estimate against this table. Still, it is informative that the shuffled control solved all six tasks but used substantially more tokens than the original `auto_skill`, `reflexion`, and `generic_checklist` aggregates.

## Interpretation

- The shuffled control did not collapse: under `gpt-5.5`, it solved all six tasks.
- The process cost was high: `102005.8333` tokens per solved task, with especially expensive runs on `black_183` and `black_193`.
- The result weakens any claim that structure alone is required for solvability under a stronger/current model.
- The result is still consistent with a process-efficiency claim: even when shuffled content is enough to solve, it appears to require more search, patch churn, and token budget.
- `black_193` is the most useful qualitative case. The original same-model first-six table had `auto_skill` as the only successful method; the shuffled control also solved it under `gpt-5.5`, but needed 4 cycles and 184255 tokens. This should be described as a hypothesis-generating case, not a direct proof.

## Claim Guidance

Safe wording:

- "In a supplementary structural-control run under `gpt-5.5`, the format-shuffled skill solved all six hard Black tasks but required high token expenditure, suggesting that shuffled skill content can remain useful for stronger models while preserving the need for same-model controls."
- "The current clean evidence supports procedural memory primarily as an efficiency-oriented artifact, especially against length-matched reflection and no-memory baselines, rather than as unconditional solve-rate dominance."
- "A definitive structure-vs-content comparison requires rerunning `auto_skill` and `format_shuffled_skill` under the same model."

Avoid wording:

- "The format-shuffled result proves SKILL.md structure is irrelevant."
- "The original Auto-SKILL.md is strictly better than shuffled skill."
- "The shuffled control is part of the primary same-model first-six comparison."

## Recommended Next Experiment

The highest-value follow-up is a same-model `gpt-5.5` first-six comparison between:

- `auto_skill`
- `format_shuffled_skill`
- `length_matched_reflexion`
- `reflexion`
- `generic_checklist`
- `no_memory`

If compute is limited, rerun only `auto_skill` under `gpt-5.5` on the same six tasks first. This would establish whether the high solve rate of `format_shuffled_skill` is mainly a model upgrade effect or whether the shuffled baseline genuinely closes the gap.
