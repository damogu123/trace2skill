# Repeated Mistake Taxonomy

## Purpose

This taxonomy standardizes how repeated mistakes are labeled in debugging trajectories. It supports the `repeated_mistake_rate` metric and helps distinguish ordinary failure from skill-induced negative transfer.

## General Rule

Mark a repeated mistake when the same mistake type appears in at least two diagnosis-edit-test cycles within one run, or when a later cycle repeats a failure mode already observed in the task's prior trajectory.

## Mistake Types

### `overfit_to_single_test`

The agent patches only the visible failing assertion instead of the underlying behavior.

Signals:

- Hard-coded expected value.
- Handles one input literal but not the input class.
- Narrow test passes while nearby related tests fail.

### `ignored_failure_log`

The agent acts without using the most diagnostic information in the failure log.

Signals:

- Patch targets a file unrelated to the traceback.
- Diagnosis contradicts the exception type.
- Later cycles repeat a path already contradicted by test output.

### `premature_patch`

The agent edits before inspecting enough relevant implementation or test context.

Signals:

- First patch occurs before reading the function under test.
- Patch summary admits uncertainty about root cause.
- Patch changes unrelated code before tracing the call path.

### `irrelevant_file_churn`

The agent repeatedly modifies files not on the failure path.

Signals:

- Multiple cycles touch unrelated modules.
- Modified files are not imported by the failing test path.
- Reverting the changes does not affect the failure.

### `narrow_validation`

The agent stops after passing a narrow test when broader validation is available and relevant.

Signals:

- Does not run the full test command after the target test passes.
- Breaks existing tests that would have been caught by broader validation.
- Ignores project-specific test guidance.

### `same_patch_pattern_retry`

The agent repeats substantially the same patch idea after it has already failed.

Signals:

- Repeated guard clauses for the same symptom.
- Repeated type conversion attempts with no new evidence.
- Repeated fallback return edits after test output rejects the behavior.

### `skill_misapplication`

The agent applies an induced skill even when trigger conditions are absent or out-of-scope signals are present.

Signals:

- Treats dependency/configuration failure as logic bug.
- Treats fixture setup failure as implementation behavior.
- Applies test-failure triage flow to flaky timing failure.

### `self_contradictory_skill_use`

The agent violates a failure mode stated in the skill it received.

Signals:

- Skill warns against hard-coding; agent hard-codes.
- Skill warns against skipping broad tests; agent skips broad tests.
- Skill warns not to use on environment failures; agent modifies business logic anyway.

## Annotation Format

Record each mistake as:

```json
{
  "type": "overfit_to_single_test",
  "description": "The agent patched only the literal empty-string case after the first test failure and repeated the same pattern in cycle 2.",
  "cycle_ids": [1, 2],
  "evidence": "runs/run_001/cycle_2.log"
}
```

## Boundary Cases

- A single failed patch is not a repeated mistake unless the same pattern appears again.
- A repeated file inspection is not a mistake unless it delays progress or ignores new evidence.
- If the task is genuinely ambiguous, mark the mistake as `uncertain` in notes and exclude it from the main repeated-mistake count.

