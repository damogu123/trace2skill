# AgenticDev-Focused Skill Review

Date: 2026-06-16

Skills used:

- `academic-paper-reviewer`: full review stance with EIC, methodology, domain,
  practical-impact, and devil's-advocate perspectives.
- `quality-editor`: terminology, citation, claim-boundary, build, and
  submission-readiness audit.

Venue checked:

- AgenticDev 2026 official page:
  https://conf.researchr.org/home/ase-2026/agenticdev-2026
- Relevant local target remains consistent with the page: ACM
  `sigconf,review,anonymous`, Full Paper, 10 pages of content plus up to two
  references-only pages.

## Editorial Decision Simulation

**Current recommendation for AgenticDev 2026 Full Paper:** borderline positive
after focused cleanup; not yet a comfortable accept.

The manuscript is well aligned with the workshop topic and is unusually honest
about claim boundaries. Its strongest contribution is a reproducible evaluation
protocol for low-shot procedural memory in language-agent debugging, not a
dominant new method result. The current evidence scale is small, but that is
mostly acceptable for a focused workshop if the paper foregrounds protocol,
artifact quality, and process measurement.

## Major Strengths

1. **Clear scoped contribution.** The Introduction and Discussion consistently
   frame `SKILL.md` as a trajectory-induced procedural memory artifact rather
   than as a generic prompt.
2. **Good claim discipline.** The paper does not claim universal superiority,
   statistical significance, or solve-rate dominance over Reflexion/generic
   checklist.
3. **Useful negative-transfer framing.** The `black_132` failure gives the
   protocol a concrete diagnostic role instead of hiding a weakness.
4. **Related Work is credible.** It no longer pretends procedural memory is
   unstudied; it narrows the gap to a joint evaluation setting.
5. **Build and submission shell are close.** A fresh build produced an 11-page
   US Letter PDF: 10 content pages plus one references page.

## Major Issues

### 1. Evidence scale remains the main reviewer risk

Location:

- `paper/sections/limitations.tex`, lines 6-14
- `paper/sections/results.tex`, lines 4-9

The paper is transparent that the primary analysis has six tasks and one
execution seed, which is good. Still, a reviewer can reasonably argue that
process-efficiency differences may be run-specific. This is the largest
scientific weakness.

Recommended fix before submission:

- Keep the workshop framing explicit: this is a protocol paper with an initial
  hard-smoke study.
- In the Abstract or Introduction, add one short phrase such as "initial
  controlled study" if space permits.
- Do not try to sell the paper as a mature benchmark result.

### 2. The `K=3` training trajectories are under-specified

Location:

- `paper/sections/method.tex`, line 55

The Method says the skill is induced from `K=3` redacted training trajectories,
but the reader cannot immediately see which tasks formed the training set, how
they differ from the held-out six, or where the redaction artifacts are
documented.

Recommended fix:

- Add a small sentence or footnote listing the three training task IDs and
  confirming they are disjoint from the held-out tasks.
- If page pressure is tight, point to a table in the artifact package.

### 3. Negative-transfer annotation needs one more operational detail

Location:

- `paper/sections/method.tex`, lines 98-100
- `paper/sections/limitations.tex`, lines 30-32

The taxonomy is defined, and the limitations correctly admit that labels were
not independently assigned by multiple annotators. What is still missing is a
compact statement of who assigned the label and what evidence was inspected.

Recommended fix:

- Add one Method sentence: labels were assigned by inspecting the validated
  trajectory record, patch sequence, test outcomes, and mistake annotations
  under the predefined taxonomy.
- Keep the limitation about no inter-annotator agreement.

### 4. Artifact availability is not concrete yet

Location:

- `paper/sections/data_availability.tex`, lines 4-8

The paper says the submission is accompanied by an anonymized artifact package,
but there is no URL or artifact identifier in the manuscript. This is probably
acceptable only if the submission system has a separate artifact field.

Recommended fix:

- Before submission, create an anonymous archive from `github_export/`.
- Either add an anonymized URL in Data Availability or ensure the submission
  form contains the artifact link.
- If no artifact will be provided at review time, change "is accompanied by" to
  "will be accompanied by" or "will be released".

### 5. The supplementary structural-control table looks unfinished

Location:

- `paper/tables/hard_first6_structural_control_gpt55.tex`, lines 6-7
- `paper/sections/results.tex`, line 77

The prose rounds values nicely (`111,978`, `102,006`, `1.67`, `2.17`), but the
LaTeX table prints raw decimals such as `111978.3333`. This is not a scientific
error, but it weakens polish.

