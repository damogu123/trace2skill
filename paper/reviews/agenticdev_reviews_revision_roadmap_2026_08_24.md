# AgenticDev 2026 Camera-Ready Revision Roadmap

## Overview

- Decision context: accepted as a two-page poster paper.
- Source comments: Review 12A and Review 12B.
- Cross-reviewer consensus: six tasks, one execution per condition, and weak
  evidence about stability are the dominant empirical limitations.
- Revision strategy: add task-level uncertainty and sensitivity analyses from
  existing validated trajectories, narrow claims, and avoid presenting those
  analyses as substitutes for repeated executions.

## Comment Tracking

| ID | Reviewer concern | Priority | Action | Status |
|---|---|---|---|---|
| R12A-1 / R12B-1a | Six tasks and one execution make headline rankings uncertain | P1 | Report Wilson solve-rate intervals, paired task-bootstrap intervals, medians, and leave-one-task-out ranges; state that these do not estimate run-to-run variance | DONE |
| R12A-1 / R12B-1b | Repeat configurations across seeds and expand task families | P2 | Not performed for the two-page camera-ready; narrow claims and retain as the primary future-work requirement | ACKNOWLEDGED LIMITATION |
| R12A-2 | It is unclear what is learned beyond a human checklist | P1 | Compare artifact content directly; state that solve rate and cycles tie and the checklist token interval crosses zero; remove causal learned-knowledge claim | DONE |
| R12B-2 | Negative-transfer labels use one annotator; add independent annotation | P2 | State one-annotator provenance in Method and Limitations; require independent annotation in future work | ACKNOWLEDGED LIMITATION |
| R12B-3 | Token cost is fragile because one outlier swings aggregates | P1 | Add token medians, leave-one-out sensitivity, and the black_193 exclusion result for the structural control | DONE |
| R12B-4 | Add confidence intervals | P1 | Add intervals next to headline solve and paired process results, explicitly labeled task-level and exploratory | DONE |
| R12A/B positive | Preserve fairness, leakage, length controls, negative-transfer transparency, and cautious framing | P2 | Retain these elements in the two-page version | DONE |

## Evidence Boundary

No new agent executions or second-annotator labels were fabricated. Repeated
seeds and inter-rater agreement remain unresolved empirical work. The added
uncertainty analysis is reproducible with
`py scripts/analyze_review_uncertainty.py`.

## Camera-Ready External Dependencies

- Confirm whether an author must attend in person or whether remote/proxy
  presentation is allowed.
- ACM eRights completed September 9, 2026. The generated block specifies
  CC-BY, DOI `10.1145/3843282.3844421`, ISBN
  `979-8-4007-2985-0/2026/10`, and proceedings dates
  `October 12--16, 2026`; these values are now in `main_poster.tex`.
