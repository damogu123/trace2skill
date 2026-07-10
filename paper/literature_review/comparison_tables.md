# Comparison Tables

## Table 1: Closest Experience-To-Artifact Methods

| Method | Artifact | Natural language | Executable | Explicit applicability | Fixed during held-out evaluation | Low-shot induction | Debugging domain |
|---|---|---:|---:|---:|---:|---:|---:|
| Reflexion | Reflection text | Yes | No | No | No | Attempt-level | Partial: HumanEval only |
| ExpeL | Insights plus recalled trajectories | Yes | No | Partial | Yes | Multiple training tasks | No |
| AutoGuide | Conditional guidelines | Yes | No | Yes | Yes | No; offline corpus | No |
| AutoManual | Evolving instruction manual | Yes | No | Partial | No during building | No; iterative building | No |
| Agent Workflow Memory | Reusable workflows | Yes | No | Partial | Offline variant: yes | No; trajectory corpus | No |
| SkillWeaver | Website APIs | Descriptions only | Yes | Website-specific | Yes after exploration | No; iterative exploration | No |
| Memp | Playbook or script-like procedure | Yes / hybrid | Optional | Partial | Strategy dependent | No; continual updates | No |
| ReasoningBank | Reasoning strategies | Yes | No | Retrieval-based | Typically yes per evaluation episode | No; memory bank construction | Yes, SWE-bench Verified |
| Skill-Pro | Activation-execution-termination skill | Hybrid | Tool-oriented | Yes | Evolved during training, reused at test | No; contrastive corpus | No |
| LEGOMem | Agent-specific procedural modules | Structured memory | Tool calls | Role-conditioned | Yes after memory construction | No; trajectory corpus | No |
| This paper | Trigger-procedure-failure-mode `SKILL.md` | Yes | No | Yes | Yes | Yes, few trajectories | Yes, PyBugHive debugging |

`Low-shot induction` means that the artifact itself is induced from a small,
fixed set of prior trajectories. It does not mean that the base model is used
few-shot.

## Table 2: Evaluation Coverage

| Method | Held-out transfer | Final success | Steps/cycles | Tokens/cost | Failed actions/patches | Explicit negative-transfer outcome | Length control | Structure control |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Reflexion | Partial | Yes | Sometimes | No | No | No | No | No |
| ExpeL | Yes | Yes | Limited | No | No | No | No | No |
| AutoGuide | Yes | Yes | Limited | No | No | No | No | No |
| AutoManual | Yes | Yes | Learning dynamics | Limited | Rule edits | No | No | No |
| Agent Workflow Memory | Yes | Yes | Yes | Limited | No | Compatibility analysis only | No | No |
| Memp | Yes | Yes | Yes | No | Update ablations | No | No | Representation variants |
| ReasoningBank | Yes | Yes | Yes | Yes | No | Noise/degradation ablation only | No | No |
| Skill-Pro | Yes | Yes | Skill-use metrics | Limited | Verification reward | No | No | Component ablations |
| LEGOMem | Yes | Yes | Yes | Not central | Workflow execution | No | No | Placement/module ablations |
| This paper | Yes | Yes | Diagnosis-edit-test cycles | Yes | Yes | Yes, per task | Yes | Supplementary shuffled control |

## Table 3: Transfer Unit And Domain

| Work | Experience unit | Reused unit | Transfer granularity | Domain |
|---|---|---|---|---|
| Reflexion | Failed/successful attempt | Verbal reflection | Later attempt or episode | Reasoning, coding, sequential decisions |
| ExpeL | Cross-task trajectory | Insight and exemplar | New task in benchmark family | Alfworld, WebShop, HotpotQA |
| AutoGuide | State-action trajectory | Conditional guideline | New task/state | Interactive agents |
| AutoManual | Builder-task interaction | Manual rule | Unseen task/environment instance | ALFWorld, WebArena |
| Voyager | Embodied execution | Code skill | New goal in same world | Minecraft |
| LearnAct | Interactive trajectory | Action function | New benchmark task | Alfworld, PDDL, Jericho |
| Agent Workflow Memory | Agent trajectory | Workflow | New task or website | Web and general assistants |
| SkillWeaver | Website exploration | API skill | New task on explored site | WebArena |
| Memp | Task trajectory | Instruction/script repository | Analogous task | TravelPlanner, ALFWorld |
| ReasoningBank | Success/failure trajectory | Reasoning strategy | New task across benchmarks | General agents and SWE-bench |
| Skill-Pro | Contrasting trajectories | Scoped procedural skill | Held-out task | Interactive agents |
| LEGOMem | Workflow trajectory | Agent-specific memory unit | New workflow | OfficeBench |
| This paper | Debugging trajectory | Natural-language `SKILL.md` | Within-family held-out bug | Python debugging |

## Trend Summary

1. The field has moved from storing reflections or exemplars toward explicit
   guidelines, manuals, workflows, and procedural skills.
2. Applicability modeling has become more explicit: AutoGuide uses state-aware
   selection, SkillWeaver uses preconditions, Skill-Pro adds activation and
   termination, and this paper encodes trigger and failure-mode sections.
3. Efficiency is no longer absent from the literature. Several papers report
   steps, API calls, tokens, or task efficiency, with ReasoningBank providing the
   closest software-engineering efficiency comparison.
4. Harmful memory is recognized as retrieval noise, path dependence,
   incompatibility, or degradation. The remaining methodological opportunity
   is to attribute harm to a memory condition at the held-out task level.

## Handoff To Related Work Writing

The Related Work section should use four subsections:

1. Reflection and experiential memory.
2. Guidelines, manuals, workflows, and procedural skills.
3. Language-agent software engineering and debugging benchmarks.
4. Evaluation gap: fixed low-shot procedural artifacts, process metrics,
   negative transfer, and artifact controls.

Avoid claiming that this paper introduces procedural memory as a concept.
Claim instead that it contributes a controlled debugging-transfer evaluation
protocol for a specific natural-language procedural artifact.
