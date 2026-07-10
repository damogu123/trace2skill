# PyBugHive Prompt and Auto-SKILL Quality Audit

Date: 2026-05-25

## Scope

- Induction prompt: `prompts/induction/pybughive_test_failure_triage_k3_seed1.md`
- Auto-SKILL: `memory/pybughive/test_failure_triage/auto_skill.md`
- Format control: `memory/pybughive/test_failure_triage/format_shuffled_skill.md`
- Redaction script: `scripts/induce_skill.py`

## Auto-SKILL Status

Decision: freeze `auto_skill.md` as v1 for the current PyBugHive held-out run.

Rationale:

- The skill uses valid `SKILL.md` frontmatter with only `name` and `description`.
- The body is organized as procedural memory: trigger conditions, debugging procedure, and failure modes.
- It avoids concrete repository, file, function, test, and patch details.
- It is already part of the completed held-out runs, so editing it mid-experiment would break comparability.

Any improved version should be saved as a new condition such as `auto_skill_v2` and evaluated from scratch across all held-out tasks.

## Induction Prompt Status

Decision: regenerate the induction prompt after strengthening redaction.

Changes made:

- Added redaction for dotted identifiers such as object paths.
- Added redaction for snake-case identifiers such as function-like names.
- Added redaction for issue, bug, and ticket number references.
- Added a project-term redaction slot for known project/package leakage in the current training summaries.
- Updated prompt metadata to document the additional redaction placeholders.

Integrity note:

- Regenerating the induction prompt does not alter `auto_skill.md`.
- Existing held-out results remain tied to frozen `auto_skill.md` v1.
- The regenerated prompt should be used for future documentation, re-induction, or v2 experiments.

## Leakage Check

Searched for repository names, PyBugHive task names, concrete function names, specific issue numbers, Python filenames, Claude-only fields, and Claude-only commands across the induction prompt and frozen Auto-SKILL.

Result:

- No concrete repository, function, file, issue, or Claude-only command leakage remained.
- Remaining `test_` matches are schema/control fields such as `test_names`, `test_passed`, and `invalid_test_command`, not hidden task identifiers.

## Baseline Control Check

`format_shuffled_skill.md` preserves the same general content as Auto-SKILL but removes the ordered Trigger Conditions / Debugging Procedure / Failure Modes structure.

This is suitable as a prompt-engineering control because it tests whether the procedural organization, not only wording or token budget, drives transfer.

## Recommendation

Continue the held-out baseline run with the frozen memory artifacts currently under `memory/pybughive/test_failure_triage/`.

Do not edit these files during the current run:

- `auto_skill.md`
- `reflexion.md`
- `length_matched_reflexion.md`
- `raw_trajectory_retrieval.md`
- `format_shuffled_skill.md`
- `generic_debugging_checklist.md`

If any artifact changes, create a new manifest and rerun all methods for all held-out tasks.
