# Skill-Pro: Learning Reusable Skills from Experience via Non-Parametric PPO

## Basic Information

- Authors: Qirui Mi, Zhijian Ma, Mengyue Yang, Haoxuan Li, Yisen Wang, Haifeng
  Zhang, and Jun Wang
- Year: 2026
- Venue: ICML 2026, accepted
- Access: Full text
- Source: https://arxiv.org/abs/2602.01869
- Version note: current title supersedes the earlier "ProcMEM" title.

## One-Sentence Summary

Skill-Pro evolves reusable procedural skills with explicit activation,
execution, and termination components using contrastive trajectory analysis
and a non-parametric PPO-style update.

## Problem And Method

The paper identifies two core problems in reusable skills: invoking a skill in
the wrong state and executing a useful skill unreliably. It formalizes a
Skill-MDP, generates candidates through semantic gradients, verifies them with
a PPO Gate, and maintains a compact library through score-based updates.

## Evaluation

The paper evaluates held-out interactive-agent tasks and reports task success,
reuse behavior, invocation quality, and component ablations.

## Strengths

- Activation and termination directly model applicability boundaries.
- Uses positive/negative trajectory contrast.
- Separates discovery, execution, and verification.

## Limitations Relative To This Paper

- It is not a real debugging study.
- The artifact is a skill library integrated with tool execution, rather than
  a frozen natural-language `SKILL.md`.
- It does not report explicit memory-attributed negative-transfer outcomes.
- It does not use length-matched reflection or shuffled-organization controls.

## Role In Related Work

Skill-Pro is the closest representational comparator. Trigger, procedure, and
failure modes should be described as related to, not preceding, its
activation-execution-termination decomposition.