Recommended fix:

- Round `Cycles / solved` and `Failed patches / run` to two decimals.
- Render `Tokens / solved` as whole numbers with comma separators.
- Consider rendering `Solve rate` and `NT rate` as `100%` and `0%`.

## Reviewer Perspectives

### EIC Perspective

The paper is a plausible fit for AgenticDev because it evaluates agentic
debugging behavior, memory reuse, failure modes, and artifact-backed
reproducibility. The submission is stronger as a workshop paper than as a main
conference paper. The EIC concern is that the empirical claim is necessarily
small: six tasks, one primary model, one execution seed, and one bug family.

Likely decision after P0 cleanup: weak accept / borderline accept.

### Methodology Reviewer

The harness design is a strength: isolated checkouts, schema validation, final
test reruns, trajectory recording, process metrics, and explicit leakage rules.
The weak points are measurement validity and controls. Negative transfer is
single-annotator, cycles are best-effort summaries, and raw-trajectory retrieval
plus oracle skill are not part of the primary hard-smoke table.

Most important request from this reviewer: make the training/held-out split and
annotation protocol more explicit.

### Domain Reviewer

Related Work is now appropriately calibrated. It acknowledges Reflexion,
workflow memory, procedural memory systems, ReasoningBank, SWE-bench,
SWE-agent, BugsInPy, and PyBugHive. The gap is narrow but defensible: no cited
work jointly evaluates a fixed low-shot natural-language procedure induced from
debugging trajectories with held-out real-bug transfer, process cost, negative
transfer, and organization/length controls.

Most important request from this reviewer: keep saying "joint evaluation gap,"
not "procedural memory is new."

### Practical-Impact Reviewer

The artifact story is promising, especially after creating `github_export/`.
However, the paper needs the artifact path to be real at submission time. A
reviewer should be able to inspect schemas, prompts, memory artifacts,
trajectories, and metric scripts without seeing raw local logs or private
machine paths.

Most important request from this reviewer: package the anonymous artifact and
link it.

### Devil's Advocate

The strongest counterargument is:

> The result may be a carefully packaged prompt-engineering effect rather than
> evidence of transferable procedural skill. Auto SKILL.md ties solve rate with
> generic checklist and Reflexion, the shuffled version solves all six tasks
> under a stronger model, and the primary study has only six tasks. Therefore
> the paper should not claim a new memory method is superior; at most it shows
> that a structured artifact can be audited and can alter process metrics in a
> narrow setting.

The manuscript mostly answers this counterargument already. The answer should
remain: the contribution is the protocol, artifact constraints, process
measurement, and negative-transfer accounting.

## Quality-Editor Audit

| Check | Result |
| --- | --- |
| Main LaTeX build | Pass |
| Page count | 11 total: 10 content + 1 references |
| Page size | US Letter |
| Undefined citations/references | None after full build |
| Citation coverage | 18 BibTeX keys, 18 cited keys, no missing/orphan keys |
| Claim guardrails | Pass |
| Anonymity in compiled main | Pass; `declarations.tex` is not included |
| Main numerical consistency | Pass |
| Remaining build warnings | Nonfatal underfull boxes, one 1.534pt overfull vbox, one SVG page-group warning |
| BibTeX metadata warnings | 38 warnings for missing publisher/address/pages/volume fields |

The BibTeX warnings are not submission blockers, but they make the reference
section look less mature. Fill stable proceedings metadata where known; leave
true forthcoming/preprint entries clearly marked.

## P0 Revision Checklist

Do these before submission:

1. Add or submit the anonymized artifact link.
2. Specify the three training trajectories or point to the exact artifact table.
3. Add one sentence describing the negative-transfer annotation evidence source.
4. Round and format the structural-control table.
5. Clean up stable BibTeX metadata warnings where possible.

## P1 Nice-To-Have Improvements

1. Include or cite the common-solved pairwise table more visibly.
2. Add an artifact README explaining how to validate tasks, trajectories, and
   manifests from the anonymous package.
3. Mention model-version availability as a reproducibility caveat in one compact
   place, since the original `gpt-5.3-codex` setting became unavailable.

## Bottom Line

The manuscript is close to a credible AgenticDev workshop submission. It should
not be reframed as a broad performance paper. Its best identity is:

> a careful evaluation protocol and artifact-backed pilot study showing that
> low-shot trajectory-induced procedural memory can alter debugging process
> efficiency while also exposing negative transfer.

