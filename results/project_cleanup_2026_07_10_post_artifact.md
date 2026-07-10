# Post-Artifact Local Cleanup Report

Date: 2026-07-10

Purpose: remove large local-only experiment material after the cleaned
AgenticDev artifact package and GitHub export had been created.

## Deleted

- `runs/`: 1,330 files, 249.96 MB
- `data/external/`: 78 files, 16.38 MB

Approximate space freed: 266.34 MB.

## Retained

- `github_export/`: GitHub-facing repository export
- `artifact_agenticdev2026/`: compact upload-ready experiment artifact
- `trajectories/`: validated cleaned process records
- `tasks/`, `manifests/`, `data/pybughive/`, `data/pybughive_hard/`
- `paper/`: manuscript source and current PDFs

## Rationale

The deleted `runs/` directory contained raw stdout, patches, traces, and
machine-specific logs. The paper's reproducibility evidence is preserved in the
validated trajectory JSON files and in `artifact_agenticdev2026/`. The deleted
`data/external/` directory contained third-party benchmark material that is not
needed in the cleaned repository export.

## Verification

The following validations passed after deletion:

```powershell
py scripts\validate_task.py tasks
py scripts\validate_trajectory.py trajectories
py scripts\validate_run_manifest.py manifests
py scripts\validate_task.py artifact_agenticdev2026\tasks
py scripts\validate_trajectory.py artifact_agenticdev2026\trajectory_sets\primary_first6
py scripts\validate_trajectory.py artifact_agenticdev2026\trajectory_sets\structural_control_gpt55
py scripts\validate_run_manifest.py artifact_agenticdev2026\manifests
```

Current clean upload targets:

- full GitHub-facing export: `github_export/`
- compact experiment/data artifact: `artifact_agenticdev2026/`
