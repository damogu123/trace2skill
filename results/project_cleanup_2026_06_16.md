# Project Cleanup Report

Date: 2026-06-16

## Summary

Performed a conservative cleanup of generated and reconstructable files.

- Before: 31,832 files, 1,207.6 MB.
- After: 2,122 files, 274.5 MB.
- Freed: 933.1 MB.

## Deleted

- `workspaces/`: isolated task checkouts and verification workspaces. These are
  reconstructable from tasks, manifests, and `scripts/prepare_task.py`.
- `paper/render_agenticdev/`: rendered PNGs used for visual PDF inspection.
- `paper/svg-inkscape/`: generated SVG-to-PDF cache from LaTeX builds.
- `scripts/__pycache__/`: Python bytecode cache.
- LaTeX intermediates in `paper/`: `*.aux`, `*.bbl`, `*.blg`, `*.fdb_latexmk`,
  `*.fls`, `*.log`, and `*.out`.
- Superseded local PDF builds in `paper/`: `main_updated.pdf`,
  `main_numeric.pdf`, `main_times.pdf`, `main_figures.pdf`, and
  `main_agenticdev_baseline.pdf`.

## Retained

- `runs/`: raw run logs, patches, final tests, and agent traces.
- `trajectories/`: validated trajectory JSON records.
- `results/`: reports, metrics, and setup notes.
- `data/`, `tasks/`, `manifests/`, `prompts/`, `schemas/`, `memory/`,
  `patches/`, and core scripts.
- `paper/main.pdf` and `paper/main_agenticdev.pdf`: current AgenticDev
  submission-format PDFs.
- `paper/main_figures_clean.pdf`: pre-venue generic manuscript build.
- All paper source files, tables, figures, reviews, and bibliography.

## Verification

- Required project files still exist:
  - `paper/main.pdf`
  - `paper/main_agenticdev.pdf`
  - `paper/main_figures_clean.pdf`
  - `paper/main.tex`
  - `paper/references.bib`
  - `paper/BUILD.md`
  - `scripts/record_trajectory.py`
  - `scripts/run_external_agent.py`
  - `scripts/validate_trajectory.py`
- `python scripts/validate_trajectory.py trajectories` passed for all 129
  trajectory JSON files.
- PDF metadata:
  - `paper/main.pdf`: 11 pages, US Letter.
  - `paper/main_agenticdev.pdf`: 11 pages, US Letter.
  - `paper/main_figures_clean.pdf`: 20 pages, US Letter.

## Rebuild Notes

To regenerate paper build intermediates and SVG conversion outputs:

```powershell
cd paper
$env:Path="C:\Strawberry\perl\bin;C:\Strawberry\c\bin;$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64;C:\Program Files\Inkscape\bin;$env:Path"
latexmk -pdf -jobname=main_agenticdev -shell-escape -interaction=nonstopmode -file-line-error main.tex
```

To recreate task workspaces, run the relevant manifest through the existing
preparation or external-agent scripts with `--prepare`.
