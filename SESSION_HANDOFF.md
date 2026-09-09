# Session Handoff

Last updated: 2026-07-10

## Project Goal

Working title:

**Evaluating Low-Shot Procedural Skill Transfer in Language-Agent Debugging**

The paper studies whether a language agent can induce a natural-language `SKILL.md` from a small number of debugging trajectories and transfer that procedural memory to within-family held-out debugging tasks.

Primary positioning:

- The main contribution is an evaluation protocol.
- `SKILL.md` is a trajectory-induced procedural memory artifact, not ordinary prompt engineering.
- The empirical claim concerns low-shot within-family transfer and process efficiency.
- Do not claim universal superiority over Reflexion or statistical significance.

## Core Research Question

Can an agent induce a natural-language procedural memory artifact from a few debugging trajectories and, on within-family held-out tasks, achieve comparable repair success with fewer recorded diagnosis-edit-test cycles and tokens than reflection-style memory, without increasing negative transfer?

## Current Evidence

### Primary experiment

- Six verified PyBugHive `black` hard-smoke tasks.
- Model: `gpt-5.3-codex`.
- Five methods: no memory, generic checklist, Reflexion, length-matched Reflexion, Auto SKILL.md.
- Auto SKILL.md solves 5/6, tied with the best primary methods.
- Auto SKILL.md has lower tokens per solved task than the four comparison methods.
- One explicit negative-transfer failure occurs in the primary Auto SKILL.md run.

Use:

- `paper/tables/hard_first6_main_table.md`
- `paper/tables/hard_first6_common_solved_pairwise.md`
- `paper/sections/result_claims_guardrails.md`

### Supplementary structural control

- Same first-six tasks under `gpt-5.5`.
- Auto SKILL.md versus format-shuffled SKILL.md.
- Both solve 6/6.
- Auto SKILL.md uses fewer recorded cycles and failed patches.
- Format-shuffled SKILL.md uses fewer tokens in aggregate.
- This is a boundary check, not part of the primary five-method table.
- It does not prove that canonical SKILL.md structure is necessary for solvability.

Use:

- `paper/tables/hard_first6_structural_control_gpt55.md`
- `results/pybughive_hard_auto_vs_format_shuffled_first6_gpt55_report.md`
- `paper/tables/experiment_ledger.md`

### Earlier easy MVP

- A separate PyBugHive MVP contains 7 held-out tasks x 7 methods = 49 valid trajectories.
- It includes Auto SKILL.md, format-shuffled skill, generic checklist, length-matched Reflexion, no memory, raw trajectory retrieval, and Reflexion.
- The MVP was too easy: generic checklist and no memory solved all seven tasks.
- It is useful for harness validation and exploratory evidence, but it is not the paper's primary quantitative result.

Use:

- `results/pybughive_pipeline_status.md`
- `results/pybughive_heldout_final_metrics.csv`
- `results/pybughive_results_memo.md`
- `results/pybughive_task_breakdown.md`

## Data Provenance

- Early `fixtures/local_*` tasks were authored locally to validate task preparation, trajectory recording, baselines, and metric computation.
- Those local fixtures are synthetic engineering tests, not the paper's publication dataset.
- The empirical paper evidence uses imported and locally reproduced PyBugHive tasks.
- Reference patches are used only to verify task reproducibility and solvability; they are not shown to the held-out repair agent.
- The current primary study is intentionally restricted to verified PyBugHive `black` formatter tasks.

## Implementation Status

The evaluation harness is implemented and has been exercised end to end.

Schemas:

- `schemas/task.schema.json`
- `schemas/trajectory.schema.json`
- `schemas/agent_trace.schema.json`
- `schemas/run_manifest.schema.json`

Core scripts:

- `scripts/import_pybughive_tasks.py`
- `scripts/verify_pybughive_tasks.py`
- `scripts/select_pybughive_hard_subset.py`
- `scripts/prepare_task.py`
- `scripts/create_run_manifest.py`
- `scripts/build_run_prompts.py`
- `scripts/run_external_agent.py`
- `scripts/run_codex_agent.py`
- `scripts/record_trajectory.py`
- `scripts/validate_task.py`
- `scripts/validate_trajectory.py`
- `scripts/validate_run_manifest.py`
- `scripts/compute_metrics.py`
- `scripts/make_paper_results.py`

