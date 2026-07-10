# Format-Shuffled SKILL.md Baseline

## Purpose

The format-shuffled baseline tests whether `Trigger Conditions`, `Debugging Procedure`, and `Failure Modes` structure contributes value beyond the same natural-language content.

This is a prompt-engineering control. It preserves the information content of `Auto-SKILL.md` while destroying its procedural organization.

## Input

- One generated `Auto-SKILL.md`.

## Generation Rules

1. Extract all bullet points, numbered steps, and standalone guidance sentences from `Auto-SKILL.md`.
2. Remove the section headers:
   - `Trigger Conditions`
   - `Debugging Procedure`
   - `Failure Modes`
3. Preserve the original text of each extracted sentence or bullet.
4. Shuffle the extracted units with a fixed random seed.
5. Do not add information.
6. Do not delete information except formatting-only text.
7. Do not rewrite the semantic content.
8. Output a single `Debugging Notes` block.
9. Keep token length within +/-10% of the original `Auto-SKILL.md`.
10. If token length differs by more than 10%, adjust only by restoring or removing formatting-neutral connective text.

## Output Format

```markdown
# Debugging Notes

The following notes were derived from prior debugging experience.

- [shuffled sentence 1]
- [shuffled sentence 2]
- [shuffled sentence 3]
```

## Fairness Constraints

- Use the same source skill as `Auto-SKILL.md`.
- Preserve information content while breaking structure.
- Use the same model and context budget as other baselines during evaluation.
- Do not include labels such as "trigger", "procedure", or "failure mode" in the output.

## Reporting

For each shuffled baseline, record:

```json
{
  "source_skill_id": "skill_3shot_seed1",
  "shuffle_seed": 1,
  "source_token_count": 620,
  "shuffled_token_count": 604,
  "token_delta_percent": -2.58
}
```
