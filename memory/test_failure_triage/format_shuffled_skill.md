# Debugging Notes

The following notes were derived from prior debugging experience.

- Likely implementation of <identifier> behavior.
- Do not edit unrelated modules unless the traceback or direct call path justifies the change.
- A failing test points to a narrow behavioral edge case rather than an installation or infrastructure error.
- Return an empty list for whitespace-only input.
- Add the smallest general branch or normalization step that handles the missing case without hard-coding the visible assertion.
- Rerun the narrow failing test after each patch; when it passes, run the broader test command if available.
- Start from the failing assertion and restate the smallest expected behavior before opening implementation files.
- Do not keep retrying the same patch shape after a failed test rerun; return to the original failure log.
- Inspect the implementation path most directly connected to the observed behavior, then compare it with nearby tests or call sites.
- The assertion or traceback implies that one input shape is not handled consistently with nearby expected behavior.
- Do not overfit to a single visible literal from the failing assertion.
- The failure indicates a missing empty-input branch.
