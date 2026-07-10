# PyBugHive Hard First-Six Same-Model Structural Control

Date: 2026-06-03

## Purpose

This report compares `auto_skill` and `format_shuffled_skill` under the same model, `gpt-5.5`, on the first six PyBugHive Black hard-smoke tasks:

- `pybughive_black_132`
- `pybughive_black_133`
- `pybughive_black_154`
- `pybughive_black_183`
- `pybughive_black_193`
- `pybughive_black_232`

The goal is to separate two explanations:

- Content effect: the skill contains useful debugging information regardless of structure.
- Procedural-structure effect: the `Trigger Conditions`, `Debugging Procedure`, and `Failure Modes` organization changes agent behavior.

## Artifacts

- Auto manifest: `manifests/pybughive_hard_auto_skill_first6_codex_gpt55.json`
- Auto prompts: `prompts/runs/pybughive_hard_auto_skill_first6/`
- Auto trajectories: `trajectories/pybughive_hard_auto_skill_first6/`
- Auto aggregate metrics: `results/pybughive_hard_auto_skill_first6_gpt55_metrics.csv`
- Auto by-task metrics: `results/pybughive_hard_auto_skill_first6_gpt55_by_task_metrics.csv`
- Shuffled aggregate metrics: `results/pybughive_hard_format_shuffled_first6_gpt55_metrics.csv`
- Shuffled by-task metrics: `results/pybughive_hard_format_shuffled_first6_gpt55_by_task_metrics.csv`

## Aggregate Result

| Method | Model | Solved | Solve rate | Cycles per solved task | Tokens per solved task | Failed patches per run | Mistakes per cycle | Negative transfer |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `auto_skill` | `gpt-5.5` | 6/6 | 1.0000 | 1.6667 | 111978.3333 | 0.5000 | 1.0000 | 0.0000 |
| `format_shuffled_skill` | `gpt-5.5` | 6/6 | 1.0000 | 2.1667 | 102005.8333 | 0.8333 | 0.6923 | 0.0000 |

## By-Task Result

| Task | Auto cycles | Shuffled cycles | Auto tokens | Shuffled tokens | Auto failed patches | Shuffled failed patches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `pybughive_black_132` | 2 | 2 | 107406 | 107759 | 0 | 1 |
| `pybughive_black_133` | 2 | 2 | 57947 | 58483 | 1 | 0 |
| `pybughive_black_154` | 2 | 2 | 78849 | 65245 | 1 | 1 |
| `pybughive_black_183` | 1 | 1 | 74970 | 133830 | 0 | 0 |
| `pybughive_black_193` | 1 | 4 | 258676 | 184255 | 0 | 2 |
| `pybughive_black_232` | 2 | 2 | 94022 | 62463 | 1 | 1 |

## Interpretation

- Solve rate does not separate the two methods under `gpt-5.5`: both solved all six tasks.
- Auto SKILL records fewer cycles on average: `1.6667` vs `2.1667`.
- Auto SKILL records fewer failed patches on average: `0.5000` vs `0.8333`.
- Auto SKILL is not more token-efficient in aggregate: `111978.3333` vs `102005.8333` tokens per solved task.
- The token disadvantage is mostly driven by `pybughive_black_193`, where Auto SKILL solved but used `258676` tokens. The trace records this as one cycle, but the stdout and mistake list show substantial internal patch search. Treat this as a process-cost outlier, not a clean one-step solve.
- The shuffled baseline is surprisingly strong under `gpt-5.5`. This weakens any claim that the SKILL.md structure alone is necessary for solving this controlled Black subset.
- The most defensible same-model claim is narrower: procedural structure may reduce recorded repair cycles and patch churn, but the current evidence does not show consistent token-efficiency superiority over shuffled content.

## Claim Guidance

Safe wording:

- "Under a same-model `gpt-5.5` structural-control rerun, both Auto SKILL.md and format-shuffled skill content solved all six tasks. Auto SKILL.md used fewer recorded cycles and fewer failed patches, while token cost was mixed and higher in aggregate because of a high-cost `black_193` run."
- "These results suggest that procedural organization affects process behavior, but they do not support a strong claim that SKILL.md structure is strictly necessary for solvability or uniformly more token-efficient."
- "The format-shuffled control closes the solve-rate gap under a stronger model, so the paper should position SKILL.md as a procedural memory artifact whose benefits are evaluated through process metrics and failure analysis, not as a guaranteed solve-rate improvement."

Avoid wording:

- "Auto SKILL.md outperforms format-shuffled skill on all metrics."
- "The experiment proves that SKILL.md structure is required."
- "The shuffled baseline is only prompt noise."

## Recommended Paper Use

Use this as a supplementary structural-control result, not as the primary main table. The cleanest primary table remains the original first-six same-model comparison across `auto_skill`, `reflexion`, `length_matched_reflexion`, `generic_checklist`, and `no_memory`.

In Discussion, this result should be used as a useful boundary finding:

- stronger models can recover from shuffled procedural content;
- structure still appears to reduce some process costs;
- process metrics must be reported alongside solve rate;
- token efficiency is fragile and can be dominated by one hard task.

## Next Experiment

If compute allows, the next clean step is to rerun the other baselines under `gpt-5.5` on the same first-six tasks:

- `no_memory`
- `generic_checklist`
- `reflexion`
- `length_matched_reflexion`

That would produce a fully same-model updated table. If compute is limited, prioritize `length_matched_reflexion` and `reflexion`, because the core paper claim compares procedural memory against reflection-style memory.
