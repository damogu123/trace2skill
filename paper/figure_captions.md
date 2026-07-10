# Figure Captions

**Figure 1. Evaluation protocol for low-shot procedural skill transfer.** Historical debugging trajectories are compressed into a natural-language SKILL.md artifact containing trigger conditions, a debugging procedure, and failure modes. The same held-out debugging tasks are then run with Auto SKILL.md and four controls: no memory, a generic debugging checklist, Reflexion-style memory, and a length-matched Reflexion control. Outcomes are evaluated by solve rate, diagnosis-edit-test cycles, token cost, repeated mistakes, and negative transfer.

**Figure 2. Same-model hard-smoke aggregate over the first six PyBugHive Black tasks.** Auto SKILL.md matches the strongest solve rate while using fewer tokens per solved task than the memory and no-memory controls. Because the comparison is solve-conditional, the per-task outcome heatmap and paired common-solved table should be reported alongside this figure.

**Figure 3. Process efficiency among solved hard-smoke tasks.** Points show each method's average diagnosis-edit-test cycles and tokens per solved task over the same-model first-six aggregate. Lower-left indicates more efficient successful repair behavior; marker size encodes solve rate.

**Figure 4. Per-task outcome matrix for the first-six hard-smoke tasks.** Green cells indicate solved tasks, red cells indicate unsolved tasks, and NT marks the negative-transfer flag. This figure makes the subfamily-sensitive nature of procedural memory visible: Auto SKILL.md wins on black_193 and black_232 but fails with negative transfer on black_132.

**Figure S1. Model-mixed exploratory all-seven aggregate.** This supplementary figure includes pybughive_black_234, which was run with gpt-5.5 after gpt-5.3-codex became unavailable. Use it as a robustness/completion check, not as the primary same-model claim.

**Figure S2. pybughive_black_234 token cost by method.** All five methods solved the task. The task primarily separates methods by token cost rather than solve rate or cycles.
