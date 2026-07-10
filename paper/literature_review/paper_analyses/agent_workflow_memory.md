# Agent Workflow Memory

## Basic Information

- Authors: Zora Zhiruo Wang, Jiayuan Mao, Daniel Fried, and Graham Neubig
- Year: 2025
- Venue: ICML 2025
- Access: Full text
- Sources:
  https://openreview.net/forum?id=NTAhi2JEEE and
  https://arxiv.org/abs/2409.07429

## One-Sentence Summary

Agent Workflow Memory induces reusable workflows from agent trajectories and
retrieves them to guide later tasks.

## Problem And Method

The paper treats workflow knowledge as a reusable memory type between raw
trajectory replay and generic reflection. It provides offline and online
variants: workflows can be induced from prior trajectories before deployment
or incrementally added during use.

## Evaluation

Experiments cover WebArena, Mind2Web, and GAIA. Reported outcomes include task
success, progress, and process behavior. An appendix study mixes workflow
memories and finds that incompatible or irrelevant memories can impair some
tasks.

## Strengths

- Closest prior analogue to trajectory-induced natural-language procedures.
- Evaluates transfer across tasks and, in some settings, websites.
- Directly investigates workflow compatibility.

## Limitations Relative To This Paper

- Does not focus on low-shot real debugging trajectories.
- Does not define a fixed trigger-procedure-failure-mode artifact.
- Compatibility degradation is not operationalized as a per-task
  memory-attributed negative-transfer outcome.
- No prompt-length or organization-matched controls.

## Role In Related Work

This should be presented as the closest workflow-level precedent and discussed
before the paper states its evaluation gap.