Implemented runner behavior includes:

- isolated task workspaces;
- initial failure reproduction;
- narrow and broader test reruns;
- final patch collection;
- structured trajectory validation;
- UTF-8 Codex CLI output capture;
- token-count repair from Codex logs;
- WSL execution for compatible PyBugHive environments;
- normalized mistake and negative-transfer records.

Frozen memory artifacts:

- `memory/pybughive/test_failure_triage/auto_skill.md`
- `memory/pybughive/test_failure_triage/reflexion.md`
- `memory/pybughive/test_failure_triage/length_matched_reflexion.md`
- `memory/pybughive/test_failure_triage/raw_trajectory_retrieval.md`
- `memory/pybughive/test_failure_triage/format_shuffled_skill.md`

Do not edit a frozen memory artifact and reuse old results. Any changed artifact must receive a new condition/manifest and be rerun.

`oracle_skill_template.md` is still a template, not a completed human-authored oracle condition. Oracle skill has not been included in the hard-smoke primary study.

## Experiment Completeness

- `trajectories/pybughive_hard_smoke/` contains 35 trajectories: seven tasks x five primary methods. The first six tasks form the clean same-model primary table; `black_234` is model-mixed supplementary evidence.
- `trajectories/pybughive_hard_auto_skill_first6/` contains six `gpt-5.5` Auto SKILL.md reruns.
- `trajectories/pybughive_hard_format_shuffled_first6/` contains six `gpt-5.5` format-shuffled reruns.
- `trajectories/pybughive_heldout_memory_baselines/` contains 49 earlier easy-MVP trajectories: seven tasks x seven methods.
- As of June 7, 2026, all 96 JSON files across these four trajectory directories pass `scripts/validate_trajectory.py`.
- Raw trajectory retrieval and oracle skill are not part of the first-six hard-smoke primary table.
- A full current-model rerun of all methods has not been completed.
- Multiple agent-execution seeds, multiple induction seeds, and cross-project hard tasks have not been completed.

Model-attribution caveat:

- `manifests/pybughive_hard_smoke_codex.json` retains a top-level `gpt-5.3-codex` model label, but the five actual `black_234` trajectory records were produced with `gpt-5.5`.
- For model attribution, use each trajectory's recorded model together with `paper/tables/experiment_ledger.md`; do not infer the all-seven setting from the manifest's top-level model field alone.

## Drafted Paper Sections

- `paper/sections/abstract.md` and `abstract.tex`
- `paper/sections/introduction.md` and `introduction.tex`
- `paper/sections/method.md` and `method.tex`
- `paper/sections/results.md` and `results.tex`
- `paper/sections/discussion.md` and `discussion.tex`
- `paper/sections/limitations.md` and `limitations.tex`
- `paper/sections/declarations.md` and `declarations.tex`
- `paper/sections/appendix_results.md`
- `paper/main.tex`
- `paper/BUILD.md`

The Abstract and Introduction were revised after reviewer feedback. They now:

- explicitly scope results to the primary same-model run;
- define the evaluation gap beyond solve rate;
- operationally distinguish procedural memory from a generated prompt;
- explain why formatter hard-smoke tasks are meaningful;
- avoid strengthening the empirical claim.

## Review Reports

- `paper/reviews/method_results_discussion_limitations_reviewer_report.md`
- `paper/reviews/post_structural_control_reviewer_report.md`
- `paper/reviews/quick_review_intro_abstract_2026_06_03.md`
- `paper/reviews/agenticdev_skill_review_2026_06_16.md`
- `paper/reviews/p0_revision_report_2026_07_10.md`

Current editorial assessment:

- AgenticDev/focused workshop: borderline positive after P0 cleanup.
- Main conference: major revision, mainly due to evidence scale and literature positioning.

Latest AgenticDev-focused skill review completed on June 16, 2026 using
`academic-paper-reviewer` and `quality-editor`.

Key P0 cleanup items before submission:

- add or submit the anonymized artifact link: still open because it requires an
  external upload target;
- specify the three `K=3` training trajectories or point to the exact artifact
  table: completed July 10, 2026;
- add one sentence describing the negative-transfer annotation evidence source:
  completed July 10, 2026;
- round and format the `gpt-5.5` structural-control table: completed July 10,
  2026;
