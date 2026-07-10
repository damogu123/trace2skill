# Raw Trajectory Retrieval

Use these redacted prior trajectory summaries as retrieved episodic memory. Do not infer hidden file, function, test, repository, or patch details.

## Retrieval Metadata

```json
{
  "bug_family": "test_failure_triage",
  "trajectory_count": 1,
  "selection_seed": 1,
  "redaction": {
    "paths": "<path>",
    "python_files": "<file>",
    "test_names": "<test>",
    "inline_code": "`<code>`"
  }
}
```

## Retrieved Trajectories

```json
[
  {
    "trajectory_index": 1,
    "source_file": "<path>",
    "method": "auto_skill",
    "solved": true,
    "cycles_used": 1,
    "failed_patch_count": 0,
    "negative_transfer": false,
    "cycles": [
      {
        "cycle_id": 1,
        "diagnosis": "The failure indicates a missing empty-input branch.",
        "inspection_reasons": [
          "Likely implementation of <identifier> behavior."
        ],
        "modified_file_count": 1,
        "patch_summary": "Return an empty list for whitespace-only input.",
        "test_passed": true,
        "mistakes": []
      }
    ]
  }
]
```
