# P0 Revision Report - 2026-07-10

## Scope

This revision addresses the AgenticDev-focused P0 cleanup items identified in
`paper/reviews/agenticdev_skill_review_2026_06_16.md`.

Skills used:

- `academic-paper` revision mode
- `quality-editor`

## Manuscript Changes

- Added the exact `K=3` induction-source trajectories in Method:
  `pybughive_black_297`, `pybughive_cookiecutter_1513`, and
  `pybughive_discord_py_7676`.
- Clarified that all three induction-source runs are no-memory, seed-1 training
  trajectories labeled `test_failure_triage`, and that none of their task IDs
  appears in the held-out hard-smoke slice.
- Added the negative-transfer annotation evidence source: validated trajectory
  records, cycle diagnoses, patch summaries, test-rerun outcomes, failed-patch
  counts, and mistake annotations.
- Added concrete evidence for the `pybughive_black_132` Auto SKILL.md negative
  transfer case: the stored trajectory notes that the first attempted fix
  increased full-suite failures from four to six before later narrowing.
- Rounded and formatted the `gpt-5.5` structural-control table consistently.
- Cleaned stable BibTeX metadata where the source was already verified,
  including publisher/address fields for NeurIPS, ACL, ICLR, AAAI Press, and
  ACM entries where appropriate.

## Verification

- `latexmk -pdf -jobname=main_agenticdev -shell-escape -interaction=nonstopmode -file-line-error main.tex`
  passed from `paper/`.
- `paper/main_agenticdev.pdf` was regenerated as an 11-page US Letter PDF.
- Final LaTeX log contains no undefined citations, undefined references, or
  overfull horizontal boxes.
- Citation-key coverage check: 18 BibTeX keys, 18 cited keys, no missing keys,
  no orphan BibTeX entries.
- `py scripts/validate_trajectory.py trajectories` passed for all trajectory
  JSON files.
- `py scripts/validate_task.py tasks` passed for all task files.
- `py scripts/validate_run_manifest.py manifests` passed for all manifests.
- `py scripts/create_github_export.py --force` regenerated `github_export/`
  with 506 copied files and 219 skipped generated/local files after cleanup.
- Exported `tasks`, `trajectories`, and `manifests` pass the same schema
  validators.
- Claim-guardrail search found no unsupported universal-superiority,
  statistical-significance, or state-of-the-art claims.

## Residual Submission Items

- The anonymous artifact link still needs an external upload target.
- Remaining BibTeX warnings are conservative metadata warnings for accepted or
  preprint-style records with no stable page/publisher/address metadata in the
  verified source. They should not be eliminated by inventing publication
  details.
- Final submission metadata still needs venue-specific fields once the actual
  submission form is open.