- clean stable BibTeX metadata warnings where possible: completed
  conservatively July 10, 2026. Do not invent pages, venues, publisher, address,
  DOI, or volume metadata merely to silence BibTeX warnings.

## AgenticDev P0 Revision Completed

Completed on July 10, 2026 using:

1. `$academic-paper` revision mode
2. `$quality-editor`

Completed changes:

- added exact `K=3` induction-source trajectories in Method:
  `pybughive_black_297`, `pybughive_cookiecutter_1513`, and
  `pybughive_discord_py_7676`;
- stated that the induction-source runs are no-memory, seed-1 training
  trajectories labeled `test_failure_triage`, with no overlap against the
  held-out hard-smoke task IDs;
- added the evidence basis for negative-transfer annotation;
- added concrete `pybughive_black_132` negative-transfer evidence from the
  validated trajectory record;
- rounded and formatted the `gpt-5.5` structural-control table;
- cleaned stable BibTeX publisher/address metadata where source-verified.

Verification:

- `paper/main_agenticdev.pdf` was rebuilt on July 10, 2026 as an 11-page US
  Letter AgenticDev PDF;
- no undefined citation, undefined reference, or overfull horizontal-box warning
  remains in the final LaTeX log;
- all 18 BibTeX entries are cited, with no missing or orphan keys;
- `py scripts/validate_trajectory.py trajectories` passed;
- `py scripts/validate_task.py tasks` passed;
- `py scripts/validate_run_manifest.py manifests` passed.

Remaining submission item:

- create/upload the anonymous artifact package and add the final artifact link
  to the paper/submission form.

## AgenticDev Artifact Folder Completed

Completed on July 10, 2026.

Output:

- `artifact_agenticdev2026/`
- 492 files
- 2.14 MB

Purpose:

- upload-ready experiment/data artifact folder for GitHub;
- contains the paper's induction trajectories, primary hard-smoke trajectories,
  exploratory all-seven records, `gpt-5.5` structural-control records, curated
  tasks, manifests, prompts, frozen memory artifacts, patches, metrics, tables,
  figures, schemas, and scripts;
- keeps the earlier easy PyBugHive MVP in
  `supplementary_harness_validation/`, separate from the primary evidence.

Important exclusions:

- `runs/` raw artifacts are not included because they are about 250 MB and
  contain raw stdout, local checkout paths, and machine-specific logs;
- `data/external/`, `workspaces/`, PDFs, and LaTeX intermediates are excluded;
- validated trajectory JSON files are the canonical cleaned process records
  used for metrics and paper claims.

Verification:

- artifact root `tasks`, `trajectories`, and `manifests` pass schema
  validation;
- `task_sets/primary_first6`, `trajectory_sets/primary_first6`, and
  `trajectory_sets/structural_control_gpt55` pass schema validation;
- recomputed primary first-six metrics reproduce the paper-level values
  including Auto SKILL.md 5/6 solved and 56,866.8 tokens per solved task;
- recomputed structural-control metrics reproduce 6/6 vs. 6/6 and 1.6667 vs.
  2.1667 cycles per solved task;
- local absolute project paths were sanitized from artifact contents.

Use:

- `artifact_agenticdev2026/README.md`
- `artifact_agenticdev2026/DATA_SELECTION.md`
- `artifact_agenticdev2026/REPRODUCE.md`
- `artifact_agenticdev2026/FILE_INVENTORY.tsv`
- `results/agenticdev_artifact_package_2026_07_10.md`
- `github_export/artifact_agenticdev2026/`

Regenerate with:

```powershell
py scripts/create_agenticdev_artifact.py --force
py scripts/create_github_export.py --force
```

## Related Work Literature Review Completed

Completed on June 7, 2026 using:

1. `$deep-research lit-review mode`
2. `$paper-analyst`

Research scope:

- low-shot procedural skill transfer;
- agent memory and reflection;
- trajectory-to-skill or trajectory-to-workflow induction;
- reusable skill libraries;
- language-agent coding/debugging;
- software-engineering agent benchmarks.

Target source families:

- Reflexion and experiential memory;
- ExpeL and AutoGuide;
- Voyager and reusable skill libraries;
- Agent Workflow Memory;
- SkillWeaver and related skill-discovery systems;
- trajectory/programmatic skill induction;
- SWE-agent and SWE-bench;
- PyBugHive and BugsInPy.

