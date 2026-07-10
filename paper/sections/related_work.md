# Related Work

## Reflection and experiential memory

Language-agent memory first developed around verbal feedback and reusable
experience. Reflexion stores natural-language reflections from prior attempts
and reintroduces them as episodic memory, while Agent-Pro translates
interaction failures into policy-level reflection and optimization
[@shinn2023reflexion; @zhang2024agentpro]. These methods show that an agent can
improve without updating the base model, but their memory objects primarily
record retrospective lessons or policy adjustments.

Cross-task systems move from individual reflection toward abstraction over
multiple trajectories. ExpeL distills general insights from successes and
failures and combines them with retrieval of successful experiences
[@zhao2024expel]. Investigate-Consolidate-Exploit similarly consolidates
cross-task experience before retrieving it for new tasks [@qian2024ice].
Together, these systems establish trajectory-to-text experience compression.
They do not, however, require one frozen artifact to encode applicability,
ordered execution, and rejection conditions for a debugging family.

## Guidelines, workflows, and procedural skills

Later work gives experience a more operational structure. AutoGuide induces
context-aware guidelines from interaction trajectories and selects them
according to the current state [@fu2024autoguide]. AutoManual maintains an
instruction manual through rule addition, revision, merging, deletion, and
validation [@chen2024automanual]. Agent Workflow Memory is the closest
natural-language workflow precedent: it induces reusable workflows from agent
trajectories in offline and online settings and retrieves them for later tasks
[@wang2025workflowmemory]. These systems demonstrate that natural-language
memory can express more than retrospective reflection, including conditional
guidance and multi-step workflows.

A parallel line of work stores executable or structured skills. Voyager builds
an executable skill library for lifelong Minecraft exploration, and LearnAct
creates and revises callable actions for interactive environments
[@wang2024voyager; @zhao2024learnact]. SkillWeaver discovers, practices, and
distills website-specific APIs for later web tasks [@zheng2025skillweaver].
These systems emphasize reliable invocation and reuse, but their artifacts are
executable capabilities rather than fixed natural-language debugging
procedures.

Procedural memory is now an explicit object of study. Memp compares
fine-grained instructions with higher-level script-like abstractions and
studies how a memory repository is built, retrieved, updated, corrected, and
deprecated [@fang2026memp]. Skill-Pro represents skills through activation,
execution, and termination conditions and maintains them through verification
and score-based updates [@mi2026skillpro]. LEGOMem decomposes workflow
trajectories into modular memory units allocated across orchestrators and task
agents [@han2026legomem]. Our work therefore does not claim to introduce
procedural memory. It studies a narrower artifact and evaluation setting:
low-shot induction of a frozen natural-language `SKILL.md` for held-out
debugging tasks.

## Language-agent debugging and benchmarks

Repository-level software engineering provides a demanding test of agent
transfer. SWE-bench evaluates whether language models can resolve real GitHub
issues under repository tests, while SWE-agent shows that the
agent-computer interface materially affects repair behavior
[@jimenez2024swebench; @yang2024sweagent]. ReasoningBank connects this domain
to memory research by evaluating reusable reasoning memories on SWE-bench
Verified and reporting success together with interaction steps and token
consumption [@ouyang2026reasoningbank]. It also finds that retrieving excessive
or noisy experience can reduce performance, making it the closest prior
comparison for efficiency and harmful memory in software repair.

Reproducible bug databases support more controlled debugging studies.
BugsInPy packages real Python defects with environments and tests, and
PyBugHive expands this line with a larger manually validated collection of
reproducible Python bugs [@widyasari2020bugsinpy; @antal2024pybughive].
These benchmarks provide bug provenance and executable validation, but they do
not define how an agent should induce or evaluate transferable memory. We use
PyBugHive to construct a within-family setting in which training trajectories
and held-out failures remain related without being identical.

## Evaluation gap

Prior work already evaluates more than final success. Cross-task memory systems
report actions, steps, API calls, tokens, or task efficiency, and several
papers recognize that stale, incompatible, or noisy memory can be harmful
[@chen2024automanual; @wang2025workflowmemory; @fang2026memp;
@ouyang2026reasoningbank]. The remaining gap is therefore not the existence of
procedural memory, efficiency measurement, or memory degradation in isolation.

Within our verified corpus, we did not identify a study that jointly evaluates
five elements: (1) a fixed natural-language procedure induced from a few
debugging trajectories, (2) transfer to held-out bugs in a controlled software
family, (3) repair success together with diagnosis-edit-test cycles, token
cost, and failed patches, (4) explicit per-task attribution of negative
transfer to the memory condition, and (5) controls for generic advice,
reflection-style memory, memory length, and procedural organization. Our
contribution targets this joint evaluation gap. The empirical study remains
deliberately narrow, so the claim concerns a reproducible protocol and an
initial within-family hard-smoke evaluation rather than general superiority
over prior memory systems.
