# Appendix Results

## A. Model-mixed all-seven aggregate

The all-seven result includes `pybughive_black_234`, which was run with `gpt-5.5` after `gpt-5.3-codex` became unavailable in the local Codex CLI session. This table is useful as a robustness and completion check, but it should not replace the first-six same-model result as the paper's main quantitative evidence.

```text
See: paper/tables/hard_first7_exploratory_table.md
Figure: paper/figures/hard_first7_exploratory_bars.svg
```

Key observation: Auto SKILL.md, Reflexion memory, and the generic checklist each solve 6/7 tasks. Auto SKILL.md remains the most token-efficient successful method among the five primary methods in this model-mixed aggregate, but the generic checklist has the lowest cycle average after adding `black_234`. This reinforces the need to frame the contribution as an evaluation protocol plus evidence for procedural-memory efficiency, not as universal dominance.

## B. pybughive_black_234 single-task note

All five methods solved `pybughive_black_234`. The root cause was localized in `LineGenerator.visit_import_from`: Black's custom import-from parenthesis handling inserted optional parentheses for long `from ... import *` statements, producing invalid code, and could also run across `# fmt: off` import regions.

```text
See: paper/tables/black234_single_task_table.md
Figure: paper/figures/black234_tokens.svg
```

This task mainly separates methods by token cost. Length-matched Reflexion, Reflexion memory, and the generic checklist solved in one cycle with roughly 51k-54k tokens. Auto SKILL.md solved in two cycles and 73k tokens. No memory solved in one cycle but used roughly 99k tokens. Because all methods solved, this task is not a strong solve-rate separator.

## C. Common-solved paired comparison

The paired common-solved table compares Auto SKILL.md against each baseline only on tasks both methods solved. This should be used in the paper or appendix to make the efficiency claim more conservative.

```text
See: paper/tables/hard_first6_common_solved_pairwise.md
CSV: paper/tables/hard_first6_common_solved_pairwise.csv
```

Recommended wording:

> To avoid comparing solve-conditional means over different solved-task subsets, we also compute paired efficiency on common-solved tasks. On tasks solved by both Auto SKILL.md and Reflexion memory, Auto SKILL.md reduces diagnosis-edit-test cycles by 36.4% and tokens by 32.2%. Against the length-matched Reflexion control on the same common-solved set, it reduces cycles by 36.4% and tokens by 36.2%.

## D. Same-model structural-control rerun

We additionally reran Auto SKILL.md and format-shuffled SKILL.md under `gpt-5.5` on the same first-six hard-smoke tasks. This result is supplementary because it uses a later model than the primary five-method table and includes only two methods. It is useful as a structure-versus-content boundary check.

```text
See: paper/tables/hard_first6_structural_control_gpt55.md
Detailed report: results/pybughive_hard_auto_vs_format_shuffled_first6_gpt55_report.md
```

Key observation: both Auto SKILL.md and the format-shuffled control solve all six tasks. Auto SKILL.md uses fewer recorded cycles (1.67 vs. 2.17) and fewer failed patches per run (0.50 vs. 0.83), but it is not more token-efficient in aggregate (111,978 vs. 102,006 tokens per solved task). This supports a process-behavior interpretation of procedural structure, not a claim that structure is required for solvability.

## E. Experiment ledger

The experiment ledger separates primary and supplementary evidence by model setting, task count, and method set. This table should be included in the appendix so readers do not merge the original `gpt-5.3-codex` five-method table with the later `gpt-5.5` structural-control rerun.

```text
See: paper/tables/experiment_ledger.md
LaTeX: paper/tables/experiment_ledger.tex
```