Source rules:

- Use original papers, official proceedings/OpenReview pages, arXiv records, or official benchmark/project pages.
- Do not invent citation metadata, venue, DOI, result numbers, or BibTeX keys.
- If only an abstract is accessible, mark the analysis as abstract-level.
- Separate peer-reviewed papers from preprints and very recent work.

Completed outputs:

- `paper/literature_review/search_protocol.md`
- `paper/literature_review/literature_matrix.md`
- `paper/literature_review/comparison_tables.md`
- `paper/literature_review/research_gap.md`
- `paper/literature_review/verified_sources.md`
- ten core paper analysis cards under
  `paper/literature_review/paper_analyses/`

The verified corpus contains 18 sources: 16 published/formally accepted papers
and two labeled preprints.

Important literature conclusion:

- A broad claim that procedural memory is unstudied is false by 2026. Memp,
  Skill-Pro, and LEGOMem explicitly study procedural memory.
- ReasoningBank already evaluates memory on SWE-bench Verified with success,
  steps, and token cost, and observes degradation from noisy or excessive
  memory.
- The defensible gap is narrower: in the verified corpus, no work jointly
  evaluates a fixed low-shot natural-language procedural artifact induced from
  debugging trajectories, within-family held-out real-bug transfer, repair
  success plus process cost, explicit per-task memory-attributed negative
  transfer, and length/organization controls.

Metadata corrections discovered during audit:

- PyBugHive is Antal et al. (2024), DOI
  `10.1109/ACCESS.2024.3449106`. Do not use the earlier mismatched candidate
  author list or DOI.
- Reflexion was missing Edward Berman in the candidate author list.
- Agent-Pro had an incorrect candidate author list and DOI; the correct DOI is
  `10.18653/v1/2024.acl-long.292`.
- LearnAct, SkillWeaver, Memp, Skill-Pro, and LEGOMem had mismatched candidate
  author lists.
- Memp and LEGOMem method/domain descriptions were corrected against their
  current original records.

Related Work prose and citation integration are complete:

- `paper/sections/related_work.md`
- `paper/sections/related_work.tex`
- `paper/references.bib`
- `paper/reviews/related_work_quality_report_2026_06_07.md`

The Introduction Markdown and LaTeX files now cite verified work on
software-engineering agents, reflection, experiential memory, workflows,
procedural memory, efficiency, and PyBugHive.

All 18 BibTeX keys are cited in both Markdown and LaTeX coverage, with no
missing or orphan keys. Four DOI-title pairs were checked against Crossref.

## Full Manuscript Integration Completed

Completed on June 8, 2026 using:

1. `$academic-paper` revision mode
2. `$quality-editor`

Completed work:

- created `paper/main.tex` and integrated Abstract, Introduction, Related Work,
  Method, Results, Discussion, Limitations, Declarations, and
  `paper/references.bib`;
- added `paper/BUILD.md` with the required LaTeX/SVG build command and
  dependency notes;
- added verified citations to Method, Discussion, and Limitations while
  keeping Markdown and LaTeX synchronized;
- added draft data/code, ethics, author-contribution, competing-interest,
  funding, and AI-assistance declarations;
- checked all citation keys, section inputs, figure paths, static LaTeX brace
  and environment balance, terminology, and result-claim boundaries.

Audit result:

- 18 BibTeX keys, 18 Markdown keys, and 18 LaTeX keys;
- zero missing keys, zero orphan entries, and zero Markdown/LaTeX differences;
- all eight main section inputs and all four referenced SVG files exist;
- no unsupported universal-superiority, novelty, or statistical-significance
  claim was found.

Use:

- `paper/reviews/full_manuscript_consistency_report_2026_06_08.md`

## LaTeX Toolchain And PDF Build Completed

Completed on June 8, 2026.

Installed on Windows:

- MiKTeX 25.12 with the current package set;
- Strawberry Perl 5.42.2.1;
- Inkscape 1.4.4.

The user `PATH` includes MiKTeX and Inkscape. Open a new terminal before
running the build manually.

Verified command from `paper/`:

```powershell
latexmk -pdf -shell-escape -interaction=nonstopmode -file-line-error main.tex
```

Build result after the latest visual/citation corrections:

- `paper/main_figures_clean.pdf`, 20 US Letter pages;
- all 18 bibliography entries resolved;
- all four SVG figures converted and embedded;
- no final overfull/underfull box, undefined citation/reference, package, or
  BibTeX warning;
- title, Method figure, Results tables/figures, declarations, and bibliography
  pages visually inspected.

Build-related source corrections include Latin Modern fonts, safe SVG text
embedding, width-constrained result tables, breakable code identifiers, and
controlled Results float placement. Citations now use uncompressed bracketed
numeric references ordered by first appearance, for example `[3, 4, 5]`
rather than `[3--5]`. The generic manuscript uses the Times-style
`newtxtext`/`newtxmath` family, giving citation labels such as `[1]` the wider,
more compact proportions common in CS papers. Figure 1 uses non-overlapping
control-condition connectors and a taller metrics box. Figure 3 uses compact
letter markers plus a separate legend, so method labels no longer overlap the
points. Figure 2 and Figure 3 now use larger titles, axes, ticks, values, and
legend labels sized for the final manuscript width. Figure 3's x-axis title
is the final line inside the graphic; the marker-size and lower-left
interpretation are stated only in the caption to avoid redundant visual
clutter.

Current PDF inventory:

- `paper/main_agenticdev.pdf` is the latest AgenticDev submission-format build
  and was rebuilt on July 10, 2026.
- `paper/main.pdf` is an earlier 11-page local AgenticDev build retained for
  reference; do not treat it as the latest submission PDF.
- `paper/main_figures_clean.pdf` is the earlier 20-page generic build retained
  for visual/reference comparison.

Use:

- `paper/BUILD.md`
- `paper/reviews/latex_build_report_2026_06_08.md`

## Next Task

Prepare the anonymized artifact package/link and complete the AgenticDev
submission metadata. Do not de-anonymize the manuscript before confirming the
venue's current review instructions.

## Project Cleanup Completed

Completed on June 16, 2026.

Conservative cleanup removed generated and reconstructable files:

- deleted `workspaces/` isolated checkouts and verification workspaces;
- deleted `paper/render_agenticdev/` visual-inspection PNGs;
- deleted `paper/svg-inkscape/` LaTeX SVG conversion cache;
- deleted Python bytecode cache;
- deleted LaTeX intermediate files in `paper/`;
- deleted superseded local PDFs:
  `main_updated.pdf`, `main_numeric.pdf`, `main_times.pdf`,
  `main_figures.pdf`, and `main_agenticdev_baseline.pdf`.

Retained all scientific/source assets:

- `runs/` raw logs, patches, traces, and final test logs;
- `trajectories/` validated trajectory JSON records;
- `results/`, `data/`, `tasks/`, `manifests/`, `prompts/`, `schemas/`,
  `memory/`, `patches/`, and all core scripts;
- `paper/main.pdf`, `paper/main_agenticdev.pdf`, and
  `paper/main_figures_clean.pdf`;
- paper source, figures, tables, reviews, bibliography, and literature review.

Cleanup result:

- before: 31,832 files, 1,207.6 MB;
- after: 2,122 files, 274.5 MB;
- freed: 933.1 MB.

Verification:

- `python scripts/validate_trajectory.py trajectories` passed for all 129
  trajectory JSON files;
- `paper/main.pdf` and `paper/main_agenticdev.pdf` remain 11-page US Letter
  AgenticDev builds;
- `paper/main_figures_clean.pdf` remains a 20-page US Letter generic build.

Superseded note:

- The June 16 cleanup retained `runs/`, but that was superseded by the
  post-artifact cleanup on July 10, 2026 after validated trajectory records and
  the compact artifact package had been created.

Use:

- `results/project_cleanup_2026_06_16.md`

## Post-Artifact Local Cleanup Completed

Completed on July 10, 2026.

Deleted after creating and validating the compact AgenticDev artifact package:

- `runs/` raw run artifacts: 1,330 files, 249.96 MB;
- `data/external/`: 78 files, 16.38 MB.

Retained:

- `github_export/` for the GitHub-facing repository upload;
- `artifact_agenticdev2026/` for the compact experiment/data artifact;
- `trajectories/`, `tasks/`, `manifests/`, `data/pybughive*/`, paper source,
  and paper PDFs.

Verification after deletion:

- root `tasks`, `trajectories`, and `manifests` passed schema validation;
- artifact `tasks`, `trajectory_sets/primary_first6`,
  `trajectory_sets/structural_control_gpt55`, and `manifests` passed schema
  validation.

