# Related Work Search Protocol

## Scope

This targeted literature review supports the paper:

**Evaluating Low-Shot Procedural Skill Transfer in Language-Agent Debugging**

Search date: 2026-06-07

Review mode: `deep-research` lit-review with `paper-analyst` structured extraction.

The review asks how prior work represents and transfers agent experience, with
special attention to:

- reflection and experiential memory;
- trajectory-to-guideline, manual, workflow, or skill induction;
- reusable procedural memory and skill libraries;
- language-agent coding and debugging;
- software-engineering benchmarks suitable for transfer evaluation.

## Search Sources

Primary-source search was conducted over:

- official conference proceedings and journal pages;
- OpenReview records;
- ACL Anthology;
- arXiv records and full-text HTML/PDF;
- official benchmark or author-hosted publication pages.

Semantic Scholar and general web search were used only for discovery and
deduplication hints. Inclusion and metadata verification required a primary
record.

## Query Families

Representative queries:

```text
"language agent" reflection memory transfer
"experiential learning" LLM agents trajectories insights
"state-aware guidelines" LLM agents
"instruction manual" LLM agent environmental learning
"agent workflow memory" trajectories
"procedural memory" LLM agents
"reusable skills" LLM agents experience
"skill library" web agent self-improve
"trajectory-to-skill" OR "trajectory-to-workflow" LLM agent
"language agent" debugging benchmark
SWE-bench SWE-agent PyBugHive BugsInPy
```

Title searches and backward/forward citation snowballing were then used for
the target families named in `SESSION_HANDOFF.md`.

## Inclusion Criteria

A source was included when it met at least one of these conditions:

1. It introduces an agent memory, reflection, guideline, manual, workflow, or
   reusable skill mechanism derived from interaction experience.
2. It evaluates transfer of learned experience to held-out or later tasks.
3. It introduces a coding/debugging agent or a reproducible software-defect
   benchmark relevant to the paper's evaluation setting.
4. It is a recent procedural-memory system that materially narrows the
   proposed research gap.

For method claims, the source needed an original paper or official record.
Preprints were retained only when directly relevant and clearly labeled.

## Exclusion Criteria

Sources were excluded from the core matrix when they:

- used reflection only for within-attempt answer refinement without persistent
  cross-task memory;
- discussed generic prompt engineering without experience-derived artifacts;
- addressed parametric fine-tuning only, with no inspectable agent memory;
- lacked an independently verifiable primary record;
- duplicated a later accepted or published version.

## Screening And Version Resolution

This is a targeted, reproducible review rather than a PRISMA systematic
review. Search-engine hit counts were not used because the result sets were
dynamic and heavily overlapping.

The final corpus contains 18 sources:

- 16 peer-reviewed, published, or formally accepted papers;
- 2 clearly labeled arXiv preprints.

Important version decisions:

- AutoGuide is represented by its NeurIPS 2024 paper, not the earlier workshop
  version.
- Memp is represented as an accepted ACL 2026 Findings paper.
- ReasoningBank is represented by its ICLR 2026 version.
- The work previously discoverable as "ProcMEM" is represented by its current
  title, **Skill-Pro**, accepted at ICML 2026.
- LEGOMem is represented by its AAMAS 2026 paper.
- Preprint and proceedings records for the same work were merged.

## Verification Procedure

Each included source received the following checks:

1. Exact title matched against an original paper or official venue record.
2. Author list and publication status matched against that record.
3. Method characterization was extracted from the abstract or full text.
4. Claims about transfer, efficiency, and failure behavior were checked in the
   paper rather than inferred from the title.
5. Access depth was recorded as `full-text` or `abstract/metadata`.
6. If the full text was not inspected, the analysis was restricted to claims
   supported by the official abstract.

## Extraction Fields

The matrix records:

- memory representation;
- source of experience;
- induction or update mechanism;
- artifact type;
- trigger or applicability modeling;
- transfer setting;
- task domain;
- evaluation metrics;
- negative-transfer treatment;
- limitation relative to the current paper.

## Limitations

- The review is deliberately focused on the closest method and benchmark
  families, not every agent-memory paper.
- Rapidly evolving 2025-2026 work may receive revised titles or publication
  metadata after the search date.
- Absence claims are therefore stated only for the 18-source verified corpus,
  not for all possible literature.
- Citation counts were not used because they change over time and are not
  needed for the paper's positioning claim.

## AI-Assistance Disclosure

Codex was used for search orchestration, source comparison, metadata checks,
and drafting these review artifacts. Inclusion and factual method claims were
restricted to the primary records listed in `verified_sources.md`. The review
has not yet received an independent human citation audit.
