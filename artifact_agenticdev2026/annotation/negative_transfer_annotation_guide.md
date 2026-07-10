# Negative Transfer Annotation Guide

## Purpose

This guide defines when a procedural skill harms a debugging agent relative to control conditions. The goal is to distinguish harmless failure from skill-induced failure.

## Categories

### 1. Performance Negative Transfer

Mark `performance` when Auto-SKILL.md causes worse measurable performance.

Positive criteria:

- Auto-SKILL.md is unsolved while No Memory or Reflexion solves the same task.
- Auto-SKILL.md solves the task but uses at least 2 more diagnosis-edit-test cycles than Reflexion.
- Auto-SKILL.md uses at least 30% more total tokens than Reflexion without improving solve rate.
- Auto-SKILL.md breaks existing tests when the comparison method does not.

### 2. Behavioral Negative Transfer

Mark `behavioral` when the agent follows a skill procedure that is visibly inappropriate for the task.

Positive criteria:

- The task is adversarial or non-applicable, but the agent still follows the skill.
- The agent modifies unrelated implementation paths because the skill suggests an overgeneral procedure.
- The agent ignores a more direct root-cause signal in the failure log.
- The agent continues the same skill-driven path after test feedback shows it is ineffective.

### 3. Self-Contradictory Negative Transfer

Mark `self_contradictory` when the agent violates the skill's own failure-mode warnings.

Positive criteria:

- The skill warns against overfitting one failing test, but the agent does so.
- The skill warns against skipping broader validation, but the agent submits after only a narrow test.
- The skill warns that dependency, configuration, fixture, or flaky-test failures are out of scope, but the agent still applies the skill.
- The skill warns against patching before inspecting relevant code, but the agent patches without sufficient inspection.

## Boundary Cases

- If Auto-SKILL.md fails but all baselines fail, do not mark negative transfer.
- If Auto-SKILL.md uses one extra cycle but fewer tokens and still solves, do not automatically mark negative transfer.
- If task metadata is ambiguous, mark `uncertain`.
- If the agent never mentions the skill but behaves according to an inappropriate skill procedure, behavioral negative transfer may still apply.
- If multiple categories apply, choose the most direct cause and mention secondary categories in notes.

## Annotation Inputs

Annotators receive:

- Task metadata.
- Auto-SKILL.md used in the run.
- Auto-SKILL.md trajectory log.
- Baseline summary for the same task.
- Test results and patch summaries.

Annotators do not need access to raw model hidden reasoning. Use logged actions and textual outputs only.

## Annotation Procedure

1. Two annotators independently label each candidate run.
2. Each annotator records:
   - `negative_transfer`: yes / no / uncertain
   - `category`: performance / behavioral / self_contradictory / none
   - evidence span or log pointer
   - confidence: low / medium / high
3. Compute Cohen's kappa on yes/no labels after excluding `uncertain`.
4. Resolve disagreements through adjudication.
5. Report `uncertain` cases separately in the appendix.

## CSV Format

```csv
run_id,task_id,annotator,negative_transfer,category,evidence,confidence
```

## Main Reporting

Report:

- Negative transfer rate by method.
- Negative transfer rate by bug family.
- Category breakdown.
- Cohen's kappa for annotation agreement.
- Representative examples for each category.
