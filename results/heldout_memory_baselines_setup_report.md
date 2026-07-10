# Held-Out Memory Baselines Setup Report

## Status

The held-out within-family pilot setup is ready for a real external agent runner.

## Held-Out Tasks

All held-out tasks use bug family `test_failure_triage` and split `heldout`.

- `local_empty_average_bug`
- `local_missing_timeout_bug`
- `local_whitespace_title_bug`

Each task has been reference-checked:

- install/setup command returns 0;
- the narrow failing test fails before the reference patch;
- the reference patch applies cleanly;
- the narrow failing test passes after the reference patch.

## Baseline Matrix

Manifest:

```text
manifests/heldout_memory_baselines.json
```

The runnable matrix contains 21 runs:

- 3 held-out tasks
- 7 non-oracle conditions
- 1 seed

Conditions:

- no_memory
- generic_checklist
- reflexion
- length_matched_reflexion
- raw_trajectory_retrieval
- format_shuffled_skill
- auto_skill

Oracle is intentionally excluded from the runnable manifest because `oracle_skill.md` has not been human-authored yet.

## Generated Artifacts

- Prompt packs: `prompts/runs/heldout_memory_baselines/`
- Prepared workspaces: `workspaces/runs/heldout_memory_baselines/`
- Expected trajectory output: `trajectories/heldout_memory_baselines/`

## Verification

- `python scripts/validate_task.py tasks` passes.
- `python scripts/validate_run_manifest.py manifests/heldout_memory_baselines.json` passes.
- `python scripts/build_run_prompts.py manifests/heldout_memory_baselines.json` wrote 21 prompt packs.
- `python scripts/prepare_runs.py manifests/heldout_memory_baselines.json --force` prepared 21 isolated workspaces.
- Every prepared run has `install_returncode = 0` and `initial_failure_reproduced = true`.

## Next Step

Run:

```powershell
python scripts/run_external_agent.py manifests/heldout_memory_baselines.json --agent-command "<real agent command using {prompt_path} {repo_dir} {trace_path}>" --force --require-agent-zero
```

The real agent command must read `{prompt_path}`, modify `{repo_dir}`, and write `{trace_path}` according to `docs/agent_trace_contract.md`.
