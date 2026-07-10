---
name: test-failure-triage
description: Use this skill for test-failure debugging tasks where a small set of failing tests or tracebacks gives enough evidence to localize, patch, and validate a behavioral bug.
---

# Test Failure Triage Skill

## Trigger Conditions

- Use this skill when a failing test exposes a localized behavioral mismatch rather than an installation, dependency, permissions, or flaky-test problem.
- Use it when the failure can be restated as a compact expected-vs-actual behavior involving an edge case, normalization rule, boundary condition, recursive structure, formatting rule, or time/date comparison.
- Use it when the traceback, assertion, or fixture points to a narrow call path that can be inspected before editing.
- Do not use it when the task requires broad redesign, missing external services, benchmark setup repair, or changes whose correctness cannot be checked by the available tests.
- Do not use it when the visible failing test is only a symptom of widespread state corruption; first isolate the smaller invariant.

## Debugging Procedure

1. Reproduce the exact failing command before editing. If the environment requires a wrapper, use that wrapper consistently for every test rerun.
2. Compress the failure into one sentence: the input shape, the expected behavior, the observed behavior, and the boundary that makes this case special.
3. Inspect the nearest test, fixture, or traceback frame only to identify the behavioral invariant. Do not copy literals from the test into the patch.
4. Open the smallest implementation path that owns the invariant. Prefer the branch, normalization point, lookup table, comparison, or recursive merge step closest to the failing behavior.
5. Compare the failing case with neighboring supported cases. Ask which general category is missing or treated as the wrong category.
6. Make one minimal general patch that changes the invariant, not the single observed example. Avoid unrelated cleanup, broad refactors, and edits outside the direct call path.
7. Rerun the narrow failing test immediately. If it still fails, classify the failure before editing again: wrong code path, incomplete boundary, over-specific patch, or unexpected side effect.
8. Once the narrow test passes, run the broader available test command to check for negative transfer. Record any repeated mistake or invalid test command in the trajectory.

## Failure Modes

- Overfitting to a visible literal, fixture value, or assertion string instead of fixing the underlying rule.
- Editing a distant module before confirming the direct owner of the failed behavior.
- Treating a boundary case as a one-off special case when it belongs to a broader category.
- Repeating the same patch shape after a failed rerun instead of returning to the failure log and inspected invariant.
- Running an invalid or inconsistent test command, then misreading harness failure as code failure.
- Passing the narrow test while breaking broader behavior; always run the full command when available.
