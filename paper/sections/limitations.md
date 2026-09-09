# Limitations and Future Work

## Scale and experimental controls

The primary analysis contains six held-out tasks and one execution seed.
Accordingly, we report exact outcomes, Wilson solve-rate intervals, exploratory
task-resampling intervals, and sensitivity summaries rather than statistical
significance. These quantify variation across the selected tasks, not
run-to-run stochasticity. The seventh verified task is model-mixed, and the
`gpt-5.5` structural control covers only Auto SKILL.md and its
format-shuffled variant. A larger study should rerun every method under one
model, repeat agent and induction seeds, vary the `K=3` training set, and
estimate paired execution-level uncertainty. Raw-trajectory retrieval and a
human-authored oracle skill are also needed to separate procedural compression
from direct experience access and induction quality.

The human-written generic checklist is a strong unresolved control. It ties
Auto SKILL.md on solve rate and cycles, and the paired token interval crosses
zero. Although the induced artifact contains more explicit applicability
boundaries and failure classification, this pilot cannot show that those
elements encode knowledge unavailable to a competent human author. Larger
content and section ablations are required before making that claim.

## Benchmark and executor scope

The hard-smoke slice is restricted to one PyBugHive `black` formatter family
[@antal2024pybughive]. Its deterministic tests and localized invariants support
controlled within-family transfer, but they do not represent repository-wide
debugging. The observed effects may also depend on the coding agent, model
version, and tool policy: under `gpt-5.5`, shuffled skill content closed the
earlier solve-rate gap. Future evaluation should span multiple PyBugHive
projects, BugsInPy, and reproducible SWE-bench variants
[@widyasari2020bugsinpy; @jimenez2024swebench], as well as multiple agent
frameworks and model families.

## Measurement validity

Negative-transfer labels currently follow a predefined taxonomy but were
assigned by one annotator and were not independently adjudicated. Future
studies should use at least two annotators, report agreement, and separate
uncertain cases. Trace
records are also best-effort summaries: the harness validates schemas and
reruns tests, but a recorded cycle may contain substantial internal search.
Cycles should therefore be interpreted together with tokens, tool activity,
and failed patches. Direct instrumentation of reads, edits, and test executions
would improve trace fidelity.

## Induction and reproducibility

The skill was induced once from three redacted trajectories under a fixed
Trigger Conditions, Debugging Procedure, and Failure Modes contract. The
format-shuffled result shows that this organization is not necessary for
solvability under a stronger model. Section ablations, alternative training
sets, different values of `K`, and calibrated abstention tests are needed to
identify which procedural components transfer robustly. Finally, historical
Python dependencies and WSL execution create environment risk despite isolated
workspaces and reference-patch verification. Pinned container images would
better separate debugging difficulty from setup fragility.
