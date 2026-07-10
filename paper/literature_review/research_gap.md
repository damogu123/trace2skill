# Verified Research Gap

## Gap Verdict

The broad hypothesis that prior work has not studied procedural memory is
rejected.

By June 2026, Memp, Skill-Pro, and LEGOMem explicitly study procedural memory,
while AutoGuide, AutoManual, Agent Workflow Memory, Voyager, LearnAct, and
SkillWeaver induce closely related guidelines, manuals, workflows, or reusable
skills. ReasoningBank also evaluates reusable reasoning memory on SWE-bench
Verified and reports both task success and process cost.

The defensible gap is narrower and evaluation-centered.

## Supported Gap Statement

Within the 18-source verified corpus, we did not identify prior work that
jointly evaluates all of the following:

1. induction of a fixed natural-language procedural memory artifact from a
   small number of debugging trajectories;
2. transfer to held-out bugs within a controlled software family;
3. final repair success together with diagnosis-edit-test cycles, token cost,
   and failed patches;
4. explicit, per-task attribution of negative transfer to the memory
   condition;
5. controls for no memory, generic advice, reflection-style memory, memory
   length, and procedural organization.

This is an absence in the verified corpus, not a universal proof that no
related paper exists.

## What Is Already Established

### Reflection and experiential reuse

Reflexion and Agent-Pro show that verbal or policy-level reflection can improve
future decisions. ExpeL and ICE show that multiple trajectories can be
consolidated into reusable insights. Therefore, the paper should not claim
novelty for learning from textual feedback or cross-task experience.

### Guideline, manual, and workflow induction

AutoGuide, AutoManual, and Agent Workflow Memory already transform interaction
experience into reusable natural-language guidance. The distinction for
`SKILL.md` must rest on the operational contract: few source trajectories,
explicit trigger/procedure/failure-mode structure, frozen deployment, leakage
constraints, and controlled transfer evaluation.

### Procedural and executable skills

Voyager, LearnAct, SkillWeaver, Skill-Pro, Memp, and LEGOMem establish that
agents can discover, store, retrieve, and refine reusable skills or procedures.
The paper's artifact is not the first reusable skill memory. Its contribution
is the debugging-specific evaluation protocol and the inspectable
natural-language representation.

### Process efficiency

ICE reports API-call efficiency; Agent Workflow Memory and Memp report action
or task efficiency; ReasoningBank reports steps and token consumption,
including on SWE-bench Verified. The paper should
not say that existing work evaluates only final success. It can say that the
combination of repair cycles, token cost, failed patches, and explicit
negative-transfer attribution is not present in this corpus.

### Harmful or noisy memory

AutoManual discusses path dependence and distribution shift. Agent Workflow
Memory tests workflow compatibility. Memp uses negative trajectories and
anti-degradation updates. ReasoningBank shows that excessive retrieval can
introduce conflict or noise and reduce success. LEGOMem discusses irrelevant
retrieval.

These works weaken any claim that memory harm is ignored. The sharper claim is
that they generally treat harm as an ablation, retrieval, or update problem,
not as a held-out task outcome explicitly attributed to the memory condition.

## Closest Prior Work

### Agent Workflow Memory

This is the closest natural-language workflow analogue. It induces reusable
workflows from trajectories and tests cross-task transfer. The current paper
differs in low-shot construction, real debugging tasks, a frozen artifact, and
the combination of cycle/token/failed-patch/negative-transfer metrics.

### Memp

Memp is the closest conceptual precedent for procedural memory. It compares
playbook and script-like representations and studies update strategies. The
current paper should cite it as direct precedent, then distinguish its
debugging setting, fixed low-shot artifact, and artifact controls.

### ReasoningBank

ReasoningBank is the strongest evaluation comparator because it includes
SWE-bench Verified, success, steps, and token cost, and identifies degradation
from noisy or excessive memory. The remaining distinction is not "efficiency
in coding agents"; it is controlled low-shot procedural artifact induction
with explicit negative-transfer attribution and length/structure controls.

### Skill-Pro

Skill-Pro is the closest representation comparator because activation,
execution, and termination roughly parallel trigger, procedure, and failure
or stopping conditions. The current paper differs in artifact modality,
debugging domain, low-shot protocol, and evaluation controls.

## Recommended Paper Positioning

Use:

> Prior work has progressed from verbal reflection and trajectory retrieval to
> induced guidelines, manuals, workflows, and explicit procedural memories.
> However, in our verified corpus, these systems do not jointly test a fixed
> low-shot natural-language procedure on held-out real debugging tasks while
> measuring repair success, process efficiency, memory-attributed negative
> transfer, and length/organization controls. We target this evaluation gap
> rather than claiming to introduce procedural memory itself.

Avoid:

- "Existing work evaluates only solve rate."
- "No prior work studies procedural memory."
- "No prior work studies memory efficiency in software engineering."
- "No prior work recognizes harmful memory."
- "SKILL.md is the first trajectory-induced reusable agent skill."

## Residual Risks

- New 2026 work may further narrow the gap before submission.
- The phrase "low-shot" must be defined by the number of induction
  trajectories, not by in-context examples used by the base model.
- Because the current study uses six held-out tasks from one formatter family,
  the literature gap may be stronger than the empirical evidence. The paper
  should remain protocol-first.
