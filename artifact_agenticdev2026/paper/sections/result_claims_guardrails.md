# Result Claims Guardrails

Use these guardrails when drafting the paper.

## Claims We Can Make

- Auto SKILL.md matches the best solve rate on the first-six same-model hard-smoke slice.
- Auto SKILL.md has the lowest solve-conditional mean and median token use among the five primary methods in this single-execution slice.
- Task-level paired intervals favor Auto SKILL.md over length-matched Reflexion and no memory on common-solved process costs.
- Against Reflexion memory, the paired token interval favors Auto SKILL.md while the cycle interval includes zero.
- Auto SKILL.md and the generic checklist tie on solve rate and cycles; the paired checklist token interval includes zero.
- The evaluation protocol makes negative transfer visible; Auto SKILL.md has one negative-transfer failure.
- The evidence supports low-shot within-family transfer in a controlled `black` formatter-debugging slice.
- In a supplementary `gpt-5.5` Auto-vs-format-shuffled rerun, both methods solve 6/6 tasks; Auto SKILL.md uses fewer recorded cycles and fewer failed patches, while format-shuffled skill uses fewer tokens in aggregate.
- The structural-control token medians are nearly identical, and excluding `black_193` reverses the mean ordering.
- The format-shuffled control supports a process-behavior claim, not a strong solvability-necessity claim for SKILL.md structure.

## Claims To Avoid

- Do not claim SKILL.md universally outperforms Reflexion.
- Do not claim solve-rate dominance over Reflexion or generic checklist on the first-six aggregate; they are tied at 5/6.
- Do not present the first-seven result as the main evidence because it is model-mixed.
- Do not claim statistical significance from six same-model tasks.
- Do not describe Wilson or task-bootstrap intervals as run-to-run uncertainty; they describe variation across selected tasks only.
- Do not claim that trajectory induction learned knowledge beyond a competent human checklist.
- Do not describe the checklist token difference as stable; its paired bootstrap interval crosses zero.
- Do not claim general debugging-agent transfer beyond formatter-style Python tasks yet.
- Do not describe SKILL.md as merely a prompt. Call it a procedural memory artifact induced from trajectories.
- Do not claim that SKILL.md structure is necessary for solving the first-six tasks; the `gpt-5.5` format-shuffled control also solves 6/6.
- Do not claim Auto SKILL.md is uniformly more token-efficient than format-shuffled skill; it is higher in aggregate in the same-model `gpt-5.5` rerun because of `black_193`.
- Do not merge the original first-six `gpt-5.3-codex` five-method table and the later `gpt-5.5` Auto-vs-shuffled table as if they were one primary experiment.

## Strongest Reviewer-Facing Framing

The paper's primary contribution should be framed as an evaluation protocol for low-shot procedural skill transfer, with a single-execution pilot showing initial task-level process differences against reflection controls. The generic checklist remains an unresolved strong baseline. The supplementary format-shuffled result is a boundary check: stronger models can solve with shuffled skill content, so the structural claim concerns observable process behavior rather than guaranteed solvability.

## Best One-Sentence Result

In a six-task, single-execution PyBugHive Black pilot, Auto SKILL.md tied the best observed solve rate at 5/6; paired task-level analyses favored it over reflection controls on process cost but did not establish a stable advantage over a generic checklist, and one explicit negative-transfer failure plus an outlier-sensitive structural control exposed the limits of aggregate-only evaluation.
