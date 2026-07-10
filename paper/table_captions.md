# Table Captions

**Table 1. Same-model hard-smoke results over six PyBugHive Black debugging tasks.** Auto SKILL.md ties the best solve rate and has the lowest token cost per solved task. This table should be the main quantitative result because all included runs share the same model setup.

**Table 2. Per-task solve matrix for the same-model hard-smoke tasks.** This table reports exact task-level outcomes and negative-transfer flags, making clear that the evidence is subfamily-sensitive rather than uniformly positive.

**Table 3. Paired common-solved efficiency comparison.** Auto SKILL.md is compared against each baseline only on tasks both methods solved, reducing the risk that solve-conditional token averages are driven by different solved-task sets.

**Table S1. Model-mixed all-seven exploratory aggregate.** Includes pybughive_black_234 under gpt-5.5 and should be treated as supplementary until all tasks are rerun under one model.

**Table S2. pybughive_black_234 single-task exploratory result.** All methods solved, so the task is useful mainly for token-cost and qualitative patch-behavior discussion.
