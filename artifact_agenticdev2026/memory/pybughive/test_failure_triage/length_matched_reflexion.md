# Reflexion Memory

## Reflections

- I should begin with the failing test output and identify the smallest behavior it specifies.
- I should inspect the code path that directly owns the failed behavior before changing broader modules.
- I should prefer a minimal general fix and rerun the narrow failing test after each edit.
- I observed: Star-unpacking in <path> context was treated like unary operator spacing, introducing an extra space after '*'.
- I observed: Recursive config merge assumed nested keys already exist in defaults and only handled plain dict, causing KeyError for user-only nested mappings like <identifier>.project.
- I observed: Timezone-aware explicit task times were compared against `<code>` in a different <path> context, causing wrong next-slot selection near <path> day boundaries.
- I should remember this patch pattern: Added `<code>` to `<code>` so starred unpacking in expression lists is recognized as unpacking and formatted without space after `<code>`.
- I should remember this patch pattern: Updated <identifier> to treat mapping-like objects robustly and safely recurse with an empty mapping when a nested default key is missing or non-mapping.
- I should remember this patch pattern: In `<code>`, converted `<code>` into each scheduled time's timezone before computing date and comparing, ensuring correct next explicit time selection across timezone boundaries.
- I should avoid: Initial narrow test attempt used `<code>`, which is invalid for this runner.

## Additional Length-Matching Reflections

- I should keep checking whether the current edit directly follows from the failure evidence.
- I should avoid adding unrelated abstractions when a small behavioral fix is enough.
- I should stop and reread the failure log when repeated attempts do not change the result.
- I should separate diagnosis, edit, and test rerun so the run log remains auditable.
- I should keep checking whether the current edit directly follows from the failure evidence.
- I should restate the expected behavior before deciding which file to open.
- I should compare the failing case with nearby supported cases before adding a branch.
- I should prefer one small edit that changes the rule rather than several speculative edits.
- I should treat a passing narrow test as incomplete evidence until a broader test also passes.
- I should notice when a test command failure is caused by the runner rather than by the code.
- I should write down repeated mistakes so the next attempt does not spend tokens on the same path.
- I should avoid copying exact literals from a test into production logic.