Use:

- `results/project_cleanup_2026_07_10_post_artifact.md`

## GitHub Preparation Completed

Completed on June 16, 2026.

The project now has a cleaner GitHub-facing structure without deleting local
experiment evidence.

Added repository hygiene files:

- `README.md`
- `.gitignore`
- `.gitattributes`
- `requirements.txt`
- `docs/PROJECT_STRUCTURE.md`
- `docs/GITHUB_PREP.md`
- `scripts/create_github_export.py`

Additional local cleanup:

- deleted old rendered inspection screenshots from `results/*.png`;
- deleted the root `logs/` directory containing process logs and PID files;
- deleted Python bytecode caches generated during validation.

Generated clean export:

- `github_export/`
- 1,000 files after adding the July 10, 2026 AgenticDev artifact folder;
- approximately 4 MB;
- excludes `runs/`, `logs/`, `workspaces/`, `data/external/`,
  PDFs, PNGs, logs, PID files, and bytecode caches.

Regenerate with:

```powershell
py scripts/create_github_export.py --force
```

Verification:

- root `tasks`, `trajectories`, and `manifests` all pass validation;
- `github_export/` `tasks`, `trajectories`, and `manifests` all pass
  validation;
- `scripts/create_github_export.py` passes Python bytecode compilation.

July 10, 2026 note:

- Source files, review reports, and manuscript index were updated after the P0
  revision.
- The latest export run copied 1,000 files and skipped 219 generated/local
  files after adding `artifact_agenticdev2026/`.
- Regenerate `github_export/` after any later handoff/report edit so the export
  package is not stale.

Use:

- `results/github_prep_2026_06_16.md`

## AgenticDev 2026 Format Adaptation Completed

Completed on June 8, 2026.

Target:

- AgenticDev 2026, co-located with ASE 2026;
- Full Paper;
- anonymous ACM `sigconf` review format;
- 10 manuscript pages plus up to 2 references-only pages.

Completed changes:

- migrated `paper/main.tex` to
  `\documentclass[sigconf,review,anonymous,pbalance]{acmart}`;
- added AgenticDev conference metadata, ACM CCS concepts, keywords, numeric ACM
  citations, and the ACM reference style;
- added figure descriptions for accessibility;
- added Conclusion, AI-Assistance Disclosure, and a final Data Availability
  Statement;
- compressed Limitations to four focused subsections;
- removed unapproved author/funding/competing-interest placeholders from the
  compiled submission;
- cleared unassigned DOI and ISBN placeholders;
- retained the empirical claim boundaries and separation between the primary
  five-method experiment and supplementary `gpt-5.5` structural control.

Verified output:

- `paper/main_agenticdev.pdf`;
- rebuilt July 10, 2026;
- 11 US Letter pages total;
- pages 1-10 contain manuscript content;
- page 11 contains only references;
- no undefined citations/references or overfull horizontal boxes;
- pages 1, 3, 6, 7, 10, and 11 visually inspected.

Use:

- `paper/reviews/agenticdev_2026_format_report_2026_06_08.md`
- `paper/BUILD.md`

## Environment And Safety Notes

- PyBugHive reproduction has used WSL/Linux-compatible Python environments where necessary.
- Docker Desktop and Windows virtualization settings caused unrelated machine/game concerns earlier in the project.
- Do not enable, disable, install, or reconfigure Docker Desktop, Hyper-V, Virtual Machine Platform, WSL features, boot configuration, or virtualization-related Windows settings without explicit user approval and a concrete change list.
- Do not assume an experiment or download is currently running. Check processes and artifact timestamps before resuming a run.
- Python 3.14 alone is not assumed compatible with historical benchmark dependencies; use the task's pinned or verified Python environment.

## What This Handoff Does Not Preserve

- It is not a verbatim transcript of every prior conversation.
- It does not preserve transient web-search result identifiers between conversations.
- It does not preserve hidden model reasoning.
- It does preserve the operational state needed to continue: goals, evidence, code assets, manuscript assets, claim boundaries, incomplete work, safety constraints, and next commands.

## Obsolete Start Prompt

Use this exact prompt:

