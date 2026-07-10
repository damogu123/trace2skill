# AutoManual: Constructing Instruction Manuals by LLM Agents

## Basic Information

- Authors: Minghao Chen, Yihang Li, Yanting Yang, Shiyu Yu, Binbin Lin, and
  Xiaofei He
- Year: 2024
- Venue: NeurIPS 2024
- Access: Full text
- Source: https://openreview.net/forum?id=Pwl9n4zlf5

## One-Sentence Summary

AutoManual uses a builder agent to incrementally construct and revise a rule
manual from environmental interaction, then applies that manual to unseen
tasks.

## Problem And Method

The paper targets experience accumulation without parameter updates. The
builder processes a sequence of tasks and performs rule addition, revision,
merging, deletion, and validation. A separate solver uses the resulting
manual.

The full text reports construction over 36 building tasks in the main setup,
despite the agent receiving a simple demonstration of the update protocol.

## Evaluation

Experiments use ALFWorld and WebArena, reporting success on seen and unseen
tasks, learning dynamics, and rule evolution.

## Strengths

- Directly studies a natural-language manual as persistent agent knowledge.
- Includes explicit maintenance operations rather than append-only memory.
- Discusses path dependence and distribution shift.

## Limitations Relative To This Paper

- It is not a low-shot artifact induced from a small fixed trajectory set.
- The manual evolves during a building phase rather than being frozen from a
  predefined few-shot induction protocol.
- Memory-induced harm is discussed but not labeled as a per-held-out-task
  negative-transfer outcome.

## Role In Related Work

AutoManual is a very close natural-language artifact precedent. The paper must
distinguish its fixed low-shot debugging protocol and controlled baselines, not
the existence of instruction-manual memory.
