# Pilot External Mock Runner Report

## Status

This report validates `scripts/run_external_agent.py` with a mock external agent. It is not paper evidence.

## Command Pattern

```powershell
python scripts/run_external_agent.py manifests/pilot_external_mock.json --agent-command "python scripts/mock_agent_patch.py --repo-dir {repo_dir} --trace-path {trace_path} --preset local_empty_input_bug" --force --require-agent-zero
```

## Verified Behavior

- The runner expands external-agent command placeholders.
- The runner reproduces the initial failing test before agent execution.
- The mock agent edits only the isolated run checkout.
- The mock agent writes `agent_trace.json`.
- The runner captures a unified diff as `agent.patch`.
- The runner reruns the narrow and full test commands.
- The runner writes a valid `trajectory.schema.json` record.
- Metrics computation succeeds on the emitted trajectory.

## Artifacts

- Manifest: `manifests/pilot_external_mock.json`
- Prompt: `prompts/runs/pilot_external_mock/`
- Agent trace: `runs/pilot_external_mock/pilot_external_mock_local_empty_input_bug_no_memory_seed1/agent_trace.json`
- Patch: `runs/pilot_external_mock/pilot_external_mock_local_empty_input_bug_no_memory_seed1/agent.patch`
- Trajectory: `trajectories/pilot_external_mock/pilot_external_mock_local_empty_input_bug_no_memory_seed1.json`
- Metrics: `results/pilot_external_mock_metrics.json`

## Next Step

Replace `scripts/mock_agent_patch.py` with a real agent command that reads `{prompt_path}`, edits `{repo_dir}`, and writes `{trace_path}` according to `docs/agent_trace_contract.md`.