```text
请先阅读 SESSION_HANDOFF.md、paper/manuscript_index.md、
paper/sections/result_claims_guardrails.md 和
paper/reviews/quick_review_intro_abstract_2026_06_03.md。

然后继续上一次未完成的任务：
Use $deep-research lit-review mode and $paper-analyst.
围绕 low-shot procedural skill transfer、agent memory、reflection、
trajectory-to-skill induction 和 language-agent debugging，
检索并核验 Related Work 文献，形成文献矩阵、对比表、verified sources
和 research gap。禁止虚构引用。
```

The block above is retained only as historical mojibake and must not be used.

## Start Prompt For The Next Conversation

Use this exact prompt:

```text
Read SESSION_HANDOFF.md, paper/manuscript_index.md,
paper/sections/result_claims_guardrails.md, and
paper/reviews/p0_revision_report_2026_07_10.md.
Then prepare the anonymized artifact package/link and complete AgenticDev
submission metadata without changing the empirical claim boundaries.
```

## Useful Project Entry Points

- Overall manuscript status: `paper/manuscript_index.md`
- Claim boundaries: `paper/sections/result_claims_guardrails.md`
- Experiment separation: `paper/tables/experiment_ledger.md`
- Current Introduction: `paper/sections/introduction.md`
- Current Method: `paper/sections/method.md`
- Current Results: `paper/sections/results.md`
- Integrated LaTeX driver: `paper/main.tex`
- Latest verified two-page poster PDF:
  `paper/agenticdev2026_paper12_camera_ready.pdf`
- Poster camera-ready source: `paper/main_poster.tex`
- Reviewer-revised full manuscript PDF: `paper/main_revised_reviews.pdf`
- Original submitted full-paper PDF: `paper/main_agenticdev.pdf`
- Pre-venue generic PDF: `paper/main_figures_clean.pdf`
- Earlier viewer-locked PDF: `paper/main.pdf`
- LaTeX build report: `paper/reviews/latex_build_report_2026_06_08.md`
- Full consistency audit:
  `paper/reviews/full_manuscript_consistency_report_2026_06_08.md`
- Latest quick review: `paper/reviews/quick_review_intro_abstract_2026_06_03.md`

## Current Status: AgenticDev Poster Camera-Ready Revision

Updated on September 9, 2026. This section supersedes older submission-status
notes above.

- Paper #12 received one weak-accept and one accept review, then was accepted
  for an in-person poster because the one-day workshop reached capacity.
- The production category is `Extended Abstract (2 pages)`. The portal accepted
  an upload on September 9, 2026; the corrected PDF, source ZIP, and CCS XML
  still need to replace that upload and pass the external checker. The workshop
  poster session is scheduled for October 12, 2026, in Munich.
- `paper/main_poster.tex` is the current source, and
  `paper/agenticdev2026_paper12_camera_ready.pdf` is the upload-ready,
  non-anonymous two-page camera-ready PDF. The older `paper/main_poster.pdf`
  is superseded.
- `paper/main_revised_reviews.pdf` is the corresponding 11-page full revision;
  it is not the file to upload for the two-page proceedings slot.
- The reviewer revision adds Wilson solve-rate intervals, exact paired
  task-resampling intervals, medians, leave-one-task-out sensitivity, an
  explicit comparison with the human checklist, single-annotator disclosure,
  and outlier sensitivity for the structural control.
- The revisions do not claim repeated-seed evidence, broader bug-family
  coverage, or independent negative-transfer annotation because those data do
  not exist.
- Reproducible uncertainty analysis is implemented in
  `scripts/analyze_review_uncertainty.py`; generated outputs are
  `results/reviewer_uncertainty_analysis.json` and
  `paper/tables/reviewer_uncertainty_analysis.md`.
- Response and verification records are in
  `paper/reviews/agenticdev_camera_ready_response_2026_08_25.md` and
  `paper/reviews/agenticdev_camera_ready_verification_review_2026_08_25.md`.
- Final QA: the poster PDF has two US Letter pages, embedded Type 1 fonts, no
  overfull boxes, no undefined citations/references, no visible overlap, and
  visually balanced final-page columns. All trajectory, task, and manifest
  validators pass.
- The verified source upload archive is
  `paper/submission/agenticdev_camera_ready_source.zip`. It contains exactly
  `main.tex`, `references.bib`, `main.bbl`, `acmart.cls` v2.18, and
  `ACM-Reference-Format.bst`; rebuilding a fresh extraction produces the same
  two-page article text without blocking LaTeX diagnostics.

