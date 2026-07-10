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

---

# Induction Input Package

The following trajectories are redacted summaries. Do not infer or recreate hidden file, function, test, repository, or patch details.

## Package Metadata

```json
{
  "trajectory_count": 3,
  "selection_seed": 1,
  "source_files": [
    "trajectory_1.json",
    "trajectory_2.json",
    "trajectory_3.json"
  ],
  "redaction": {
    "paths": "<path>",
    "python_files": "<file>",
    "test_names": "<test>",
    "inline_code": "`<code>`",
    "identifiers": "<identifier>",
    "issue_references": "issue <number>",
    "project_terms": "<project>"
  }
}
```

## Redacted Trajectory Summaries

```json
[
  {
    "trajectory_index": 1,
    "method": "no_memory",
    "solved": true,
    "cycles_used": 1,
    "failed_patch_count": 0,
    "negative_transfer": false,
    "cycles": [
      {
        "cycle_id": 1,
        "diagnosis": "Star-unpacking in <path> context was treated like unary operator spacing, introducing an extra space after '*'.",
        "file_inspection_reasons": [
          "Confirm failing fixture and exact unpacking example `<code>`.",
          "Inspect whitespace and <path> classification logic controlling spaces after `<code>`."
        ],
        "modified_file_count": 1,
        "patch_summary": "Added `<code>` to `<code>` so starred unpacking in expression lists is recognized as unpacking and formatted without space after `<code>`.",
        "test_passed": true,
        "mistakes": [
          {
            "type": "invalid_test_command",
            "description": "Initial narrow test attempt used `<code>`, which is invalid for this runner."
          }
        ]
      }
    ]
  },
  {
    "trajectory_index": 2,
    "method": "no_memory",
    "solved": true,
    "cycles_used": 1,
    "failed_patch_count": 0,
    "negative_transfer": false,
    "cycles": [
      {
        "cycle_id": 1,
        "diagnosis": "Recursive config merge assumed nested keys already exist in defaults and only handled plain dict, causing KeyError for user-only nested mappings like <identifier>.",
        "file_inspection_reasons": [
          "Failure traceback points to <identifier> recursion and <project> YAML parsing path.",
          "Validate expected merged structure and failing scenario from <identifier>.",
          "Confirm related user-config behaviors and regression coverage.",
          "Inspect nested YAML shape that triggers recursion for new key under <identifier>.",
          "Check partial override behavior remains intact.",
          "Confirm invalid fixture context for parser error handling was unaffected."
        ],
        "modified_file_count": 1,
        "patch_summary": "Updated <identifier> to treat mapping-like objects robustly and safely recurse with an empty mapping when a nested default key is missing or non-mapping.",
        "test_passed": true,
        "mistakes": []
      }
    ]
  },
  {
    "trajectory_index": 3,
    "method": "no_memory",
    "solved": true,
    "cycles_used": 1,
    "failed_patch_count": 0,
    "negative_transfer": false,
    "cycles": [
      {
        "cycle_id": 1,
        "diagnosis": "Timezone-aware explicit task times were compared against `<code>` in a different <path> context, causing wrong next-slot selection near <path> day boundaries.",
        "file_inspection_reasons": [
          "Inspect failing regression expectations and input construction for issue <number>.",
          "Inspect `<code>` and `<code>` scheduling logic."
        ],
        "modified_file_count": 1,
        "patch_summary": "In `<code>`, converted `<code>` into each scheduled time's timezone before computing date and comparing, ensuring correct next explicit time selection across timezone boundaries.",
        "test_passed": true,
        "mistakes": []
      }
    ]
  }
]
```
