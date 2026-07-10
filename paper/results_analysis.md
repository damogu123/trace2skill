# Results Analysis Package

Generated from local experiment outputs on 2026-06-02.

## Recommended Result Claim

The current evidence supports a cautious efficiency-and-transfer claim, not a broad dominance claim:

> On a same-model hard-smoke slice of six PyBugHive Black debugging tasks, Auto SKILL.md matched the best solve rate (5/6) while using fewer tokens per solved task than Reflexion-style memory, a length-matched Reflexion control, a generic debugging checklist, and no memory. The result suggests that natural-language procedural memory can improve low-shot within-family transfer efficiency, but it is subfamily-sensitive and can still produce negative transfer.

## Main Same-Model Evidence

Use the first-six result as the main quantitative table because all six tasks were run under the same model setup.

- Auto SKILL.md solved 5/6 tasks, tied with Generic checklist and Reflexion memory for best solve rate.
- Auto SKILL.md used 56,867 tokens per solved task.
- Relative to Reflexion memory, Auto SKILL.md reduced cycles from 2.60 to 2.00 and tokens from 65,915 to 56,867.
- Relative to length-matched Reflexion, Auto SKILL.md improved solve rate from 0.6667 to 0.8333 and reduced tokens by 24.4%.
- Relative to no memory, Auto SKILL.md improved solve rate from 0.6667 to 0.8333 and reduced tokens by 38.2%.
- Relative to Generic checklist, Auto SKILL.md had the same solve rate and cycle average, but used 20.7% fewer tokens.

## Important Caveats

- The first-seven aggregate is model-mixed because pybughive_black_234 used gpt-5.5 after gpt-5.3-codex became unavailable. Treat it as exploratory.
- The current hard subset is Black-only and formatting-heavy. It is valuable for controlled within-family transfer, but not enough for a general agent-debugging claim.
- Negative transfer is not zero: Auto SKILL.md failed pybughive_black_132 and was flagged for negative transfer on that task.
- Do not claim statistical significance yet. With six same-model tasks, report exact task-level outcomes, paired common-solved comparisons, and qualitative case studies.

## Pairwise Common-Solved Efficiency

This analysis compares Auto SKILL.md against each baseline only on tasks both methods solved. It avoids comparing token averages over different solved-task sets.

See `paper/tables/hard_first6_common_solved_pairwise.md`.

- Against Generic checklist on common solved tasks (black_133, black_154, black_183, black_232), Auto SKILL.md reduced cycles by 0.0% and tokens by 19.8%.
- Against Reflexion memory on common solved tasks (black_133, black_154, black_183, black_232), Auto SKILL.md reduced cycles by 36.4% and tokens by 32.2%.
- Against Length-matched Reflexion on common solved tasks (black_133, black_154, black_183, black_232), Auto SKILL.md reduced cycles by 36.4% and tokens by 36.2%.
- Against No memory on common solved tasks (black_154, black_183, black_232), Auto SKILL.md reduced cycles by 33.3% and tokens by 32.6%.

## Figure Inventory

- `paper/figures/evaluation_protocol_diagram.svg`: method and evaluation protocol diagram.
- `paper/figures/hard_first6_main_bars.svg`: main same-model solve-rate and token-efficiency figure.
- `paper/figures/hard_first6_efficiency_scatter.svg`: cycles-vs-tokens process-efficiency figure.
- `paper/figures/hard_first6_task_outcomes_heatmap.svg`: per-task outcome heatmap with negative-transfer marker.
- `paper/figures/hard_first7_exploratory_bars.svg`: supplementary model-mixed all-seven figure.
- `paper/figures/black234_tokens.svg`: supplementary single-task token-cost figure for pybughive_black_234.

## Table Inventory

- `paper/tables/hard_first6_main_table.md` and `.tex`: main paper table.
- `paper/tables/hard_first6_task_outcomes.md`: per-task solve matrix.
- `paper/tables/hard_first6_common_solved_pairwise.md` and `.csv`: paired common-solved efficiency analysis.
- `paper/tables/hard_first7_exploratory_table.md` and `.tex`: supplementary model-mixed table.
- `paper/tables/black234_single_task_table.md`: single-task exploratory table.

## Draft Results Paragraph

Table 1 reports the same-model hard-smoke results over six PyBugHive Black tasks. Auto SKILL.md matched the strongest solve rate, solving 5/6 tasks, while reducing token cost relative to Reflexion memory, length-matched Reflexion, a generic debugging checklist, and the no-memory baseline. The gain is most clearly an efficiency result: compared with Reflexion, Auto SKILL.md achieved the same solve rate with fewer diagnosis-edit-test cycles and fewer tokens per solved task. Compared with length-matched Reflexion, it improved both solve rate and process efficiency, suggesting that the procedural structure of the memory artifact matters beyond adding more text to the context. The result is not uniformly positive: Auto SKILL.md failed on pybughive_black_132 and triggered the only negative-transfer flag. We therefore interpret SKILL.md as a subfamily-sensitive procedural memory artifact that can improve low-shot within-family transfer efficiency, rather than as a universally beneficial prompt.

## Suggested Paper Placement

- Main text Figure 1: `evaluation_protocol_diagram.svg`.
- Main text Figure 2: `hard_first6_main_bars.svg`.
- Main text Figure 3: `hard_first6_task_outcomes_heatmap.svg` or the process-efficiency scatter, depending on space.
- Main text Table 1: `hard_first6_main_table.tex`.
- Appendix: first-seven exploratory table, pybughive_black_234 single-task table, and pairwise common-solved table.
