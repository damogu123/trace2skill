| Run | Model setting | Tasks | Methods | Evidence role | Result artifacts |
|---|---|---:|---|---|---|
| Primary first-six hard smoke | `gpt-5.3-codex` | 6 | no memory; generic checklist; Reflexion; length-matched Reflexion; Auto SKILL.md | Main quantitative evidence | `paper/tables/hard_first6_main_table.md`; `results/pybughive_hard_first6_by_method_metrics.csv` |
| Exploratory all-seven aggregate | model-mixed: first six under `gpt-5.3-codex`, `black_234` under `gpt-5.5` | 7 | no memory; generic checklist; Reflexion; length-matched Reflexion; Auto SKILL.md | Supplementary robustness check only | `paper/tables/hard_first7_exploratory_table.md`; `results/pybughive_hard_first7_by_method_metrics.csv` |
| Structural-control first-six rerun | `gpt-5.5` | 6 | Auto SKILL.md; format-shuffled SKILL.md | Supplementary structure-versus-content boundary check | `paper/tables/hard_first6_structural_control_gpt55.md`; `results/pybughive_hard_auto_vs_format_shuffled_first6_gpt55_report.md` |
