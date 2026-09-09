# Reproduction Notes

## Validation

The artifact is designed so the schema validators work from this folder without
additional path configuration:

```powershell
py scripts\validate_task.py tasks
py scripts\validate_trajectory.py trajectories
py scripts\validate_run_manifest.py manifests
py scripts\validate_trajectory.py trajectory_sets\primary_first6
py scripts\validate_trajectory.py trajectory_sets\structural_control_gpt55
py scripts\validate_artifact_inventory.py .
```

## Metrics

Primary first-six hard-smoke result:

```powershell
py scripts\compute_metrics.py trajectory_sets\primary_first6 --tasks task_sets\primary_first6 --group-by method --output-csv results\recomputed_primary_first6_by_method.csv --output-json results\recomputed_primary_first6_by_method.json
```

Structural-control result:

```powershell
py scripts\compute_metrics.py trajectory_sets\structural_control_gpt55 --tasks task_sets\primary_first6 --group-by method --output-csv results\recomputed_structural_control_gpt55_by_method.csv --output-json results\recomputed_structural_control_gpt55_by_method.json
```

Paper-ready tables and figures can be regenerated with:

```powershell
py scripts\make_paper_results.py
```

That script uses the precomputed CSV files in `results/` and writes to
`paper/tables/` and `paper/figures/`.

## Rerunning Agents

The original agent executions used isolated workspaces, WSL-compatible Python
environments for PyBugHive tasks, and an external-agent contract implemented by
`scripts/run_external_agent.py` and `scripts/run_codex_agent.py`.

The artifact preserves manifests and prompts for auditability, but it is not
intended to replay the exact paid/interactive agent runs without configuring an
equivalent model endpoint and local benchmark environment.
