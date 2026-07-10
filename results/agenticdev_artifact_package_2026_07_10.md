# AgenticDev Artifact Package Report - 2026-07-10

## Output

Created a curated GitHub-ready artifact folder:

- `artifact_agenticdev2026/`
- 492 files
- 2.14 MB

The folder is intended to be uploaded directly as the experiment/data artifact
for the AgenticDev 2026 submission.

The general `github_export/` directory was also regenerated after this change
and now includes `artifact_agenticdev2026/`:

- `github_export/`
- 1,000 copied files
- 219 skipped generated/local files

## Included Evidence

- `K=3` induction-source tasks and trajectories.
- Primary first-six PyBugHive hard-smoke task set and trajectories.
- Exploratory all-seven hard-smoke records, with `black_234` kept separate in
  the documentation as model-mixed evidence.
- `gpt-5.5` structural-control rerun trajectories.
- Frozen memory artifacts and baseline prompt artifacts.
- Induction prompts and run prompts for the included experiments.
- Curated PyBugHive task metadata and benchmark patches.
- Schemas, validation scripts, metric scripts, and paper result-generation
  scripts.
- Paper tables, SVG figures, Method/Results source sections, and result
  guardrails.
- A separated `supplementary_harness_validation/` directory for the earlier
  easy PyBugHive MVP harness-validation runs.

## Excluded Evidence

- `runs/` raw run artifacts are excluded from the upload folder. They are about
  250 MB and contain raw stdout, temporary checkout paths, and machine-specific
  logs. The validated trajectory JSON files are the canonical cleaned process
  records used for metrics and claims.
- `workspaces/` isolated checkouts are excluded because they are
  reconstructable execution scratch space.
- `data/external/` is excluded because it is an external PyBugHive source dump;
  curated task metadata and patches are included instead.
- PDFs and LaTeX build intermediates are excluded.

## Convenience Sets

- `trajectory_sets/induction_train_k3/`: 3 training trajectories.
- `trajectory_sets/primary_first6/`: 30 trajectories, six tasks x five methods.
- `trajectory_sets/exploratory_all7/`: 35 trajectories, seven tasks x five
  methods.
- `trajectory_sets/structural_control_gpt55/`: 12 trajectories, six tasks x two
  methods.
- `task_sets/primary_first6/`: six primary held-out tasks.

## Verification

Schema validation passed inside the artifact:

```powershell
py scripts\validate_task.py tasks
py scripts\validate_trajectory.py trajectories
py scripts\validate_run_manifest.py manifests
py scripts\validate_task.py task_sets\primary_first6
py scripts\validate_trajectory.py trajectory_sets\primary_first6
py scripts\validate_trajectory.py trajectory_sets\structural_control_gpt55
```

Metric recomputation from the convenience sets reproduced the paper-level
values:

- Primary first-six Auto SKILL.md: 5/6 solved, 56,866.8 tokens per solved task,
  one negative-transfer flag.
- Primary first-six Reflexion memory: 5/6 solved, 65,914.6 tokens per solved
  task.
- Structural-control Auto SKILL.md: 6/6 solved, 1.6667 cycles per solved task,
  111,978.3333 tokens per solved task.
- Structural-control format-shuffled SKILL.md: 6/6 solved, 2.1667 cycles per
  solved task, 102,005.8333 tokens per solved task.

Upload hygiene checks:

- no `runs/`, `workspaces/`, `data/external/`, PDFs, or raw LaTeX build
  products are present in the artifact;
- no local absolute project paths such as Windows home or WSL-mounted project
  paths remain in artifact contents;
- bytecode caches were removed after validation.

## Rebuild Command

The artifact can be regenerated with:

```powershell
py scripts\create_agenticdev_artifact.py --force
```

The full GitHub-facing export can then be regenerated with:

```powershell
py scripts\create_github_export.py --force
```
