# Reflexion Memory

## Reflections

- I should begin with the failing test output and identify the smallest behavior it specifies.
- I should inspect the code path that directly owns the failed behavior before changing broader modules.
- I should prefer a minimal general fix and rerun the narrow failing test after each edit.
- I observed: The failure indicates a missing empty-input branch.
- I should remember this patch pattern: Return an empty list for whitespace-only input.

## Additional Length-Matching Reflections

- I should keep checking whether the current edit directly follows from the failure evidence.
- I should avoid adding unrelated abstractions when a small behavioral fix is enough.
- I should stop and reread the failure log when repeated attempts do not change the result.
- I should separate diagnosis, edit, and test rerun so the run log remains auditable.
- I should keep checking whether the current edit directly follows from the failure evidence.
- I should avoid adding unrelated abstractions when a small behavioral fix is enough.
- I should stop and reread the failure log when repeated attempts do not change the result.
