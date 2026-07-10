# Oracle SKILL.md Annotation Guide

## Purpose

The oracle skill is a human-authored upper bound. It answers how far the automatic induction pipeline is from a careful human-written procedural skill produced from the same evidence.

## Annotator Inputs

Annotators may inspect:

- The same K training trajectories used by Auto-SKILL.md induction.
- Failing test summaries.
- Diagnosis-edit-test cycles.
- Patch summaries.
- Test rerun outcomes.
- Repeated mistake summaries.
- Final task outcomes.
- Bug family label.

Annotators must not inspect:

- Held-out tasks.
- Adversarial tasks.
- Evaluation results.
- Baseline outputs.
- Full ground-truth patch code.
- Auto-SKILL.md outputs for the same K trajectories.

## Required Output

Annotators must write:

```markdown
---
name: test-failure-triage-oracle
description: Human-authored procedural skill for test-failure triage debugging.
---

# Test Failure Triage Skill

## Trigger Conditions

...

## Debugging Procedure

...

## Failure Modes

...
```

## Writing Rules

1. Use the same three-section structure as Auto-SKILL.md.
2. Keep the skill under 700 words.
3. Do not include repository names.
4. Do not include file names.
5. Do not include function, method, class, or test names.
6. Do not include literal code or patch snippets.
7. Generalize across trajectories rather than summarizing them one by one.
8. Include when not to use the skill.
9. Include failure modes likely to cause negative transfer.

## Fairness Controls

- Oracle and Auto-SKILL.md use the same K trajectories.
- Oracle and Auto-SKILL.md share the same word limit.
- Oracle and Auto-SKILL.md share the same required sections.
- Each oracle skill is written by one annotator and reviewed by another annotator for leakage.

## Metadata Record

Save one metadata file per oracle skill:

```json
{
  "oracle_skill_id": "oracle_3shot_seed1",
  "annotator_id": "A1",
  "reviewer_id": "A2",
  "training_task_ids": ["task_001", "task_002", "task_003"],
  "word_count": 512,
  "leakage_check_passed": true,
  "leakage_notes": null
}
```
