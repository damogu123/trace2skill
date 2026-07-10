# AutoGuide: Automated Generation and Selection of Context-Aware Guidelines

## Basic Information

- Authors: Yao Fu, Dong-Ki Kim, Jaekyeom Kim, Sungryull Sohn, Lajanugen
  Logeswaran, Kyunghoon Bae, and Honglak Lee
- Year: 2024
- Venue: NeurIPS 2024
- Access: Full text
- Source: https://openreview.net/forum?id=mRIQz8Zd6O

## One-Sentence Summary

AutoGuide distills interaction trajectories into reusable guidelines and
selects guidelines according to the agent's current context.

## Problem And Method

The paper argues that generic guidelines are not uniformly useful across
states. It performs offline guideline generation from trajectories, associates
guidelines with contextual states, and retrieves relevant guidance while the
agent acts.

## Evaluation

The paper evaluates guideline generation and selection on interactive-agent
benchmarks, with final task performance as the main outcome and ablations over
guideline use and selection.

## Strengths

- Explicitly models when guidance applies.
- Separates generation from context-aware selection.
- Closely precedes the trigger component of `SKILL.md`.

## Limitations Relative To This Paper

- The artifact is a collection of conditional tips rather than an ordered
  diagnosis-edit-test procedure.
- Failure or stopping conditions are not a required representational field.
- No explicit per-task negative-transfer annotation or debugging-specific
  process evaluation is provided.

## Role In Related Work

AutoGuide prevents the paper from claiming novelty for applicability-aware
natural-language memory. The distinction must be the complete procedural
contract and debugging evaluation.
