# Manuscript Working Index

Working title:

**Evaluating Low-Shot Procedural Skill Transfer in Language-Agent Debugging**

## Current Paper Assets

### Drafted Sections

- `paper/sections/method.md`: Markdown Method draft.
- `paper/sections/method.tex`: LaTeX Method draft.
- `paper/sections/introduction.md`: Markdown Introduction draft.
- `paper/sections/introduction.tex`: LaTeX Introduction draft.
- `paper/sections/related_work.md`: Markdown Related Work draft.
- `paper/sections/related_work.tex`: LaTeX Related Work draft.
- `paper/sections/abstract.md`: Markdown Abstract draft.
- `paper/sections/abstract.tex`: LaTeX Abstract draft.
- `paper/sections/results.md`: Markdown Results draft.
- `paper/sections/results.tex`: LaTeX Results draft.
- `paper/sections/discussion.md`: Markdown Discussion draft.
- `paper/sections/discussion.tex`: LaTeX Discussion draft.
- `paper/sections/limitations.md`: Markdown Limitations draft.
- `paper/sections/limitations.tex`: LaTeX Limitations draft.
- `paper/sections/declarations.md`: Markdown declarations and disclosure draft.
- `paper/sections/declarations.tex`: LaTeX declarations and disclosure draft.
- `paper/sections/appendix_results.md`: supplementary result notes.
- `paper/sections/result_claims_guardrails.md`: claims to make and claims to avoid.
- `paper/references.bib`: verified bibliography for Introduction and Related Work.

### Main Manuscript

- `paper/main.tex`: AgenticDev 2026 anonymous ACM `sigconf` manuscript driver.
- `paper/BUILD.md`: AgenticDev build command and SVG notes.
- `paper/main_agenticdev.pdf`: current submission-format build, regenerated on
  2026-07-10 with 10 pages of manuscript content and one references-only page.
- `paper/reviews/agenticdev_2026_format_report_2026_06_08.md`: venue
  requirements, completed changes, and final verification record.
- `paper/reviews/p0_revision_report_2026_07_10.md`: P0 content cleanup,
  verification, and remaining submission items.
- `paper/main_figures_clean.pdf`: latest verified 20-page local build with
  Times-style fonts, compact numeric citations, corrected Figure 1/3 layouts,
  enlarged print-readable Figure 2/3 typography, and a cleaner Figure 3 with
  encoding details moved to the caption.
- `paper/main.pdf`: earlier 11-page AgenticDev build retained as a local PDF.
- `paper/reviews/full_manuscript_consistency_report_2026_06_08.md`: full
  citation, claim, terminology, and path audit.
- `paper/reviews/latex_build_report_2026_06_08.md`: toolchain, build, and
  rendered-page verification report.

### Main Figures

- `paper/figures/evaluation_protocol_diagram.svg`: use in Method or overview.
- `paper/figures/hard_first6_main_bars.svg`: main Results figure.
- `paper/figures/hard_first6_task_outcomes_heatmap.svg`: task-level transfer and negative-transfer figure.
- `paper/figures/hard_first6_efficiency_scatter.svg`: optional main or appendix process-efficiency figure.

### Supplementary Figures

- `paper/figures/hard_first7_exploratory_bars.svg`: model-mixed all-seven result.
- `paper/figures/black234_tokens.svg`: single-task `black_234` token-cost result.

### Main Tables

- `paper/tables/hard_first6_main_table.md`
- `paper/tables/hard_first6_main_table.tex`
- `paper/tables/hard_first6_task_outcomes.md`
- `paper/tables/hard_first6_common_solved_pairwise.md`

### Supplementary Tables

- `paper/tables/hard_first7_exploratory_table.md`
- `paper/tables/hard_first7_exploratory_table.tex`
- `paper/tables/black234_single_task_table.md`
- `paper/tables/hard_first6_structural_control_gpt55.md`
- `paper/tables/hard_first6_structural_control_gpt55.tex`
- `paper/tables/experiment_ledger.md`
- `paper/tables/experiment_ledger.tex`

## Recommended Main-Text Order

1. Introduction: motivation, gap, procedural memory artifact framing.
2. Related Work: reflection, experiential memory, trajectory-to-skill induction, reusable workflows, and language-agent debugging.
3. Method: trajectory collection, SKILL.md induction, baselines, evaluation harness.
4. Results: use `paper/sections/results.md`.
5. Discussion: what procedural memory buys, where it fails, limits of Black-only hard smoke.
6. Limitations and future work: scale, cross-repository tasks, same-model reruns, statistical power.

## Main Result Sentence

On a six-task same-model PyBugHive Black hard-smoke slice, Auto SKILL.md tied the best solve rate at 5/6 while reducing tokens per solved task by 13.8% relative to Reflexion memory, 20.7% relative to a generic checklist, 24.4% relative to length-matched Reflexion, and 38.2% relative to no memory, with one explicit negative-transfer failure. A later `gpt-5.5` Auto-vs-format-shuffled rerun should be used as supplementary evidence that procedural organization affects process behavior but is not necessary for solvability in that stronger-model setting.

## Next Writing Step

Prepare the anonymized artifact package/link and complete the submission
metadata. Keep author and affiliation fields anonymous until the venue permits
de-anonymization.
