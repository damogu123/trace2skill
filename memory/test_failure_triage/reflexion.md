# Reflexion Memory

## Reflections

- I should begin with the failing test output and identify the smallest behavior it specifies.
- I should inspect the code path that directly owns the failed behavior before changing broader modules.
- I should prefer a minimal general fix and rerun the narrow failing test after each edit.
- I observed: The failure indicates a missing empty-input branch.
- I should remember this patch pattern: Return an empty list for whitespace-only input.
