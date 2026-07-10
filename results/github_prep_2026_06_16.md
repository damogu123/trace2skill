# GitHub Preparation Report

Date: 2026-06-16

## Goal

Prepare the project for eventual GitHub upload while preserving local
experiment evidence.

## Added

- `README.md`: project overview, claim boundaries, quick-start commands, and
  reproducibility notes.
- `.gitignore`: excludes local/generated artifacts such as `runs/`,
  `workspaces/`, `logs/`, `data/external/`, `prompts/runs/`, LaTeX build
  products, rendered screenshots, and `github_export/`.
- `.gitattributes`: normalizes text files and marks binary assets.
- `requirements.txt`: documents that the harness is standard-library only.
- `docs/PROJECT_STRUCTURE.md`: separates source, small evidence artifacts, and
  local-only/release artifacts.
- `docs/GITHUB_PREP.md`: GitHub upload checklist.
- `scripts/create_github_export.py`: repeatable exporter for a clean repository
  copy.

## Removed Local Temporary Files

- Deleted old rendered inspection screenshots from `results/*.png`.
- Deleted root-level process logs in `logs/`.
- Deleted Python bytecode caches generated during validation.

## Export

Generated:

- `github_export/`

Export properties:

- 503 files;
- approximately 2.0 MB;
- excludes PDF, PNG, log, PID, and bytecode files;
- excludes `runs/`, `logs/`, `workspaces/`, `data/external/`, and
  `prompts/runs/`.

The export can be regenerated with:

```powershell
python scripts/create_github_export.py --force
```

## Verification

Passed:

```powershell
python scripts/validate_task.py tasks
python scripts/validate_trajectory.py trajectories
python scripts/validate_run_manifest.py manifests
```

The same task, trajectory, and manifest validations also passed inside
`github_export/`.

`scripts/create_github_export.py` passed Python bytecode compilation.

## Notes

- `runs/` remains in the full local workspace as raw experiment evidence, but
  it is intentionally excluded from the GitHub export and root `.gitignore`.
- `data/external/` remains local until third-party redistribution permissions
  are confirmed.
- A public repository still needs a selected `LICENSE`; no license was added.
