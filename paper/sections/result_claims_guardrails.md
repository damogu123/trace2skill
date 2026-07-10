# Result Claims Guardrails

Use these guardrails when drafting the paper.

## Claims We Can Make

- Auto SKILL.md matches the best solve rate on the first-six same-model hard-smoke slice.
- Auto SKILL.md is the most token-efficient method among the five primary methods on the first-six same-model aggregate.
- Auto SKILL.md improves both solve rate and efficiency relative to length-matched Reflexion and no memory on the first-six aggregate.
- Auto SKILL.md reduces cycles and tokens relative to Reflexion memory on common-solved tasks.
- The evaluation protocol makes negative transfer visible; Auto SKILL.md has one negative-transfer failure.
- The evidence supports low-shot within-family transfer in a controlled `black` formatter-debugging slice.
- In a supplementary `gpt-5.5` Auto-vs-format-shuffled rerun, both methods solve 6/6 tasks; Auto SKILL.md uses fewer recorded cycles and fewer failed patches, while format-shuffled skill uses fewer tokens in aggregate.
- The format-shuffled control supports a process-behavior claim, not a strong solvability-necessity claim for SKILL.md structure.

## Claims To Avoid

- Do not claim SKILL.md universally outperforms Reflexion.
- Do not claim solve-rate dominance over Reflexion or generic checklist on the first-six aggregate; they are tied at 5/6.
- Do not present the first-seven result as the main evidence because it is model-mixed.
- Do not claim statistical significance from six same-model tasks.
- Do not claim general debugging-agent transfer beyond formatter-style Python tasks yet.
- Do not describe SKILL.md as merely a prompt. Call it a procedural memory artifact induced from trajectories.
- Do not claim that SKILL.md structure is necessary for solving the first-six tasks; the `gpt-5.5` format-shuffled control also solves 6/6.
- Do not claim Auto SKILL.md is uniformly more token-efficient than format-shuffled skill; it is higher in aggregate in the same-model `gpt-5.5` rerun because of `black_193`.
- Do not merge the original first-six `gpt-5.3-codex` five-method table and the later `gpt-5.5` Auto-vs-shuffled table as if they were one primary experiment.

## Strongest Reviewer-Facing Framing

The paper's primary contribution should be framed as an evaluation protocol for low-shot procedural skill transfer, with an initial controlled empirical study showing that trajectory-induced natural-language procedural memory can improve process efficiency over unstructured memory controls. The supplementary format-shuffled result should be framed as a boundary check: stronger models can solve with shuffled skill content, so the strongest structural claim is about measurable process behavior rather than guaranteed solvability.

## Best One-Sentence Result

On a six-task same-model PyBugHive Black hard-smoke slice, Auto SKILL.md tied the best solve rate at 5/6 while reducing tokens per solved task by 13.8% relative to Reflexion memory, 20.7% relative to a generic checklist, 24.4% relative to length-matched Reflexion, and 38.2% relative to no memory, with one explicit negative-transfer failure. A later same-model `gpt-5.5` structural-control rerun found that both Auto SKILL.md and format-shuffled skill solved 6/6 tasks; Auto SKILL.md used fewer recorded cycles and failed patches, while token efficiency was mixed.
