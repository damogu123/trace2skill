# Post-Structural-Control Reviewer Report

Date: 2026-06-03

Scope reviewed: `paper/sections/method.md`, `paper/sections/results.md`, `paper/sections/discussion.md`, `paper/sections/limitations.md`, plus the updated claims guardrails and supplementary structural-control table.

## Editorial Summary

Decision if submitted as-is: **Workshop borderline-to-positive; main-conference major revision**.

The paper is now much safer than the previous version. The new format-shuffled control prevents an overclaim that the canonical three-section SKILL.md structure is necessary for solving the tasks. The manuscript also now frames the main contribution correctly as an evaluation protocol plus an initial controlled hard-smoke study of procedural memory.

The main remaining risk is not claim inflation but evidence scale. Six same-model tasks, one bug family, one executor style, and lightweight negative-transfer annotation are enough for a credible workshop paper or an early empirical paper, but not enough for a strong main-conference empirical claim unless the paper is explicitly positioned as protocol-first.

## Reviewer Configuration

- Editor-in-Chief: language-agent evaluation and reproducibility.
- Methodology reviewer: experimental design, baselines, metrics, statistical validity.
- Domain reviewer: agent memory, Reflexion-style memory, skill induction.
- Perspective reviewer: benchmark construction and practical debugging-agent usefulness.
- Devil's Advocate: prompt-engineering confounds and alternative explanations.

## Major Findings

### 1. Claim strength is mostly controlled now

The current Results, Discussion, and Limitations no longer claim universal solve-rate superiority. They correctly say that Auto SKILL.md ties the best solve rate in the primary five-method run and improves efficiency relative to unstructured memory and no-memory controls.

The strongest safe claim is:

> In a controlled six-task PyBugHive Black hard-smoke slice, trajectory-induced SKILL.md matches the best primary-baseline solve rate while improving process efficiency over unstructured memory controls; a supplementary format-shuffled rerun shows that structure affects process behavior but is not necessary for solvability under a stronger model.

Avoid any stronger version in the abstract or title.

### 2. The SKILL.md vs prompt-engineering objection is reduced but not eliminated

The Method now defines SKILL.md as an induced procedural memory artifact with an induction prompt, leakage constraints, task-family scope, and evaluation-time deployment. That is the right defense.

Reviewer risk remains because the artifact is still natural-language text inserted into context. To defend the distinction, the Introduction should explicitly define a procedural memory artifact by four properties:

1. It is induced from trajectories, not hand-authored for the held-out task.
2. It has an applicability scope and trigger conditions.
3. It encodes ordered diagnostic actions and failure modes.
4. It is evaluated by transfer, process efficiency, and negative transfer, not by prompt appeal.

The format-shuffled control should be introduced as a prompt-organization control, not as a failed baseline.

### 3. Baseline coverage is acceptable for a pilot, incomplete for a full paper

The five primary baselines are reasonable: no memory, generic checklist, Reflexion memory, length-matched Reflexion, and Auto SKILL.md. The added format-shuffled control is valuable, but because it is a later `gpt-5.5` two-method rerun, it cannot be merged into the primary table.

For main-conference strength, the highest-priority missing experiment is a full same-model rerun over all methods:

- no memory
- generic checklist
- Reflexion memory
- length-matched Reflexion
- format-shuffled SKILL.md
- Auto SKILL.md
- optional raw trajectory retrieval
- optional oracle skill

If compute is limited, the paper can still proceed as a workshop submission by clearly labeling the current result as a controlled hard-smoke study.

### 4. Process metrics are good, but cycle fidelity needs a caveat

Cycles per solved task, tokens per solved task, failed patches per run, repeated mistakes, and negative transfer are the right metrics for the research question. The paper is especially strong when it argues that solve rate alone hides process differences.

The main weakness is trace fidelity. The `black_193` supplementary Auto SKILL.md run is recorded as a single successful cycle but uses 258,676 tokens and substantial internal search. This suggests "recorded cycle" is not the same as all internal reasoning or tool-search effort.

Required wording:

> We report recorded diagnosis-edit-test cycles from the accepted trajectory schema; these cycles are complemented by token usage and failed-patch counts because a single recorded cycle can still contain substantial internal search.

This should appear in Method or Limitations.

### 5. Negative transfer is useful but should remain descriptive

The negative-transfer definition is operational enough for this stage, and the `black_132` case gives it a concrete role. The manuscript correctly notes that the later `gpt-5.5` rerun solves the same task, so negative transfer is model- and executor-dependent.

Do not claim a stable negative-transfer rate beyond this run. Keep it descriptive:

- "one explicit negative-transfer flag in the primary run"
- "the protocol exposes negative transfer"
- not "Auto SKILL.md has a negative-transfer rate of X in general"

For a full submission, add two annotators and Cohen's kappa.

### 6. Data source is defensible but narrow

PyBugHive Black is defensible because the tasks are reproducible, test-driven, and within-family. The narrowness actually helps the low-shot transfer question. But the paper must not imply broad software-engineering generality.

The current data supports:

- low-shot within-family transfer
- formatter/debugging tasks
- process-efficiency evaluation
- protocol feasibility

It does not yet support:

- cross-repository generalization
- general debugging-agent memory transfer
- statistical superiority
- model-independent skill effects

## Required Revisions Before Next Draft

1. Add an Introduction section that positions the contribution as protocol-first and defines procedural memory artifact explicitly.
2. Add a small experiment ledger table in the appendix separating primary and supplementary runs by model, task count, and method set.
3. Add the recorded-cycle caveat to Method or Limitations.
4. In Abstract and Introduction, avoid "outperforms Reflexion" unless immediately qualified as process-efficiency on a six-task hard-smoke slice.
5. Keep the format-shuffled result as a boundary check: structure changes process behavior, not necessary solvability.

## Recommended Next Experiment

If we continue running experiments, choose one of these:

1. **Best scientific value:** full same-model rerun of all primary methods plus format-shuffled on the first-six tasks under `gpt-5.5`.
2. **Best cost-benefit:** rerun only Reflexion, length-matched Reflexion, Auto SKILL.md, and format-shuffled under `gpt-5.5`.
3. **Best paper-writing progress:** stop experiments for now, add the experiment ledger, then draft Introduction and Abstract with cautious claims.

## Bottom Line

The paper is now viable as a controlled empirical study if the authors do not oversell it. The current evidence is not enough to prove that SKILL.md is generally better than Reflexion memory, but it is enough to motivate an evaluation protocol and show that trajectory-induced procedural memory can produce measurable process differences in low-shot debugging transfer.
