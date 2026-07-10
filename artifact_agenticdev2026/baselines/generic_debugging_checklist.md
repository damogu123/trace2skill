# Generic Debugging Checklist Baseline

## Purpose

This checklist is a non-induced human-written debugging aid. It controls for the possibility that any structured checklist improves agent debugging, regardless of whether the content was induced from prior trajectories.

Use this baseline exactly as written across all tasks in the MVP unless the experimental protocol explicitly defines a versioned update.

## Checklist

1. Read the failing test name, assertion, and traceback before inspecting implementation code.
2. Identify the smallest behavior implied by the failing test.
3. Locate the implementation path most directly connected to that behavior.
4. Inspect existing nearby tests to infer expected behavior and edge cases.
5. Make the smallest code change that addresses the observed failure.
6. Rerun the narrow failing test after each patch.
7. If the narrow test passes, run the relevant broader test file or full test command when available.
8. Avoid hard-coding values that only satisfy the visible assertion.
9. Avoid modifying unrelated modules unless the traceback or call path justifies it.
10. If repeated patches fail, revisit the original failure log instead of continuing the same fix pattern.

## Out-of-Scope Signals

This checklist is not specialized for:

- Dependency installation failures.
- Missing optional packages.
- CI-only configuration failures.
- Flaky timing or ordering failures.
- External API or network failures.
- Large architectural refactors.

## Reporting

When this baseline is used, record:

```json
{
  "baseline": "generic_debugging_checklist",
  "version": "v1",
  "word_count": 165
}
```