ACM eRights was completed on September 9, 2026. The final source now uses
CC-BY (`\setcopyright{cc}` and `\setcctype{by}`), DOI
`10.1145/3843282.3844421`, ISBN `979-8-4007-2985-0/2026/10`, and the exact
ACM-generated conference and book-title fields. The paper-specific Author
Instructions were also applied: `sigconf,screen,pbalance`, `microtype`, submission ID,
received/accepted dates, corresponding-author status, ORCID, default-size
table/figure text, and removal of the Figure 1 frame. The source also uses the
corrected ACM CCS identifiers for `Software testing and debugging`
(`10011007.10011074.10011099.10011102.10011103`) and `Intelligent agents`
(`10010147.10010178.10010219.10010221`). The exact ACM conference and
book-title commands are each on one physical source line so the production
checker can parse them. The refreshed source ZIP has SHA-256
`CF39C1A13AA17544ACEC0B408B934694BE60326431AAEF42E91DB634C0A7378A`.
The submission checklist and form-ready CCS XML are in
`paper/submission/agenticdev_camera_ready_compliance_checklist.md` and
`paper/submission/agenticdev_ccs.xml`.
In-person attendance remains unresolved because the author indicated that
travel to Germany may not be possible; obtain a written answer from the chairs
before assuming remote presentation is allowed.

## Project Page Status

Updated on September 9, 2026.

- The Trace2Skill academic project page is implemented at `docs/index.html`
  with responsive styles and vanilla JavaScript under `docs/static/`.
- It presents the camera-ready title, author, AgenticDev poster status, method,
  primary five-condition results, uncertainty, negative transfer, structural
  control, limitations, abstract, DOI, PDF, and BibTeX without exceeding the
  paper's empirical claim boundaries.
- Reused paper figures are copied to `docs/static/images/`; the page PDF is
  `docs/static/pdfs/trace2skill-paper.pdf`.
- `scripts/create_github_export.py` preserves project-page PDF/PNG media while
  continuing to exclude generated PDFs and screenshots elsewhere.
- The layout is adapted from the Academic Project Page Template. Attribution
  and the page-specific CC BY-SA 4.0 notice are in
  `docs/PROJECT_PAGE_LICENSE.md` and the page footer.
- Publish with GitHub Pages from the default branch's `/docs` folder. The
  expected public URL is `https://damogu123.github.io/trace2skill/`.

## GitHub Repository Audit

Updated on September 9, 2026.

- The public repository is `https://github.com/damogu123/trace2skill`, and the
  project page is `https://damogu123.github.io/trace2skill/`.
- The root `README.md` is now the Chinese project overview. It documents the
  research design, exact primary and structural-control results, validation and
  recomputation commands, limitations, licenses, DOI, and citation entry.
- A release-ready `CITATION.cff` was added and validated against CFF schema
  version 1.2.0. It identifies the repository as software and the AgenticDev
  extended abstract as the preferred citation.
- GitHub Actions validation is defined in `.github/workflows/validate.yml`.
  It compiles the scripts, validates top-level and packaged records, verifies
  the artifact inventory and project page, and checks that generated result
  files are reproducible.
- `scripts/validate_artifact_inventory.py` verifies every listed file's path,
  size, and SHA-256 digest and detects unlisted files.
- `scripts/validate_project_page.py` checks local resources, fragment targets,
  duplicate IDs, JSON-LD, SVG XML, the linked PDF header, and the Chinese HTML
  language declaration.
- A packaging bug was fixed in `scripts/create_agenticdev_artifact.py`: the
  nested artifact `.gitignore` no longer excludes the 50 prompt files under
  `artifact_agenticdev2026/prompts/runs/`. The regenerated inventory contains
  495 entries and passes complete hash verification.
- When the space-heavy local `runs/` directory is absent, the same generator
  now preserves the previously verified 11-row raw-run size inventory instead
  of replacing it with an empty table.
- `scripts/make_paper_results.py` now preserves the camera-ready primary table's
  top-of-page placement (`[t]`) when results are regenerated.
- The audit did not create new empirical evidence. Multi-seed runs,
  cross-project evaluation, broader bug families, and a second annotator remain
  future work rather than repository omissions.
