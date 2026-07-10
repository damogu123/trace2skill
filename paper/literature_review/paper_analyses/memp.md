# Memp: Exploring Agent Procedural Memory

## Basic Information

- Authors: Runnan Fang, Yuan Liang, Xiaobin Wang, Jialong Wu, Shuofei Qiao,
  Pengjun Xie, Fei Huang, Huajun Chen, and Ningyu Zhang
- Year: 2026
- Venue: Findings of ACL 2026
- Access: Full text
- Sources:
  https://arxiv.org/abs/2508.06433 and
  https://openreview.net/forum?id=aaij11qBCl

## One-Sentence Summary

Memp systematically compares procedural-memory representations and update
strategies for learning reusable procedures from positive and negative
trajectories.

## Problem And Method

The paper distinguishes procedural memory from factual or episodic memory and
distills trajectories into both fine-grained instructions and higher-level
script-like abstractions. It studies how a memory repository is built,
retrieved, updated, corrected, and deprecated as experience accumulates.

## Evaluation

The full text evaluates analogous tasks in TravelPlanner and ALFWorld. It
reports success, efficiency, representation choices, and memory-strategy
ablations.

## Strengths

- Directly establishes procedural memory as an agent-memory research object.
- Compares representation and update choices rather than treating memory as a
  single prompt.
- Treats correction and deprecation as part of lifelong memory maintenance.

## Limitations Relative To This Paper

- Does not evaluate real software debugging.
- The setup is continual and update-oriented, not a fixed low-shot artifact
  induced once and deployed unchanged.
- It does not include reflection length-matching or shuffled-organization
  controls.
- Stale experience can be corrected or deprecated, but individual held-out
  failures are not labeled as negative transfer caused by memory.

## Role In Related Work

Memp invalidates any claim that procedural memory itself is novel. Cite it as
direct conceptual precedent and position the current paper as a debugging
evaluation contribution.
