# SKILL.md Induction Prompt v2

You are inducing a reusable natural-language procedural debugging skill from prior agent trajectories.

## Input

You will receive K debugging trajectories from the same bug family. Each trajectory may include:

- Failing test signal
- Diagnosis-edit-test cycles
- Inspected files
- Patch attempts
- Test reruns
- Final outcome
- Repeated mistakes
- Failure modes

## Goal

Produce a concise `SKILL.md` that helps a future coding agent solve new held-out tasks from the same bug family.

The skill is a procedural memory artifact. It is not a case summary, not a patch summary, and not a generic debugging prompt.

## Hard Constraints

1. Do not copy or mention specific repository names.
2. Do not copy or mention specific file names.
3. Do not copy or mention specific function, class, method, or test names.
4. Do not copy literal patches or code snippets.
5. Do not reveal ground-truth patches.
6. Abstract across trajectories. Preserve only reusable procedural patterns.
7. Include conditions for when this skill should not be used.
8. Include failure modes that would cause negative transfer.
9. Keep the final skill under 700 words.
10. Prefer specific procedural guidance over generic debugging advice.

## Output Format

Output exactly this structure:

```markdown
---
name: test-failure-triage
description: Use this skill for test-failure debugging tasks where failing tests provide enough evidence to guide diagnosis, patching, and validation.
---

# Test Failure Triage Skill

## Trigger Conditions

- Use this skill when ...
- Do not use this skill when ...

## Debugging Procedure

1. ...
2. ...
3. ...

## Failure Modes

- ...
- ...
- ...
```

## Quality Bar

A strong induced skill should:

- Identify reusable signals in failing tests.
- Tell the agent what to inspect before editing.
- Encourage minimal patches and test reruns.
- Warn against overfitting a single failing assertion.
- Warn against using the skill on dependency, configuration, fixture, or flaky-test failures.
- Reduce unnecessary diagnosis-edit-test cycles on held-out tasks.
