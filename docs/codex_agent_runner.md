# Codex CLI Agent Runner

This project can use Codex CLI as the external debugging agent backend through:

```text
scripts/run_codex_agent.py
```

The wrapper is called by `scripts/run_external_agent.py`. It:

- reads the run prompt at `{prompt_path}`;
- runs `codex exec` inside `{repo_dir}`;
- allows Codex to write artifacts under `{artifacts_dir}`;
- asks Codex to write `{trace_path}`;
- returns nonzero if Codex finishes without producing the trace.

## Preflight Example

First create a model-specific manifest:

```powershell
python scripts/set_manifest_model.py manifests/heldout_memory_baselines.json --output manifests/heldout_memory_baselines_codex.json --model gpt-5.3-codex --temperature 0
```

Then preflight the command shape:

```powershell
python scripts/preflight_experiment.py manifests/heldout_memory_baselines_codex.json --require-split heldout --require-real-model --require-agent-command --agent-command "python scripts/run_codex_agent.py --prompt-path {prompt_path} --repo-dir {repo_dir} --artifacts-dir {artifacts_dir} --trace-path {trace_path} --model gpt-5.3-codex" --output-json results/heldout_preflight_codex.json
```

## Execution Example

Run the held-out matrix:

```powershell
python scripts/run_external_agent.py manifests/heldout_memory_baselines_codex.json --agent-command "python scripts/run_codex_agent.py --prompt-path {prompt_path} --repo-dir {repo_dir} --artifacts-dir {artifacts_dir} --trace-path {trace_path} --model gpt-5.3-codex" --require-agent-zero --prepare --skip-existing-trajectories
```

For a first paid run, prefer `--limit 1`:

```powershell
python scripts/run_external_agent.py manifests/heldout_memory_baselines_codex.json --agent-command "python scripts/run_codex_agent.py --prompt-path {prompt_path} --repo-dir {repo_dir} --artifacts-dir {artifacts_dir} --trace-path {trace_path} --model gpt-5.3-codex" --force --require-agent-zero --prepare --limit 1
```

## After Execution

```powershell
python scripts/validate_trajectory.py trajectories/heldout_memory_baselines
python scripts/compute_metrics.py trajectories/heldout_memory_baselines --tasks tasks --group-by method,split,bug_family --output-json results/heldout_memory_baselines_metrics.json --output-csv results/heldout_memory_baselines_metrics.csv
```
