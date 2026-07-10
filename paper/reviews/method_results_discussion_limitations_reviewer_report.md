# Reviewer Report: Method, Results, Discussion, and Limitations

## Review Mode

Skill used: `academic-paper-reviewer`, full-review style simulated sequentially.

Scope reviewed:

- `paper/sections/method.md`
- `paper/sections/results.md`
- `paper/sections/discussion.md`
- `paper/sections/limitations.md`
- `paper/sections/result_claims_guardrails.md`
- main result tables under `paper/tables/`

## Editorial Decision

**Main-conference decision if submitted now:** Weak reject / major revision.

**Workshop decision if framed honestly as a protocol paper plus controlled pilot:** Borderline accept to weak accept.

The current claim is much safer than an over-broad "SKILL.md beats Reflexion" claim. The paper now correctly frames the strongest evidence as process efficiency, not universal solve-rate superiority. However, for a top conference, the empirical base is still too narrow and the prompt-engineering counterargument is not fully neutralized because the most direct structural controls are defined but not included in the main hard-smoke result.

## Summary Assessment

The paper has a promising and coherent thesis: trajectory-induced natural-language `SKILL.md` can be studied as an inspectable procedural memory artifact for low-shot within-family debugging transfer. The Method section is unusually concrete for an early paper: task schema, trajectory schema, induction contract, harness, metrics, and leakage controls are all specified. The Results section is appropriately restrained and makes good use of common-solved efficiency comparisons. The Discussion and Limitations sections correctly prevent the claim from drifting into universal superiority.

The central remaining weakness is empirical sufficiency. Six same-model tasks from one PyBugHive `black` family can support a hard-smoke claim, but not yet a strong conference-level claim about procedural memory as a general approach. The reviewer concern will not be "the idea is bad"; it will be "this is an interesting pilot, but the controls and scale are not yet enough."

## Major Issues

### 1. The prompt-engineering objection is not fully defeated

Severity: **Major**

The paper says `SKILL.md` is not ordinary prompt engineering and frames it as a procedural memory artifact. This is conceptually defensible, but the current main result does not include the strongest control: `format_shuffled_skill`. In Method, that control is defined as future/appendix infrastructure rather than part of the hard-smoke result. Length-matched Reflexion controls prompt length, but it does not isolate whether the gain comes from the specific trigger/procedure/failure-mode organization.

Specific risk:

- `discussion.md` says the length-matched Reflexion control is "the most direct evidence" for the distinction.
- A reviewer will respond that the most direct evidence is actually format-shuffled SKILL.md or section-ablation, not length-matched Reflexion.

Required fix:

- Run `format_shuffled_skill` on the same first-six hard-smoke tasks under the same model if possible.
- If that is not possible, soften the claim to: "length-matched Reflexion controls for prompt length, while future format-shuffled controls are required to isolate section structure."
- Move `format_shuffled_skill` from "future control" to "planned-but-not-yet-run structural control" and avoid claiming the three-section structure is empirically isolated.

### 2. Six tasks from one project are not enough for a main-conference empirical claim

Severity: **Major**

The text acknowledges the scale limitation, which is good. But the Method and Results still need to make the current study's status unmistakable: this is a hard-smoke, not a full benchmark evaluation.

Specific risk:

- The phrase "does an induced procedural skill improve held-out repair behavior" can sound broader than the evidence.
- The result is a 5/6 vs 5/6 tie against two baselines, with efficiency improvements on solved tasks.
- The sample is too small for significance and too narrow for generality.

Required fix:

- For a workshop: title/subtitle should signal "controlled hard-smoke evaluation" or "protocol and pilot study."
- For a main conference: expand to at least 20-30 held-out tasks across multiple PyBugHive projects or bug families, or present this as one study among several.
- Report all verified candidate tasks and exclusion criteria to reduce cherry-picking concerns.

### 3. Task selection can look post-hoc

Severity: **Major**

The Discussion says earlier MVP tasks were too easy and the harder `black` slice was selected because it exposed method differences. That is honest, but a reviewer may read it as post-hoc benchmark construction.

Required fix:

- Move subjective "too easy" narrative to an appendix or replace it with objective criteria: patch complexity, failing-test specificity, full-test availability, reference-patch verification, and nontrivial formatter behavior.
- Add a table listing all candidate hard tasks, verified/excluded status, and exclusion reason.
- Include sensitivity analysis over all verified tasks when possible.

### 4. Negative-transfer annotation is promising but under-validated

Severity: **Major**

Negative transfer is one of the paper's strongest conceptual contributions, but the current evidence includes one explicit Auto SKILL.md negative-transfer case and lightweight annotation.

Required fix:

- Define "substantially more cycles/tokens" numerically in the annotation guide or Method.
- Add two-annotator labeling and Cohen's kappa for the final paper.
- Include at least two negative-transfer case studies if the expanded study yields them.
- Add an "uncertain" category rather than forcing ambiguous failures into negative transfer or non-negative transfer.

### 5. Solve-conditional efficiency metrics need an unsolved-task companion metric

Severity: **Moderate to Major**

Tokens per solved task and cycles per solved task are meaningful, but they condition on solved runs. The paper already adds common-solved comparisons, which helps. Still, a skeptical reviewer may worry that solve-conditional means can hide costs on failures or reward methods that solve an easier subset.

Required fix:

- Keep common-solved tables.
- Add an all-run companion metric such as capped cycles per task, capped tokens per task, failed patches per task, or PAR-style penalized cost.
- State the primary efficiency metric before reporting results.

## Claim Strength Audit

### Claims that are currently safe

- Auto SKILL.md ties the best solve rate on the six-task same-model slice.
- Auto SKILL.md is more token-efficient among solved tasks in the same-model aggregate.
- Auto SKILL.md reduces cycles and tokens on common-solved tasks relative to Reflexion-style memories.
- The protocol makes negative transfer visible.
- The current evidence supports an initial controlled within-family hard-smoke result.

### Claims that are still too strong or too vulnerable

- "Procedural organization matters beyond adding context" is plausible but not fully isolated without `format_shuffled_skill` or section ablation.
- "SKILL.md is not prompt engineering" should be framed operationally, not rhetorically. The stronger wording is: "We operationalize SKILL.md as an induced procedural memory artifact and evaluate prompt-format confounds through controls."
- "Improves held-out repair behavior" should be narrowed to "can improve process efficiency on a controlled within-family slice."
- "Without increasing negative transfer" should not appear as a goal statement unless paired with "while measuring negative transfer"; Auto SKILL.md has one negative-transfer failure.

## Specific Wording Revisions

1. In `method.md`, change:
   - "improves held-out repair efficiency without increasing negative transfer"
   - to: "improves held-out repair efficiency while making negative transfer measurable."

2. In `results.md`, keep:
   - "This is not evidence of solve-rate dominance."
   This sentence is important and should stay.

3. In `results.md`, change:
   - "supports the interpretation that procedural organization matters"
   - to: "is consistent with the interpretation that procedural organization may matter; a format-shuffled control provides the stricter test."

4. In `discussion.md`, change:
   - "The length-matched Reflexion control is the most direct evidence"
   - to: "The length-matched Reflexion control is the currently available prompt-length control."

5. In `discussion.md`, change:
   - "This framing also helps avoid reducing SKILL.md to prompt engineering"
   - to: "This framing operationalizes SKILL.md as a procedural memory artifact rather than treating it as a hand-written prompt."

6. In `discussion.md`, change:
   - "Earlier MVP tasks were too easy"
   - to: "Earlier candidate tasks produced ceiling effects; the hard-smoke subset was selected using reproducibility and complexity criteria reported in Appendix X."

7. In `discussion.md`, change:
   - "procedural memory can help the agent compress the failure into the right invariant earlier"
   - to: "the case studies suggest that procedural memory may help the agent compress the failure into the right invariant earlier."

## Experiments That Should Be Added

### Minimum for a credible workshop paper

1. Add `format_shuffled_skill` on the same six hard tasks.
2. Add all-run capped efficiency metrics.
3. Add candidate-task/exclusion table.
4. Add negative-transfer annotation guide and at least one second annotator pass for the existing hard-smoke cases.
5. Keep the paper framed as an evaluation protocol plus controlled pilot.

### Minimum for a plausible main-conference submission

1. Rerun all seven verified hard tasks under one current model.
2. Run all eight methods: `no_memory`, `generic_checklist`, `reflexion`, `length_matched_reflexion`, `raw_trajectory_retrieval`, `format_shuffled_skill`, `oracle_skill`, and `auto_skill`.
3. Expand beyond `black` to at least three projects or bug families.
4. Add K-shot ablations: `K=1`, `K=3`, `K=5`, optionally `K=10`.
5. Add multiple seeds for training-trajectory selection and, if agent nondeterminism exists, run-level repeats.
6. Report paired nonparametric tests or bootstrap confidence intervals, clearly marked as exploratory if sample size remains small.
7. Include human-authored oracle skill as an upper bound and section-ablation skills to isolate Trigger Conditions, Procedure, and Failure Modes.

## Reviewer Persona Notes

### Editor-in-Chief

The contribution is timely and potentially publishable, but the current version is not yet a full empirical paper. Its best venue positioning is a workshop or short paper on evaluation protocols for agent memory. For main conference review, expand the benchmark and include structural controls.

### Methodology Reviewer

The harness and schemas are strong. The main statistical concern is small `n`, solve-conditional metrics, and missing structural controls. Add all-run penalized metrics and avoid significance language.

### Domain Reviewer

The framing around procedural memory is good, but Related Work must clearly distinguish Reflexion, Voyager-style skill libraries, trajectory summarization, and prompt engineering. The current Method/Discussion sections can carry the distinction, but only if format-shuffled or ablation controls are included.

### Devil's Advocate

The strongest counterargument is: "Auto SKILL.md is just a better prompt manually shaped by the authors; the experiment shows that this prompt was helpful on a hand-picked six-task Black slice, not that agents can self-evolve transferable skills." The current paper partially answers this through induction, leakage constraints, and length matching, but the answer is incomplete without format-shuffled controls, broader task families, and transparent task selection.

## Final Recommendation

Do not broaden the claim. The current sections are mostly safe if the paper is framed as:

> an evaluation protocol and controlled hard-smoke study showing that trajectory-induced procedural memory can match strong memory baselines while improving process efficiency, with explicit negative-transfer accounting.

To make the paper substantially stronger, prioritize one experiment before any writing polish: run `format_shuffled_skill` and, if feasible, `raw_trajectory_retrieval` on the same first-six hard tasks. That single addition would directly attack the "just prompt engineering" objection.
