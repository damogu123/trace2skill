# ExpeL: LLM Agents Are Experiential Learners

## Basic Information

- Authors: Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu,
  and Gao Huang
- Year: 2024
- Venue: AAAI 2024
- Access: Full text
- DOI: https://doi.org/10.1609/aaai.v38i17.29936

## One-Sentence Summary

ExpeL learns reusable natural-language insights from cross-task trajectories
and combines them with retrieval of successful experiences at inference time.

## Problem And Method

The paper addresses cross-task learning without weight updates. It collects
successful and failed trajectories, extracts general insights through
comparison, and updates insight confidence through reinforcement or
down-voting. At test time, the agent receives learned insights and retrieved
successful trajectories.

## Evaluation

Experiments cover ALFWorld, WebShop, and HotpotQA. The paper evaluates transfer
from training tasks to unseen tasks using final task performance.

## Strengths

- Directly studies inter-task experiential transfer.
- Combines abstraction with exemplar retrieval.
- Includes a mechanism for weakening misleading insights.

## Limitations Relative To This Paper

- The memory is a set of general insights rather than one fixed procedural
  artifact with an ordered debugging routine.
- Negative or misleading insights are handled through updates, not reported as
  memory-attributed held-out failures.
- Debugging cycles, token costs, and failed patches are not the evaluation
  focus.

## Role In Related Work

ExpeL is a key precedent for trajectory-to-natural-language abstraction and
should be cited before claiming that `SKILL.md` compresses experience.
