# External Agent Runner Contract

This project treats an external debugging agent as a command that receives a run prompt and edits one isolated checkout.

The harness is responsible for:

- reproducing the initial failing test;
- invoking the external agent command;
- collecting the final patch diff;
- rerunning the narrow and full tests;
- converting the result into `trajectory.schema.json`.

The external agent is responsible for:

- reading the prompt pack for its run;
- editing only the provided checkout;
- optionally writing `agent_trace.json` with diagnosis-edit-test cycle metadata.

## Command Placeholders

`scripts/run_external_agent.py` expands these placeholders inside `--agent-command`:

- `{prompt_path}`
- `{repo_dir}`
- `{artifacts_dir}`
- `{trace_path}`
- `{task_path}`
- `{run_id}`
- `{method}`

The same values are also exposed as environment variables:

- `RUN_ID`
- `METHOD`
- `PROMPT_PATH`
- `REPO_DIR`
- `ARTIFACTS_DIR`
- `TRACE_PATH`
- `TASK_PATH`

## Minimal Trace

The preferred trace path is:

```text
{artifacts_dir}/agent_trace.json
```

It should validate against `schemas/agent_trace.schema.json`.

```json
{
  "llm_turns": 8,
  "tool_calls": 14,
  "input_tokens": 12000,
  "output_tokens": 1800,
  "cycles": [
    {
      "cycle_id": 1,
      "diagnosis": "The failing assertion suggests a missing boundary-case branch.",
      "file_inspections": [
        {
          "path": "src/module.py",
          "reason": "Owns the behavior exercised by the failing test."
        }
      ],
      "modified_files": ["src/module.py"],
      "patch_summary": "Added a general boundary-case branch.",
      "test_command": "pytest tests/test_module.py::test_case -q",
      "test_passed": true,
      "test_log_path": "runs/example/cycle_1.log",
      "mistakes": []
    }
  ],
  "negative_transfer": {
    "detected": false,
    "category": null,
    "reason": null
  }
}
```

If no trace is emitted, the runner can be called with `--allow-missing-trace`, but that should only be used for smoke tests. Real experiments should require trace output or model usage logs.
