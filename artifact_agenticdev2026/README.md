# AgenticDev 2026 Artifact Package

This folder is a curated, GitHub-ready artifact for the paper:

**Evaluating Low-Shot Procedural Skill Transfer in Language-Agent Debugging**

It contains the data and process records used for the AgenticDev 2026 submission:

- the `K=3` induction trajectories;
- the primary same-model PyBugHive hard-smoke experiment;
- the model-mixed all-seven exploratory record;
- the `gpt-5.5` structural-control rerun;
- scripts, schemas, prompts, memory artifacts, task metadata, patches, metrics,
  paper tables, and process reports needed to audit the claims.

## Quick Validation

From this artifact folder:

```powershell
py scripts\validate_task.py tasks
py scripts\validate_trajectory.py trajectories
py scripts\validate_run_manifest.py manifests
py scripts\validate_task.py task_sets\primary_first6
py scripts\validate_trajectory.py trajectory_sets\primary_first6
py scripts\validate_trajectory.py trajectory_sets\structural_control_gpt55
py scripts\validate_artifact_inventory.py .
```

Recompute the main first-six aggregate:

```powershell
py scripts\compute_metrics.py trajectory_sets\primary_first6 --tasks task_sets\primary_first6 --group-by method --output-csv results\recomputed_primary_first6_by_method.csv --output-json results\recomputed_primary_first6_by_method.json
```

Recompute the `gpt-5.5` structural control:

```powershell
py scripts\compute_metrics.py trajectory_sets\structural_control_gpt55 --tasks task_sets\primary_first6 --group-by method --output-csv results\recomputed_structural_control_gpt55_by_method.csv --output-json results\recomputed_structural_control_gpt55_by_method.json
```

## Main Experimental Sets

| Set | Location | Role |
|---|---|---|
| `K=3` induction training | `trajectory_sets/induction_train_k3/` | Source trajectories used to induce `memory/pybughive/test_failure_triage/auto_skill.md` |
| Primary first-six hard smoke | `trajectory_sets/primary_first6/` | Main quantitative evidence in the paper |
| Exploratory all-seven hard smoke | `trajectory_sets/exploratory_all7/` | Supplementary model-mixed robustness check |
| Structural control `gpt-5.5` | `trajectory_sets/structural_control_gpt55/` | Auto SKILL.md vs. format-shuffled SKILL.md |

The full curated trajectory directories are also available under `trajectories/`.

## What Is Not Included

The local `runs/` directory is not copied. It is about 250 MB and contains raw
agent stdout, temporary checkout paths, and machine-specific run logs. The
validated trajectory JSON files in this artifact are the canonical cleaned
process records used for metrics and paper claims.

The external PyBugHive source dump under `data/external/` is not copied. This
artifact includes the curated task metadata and patches derived from it.
