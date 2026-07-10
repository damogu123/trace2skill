# ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory

## Basic Information

- Authors: Siru Ouyang et al.
- Year: 2026
- Venue: ICLR 2026
- Access: Full text
- Sources:
  https://openreview.net/forum?id=jL7fwchScm and
  https://arxiv.org/abs/2509.25140

## One-Sentence Summary

ReasoningBank distills reusable reasoning strategies from both successful and
failed trajectories and learns to retrieve them through memory-aware
reinforcement learning.

## Problem And Method

The paper argues that raw trajectory memories are noisy and hard to reuse. A
self-judgment component labels outcomes and synthesizes compact reasoning
memories. Memory-aware RL then learns retrieval and use rather than relying
only on static similarity.

## Evaluation

The paper evaluates multiple agent benchmarks, including SWE-bench Verified.
It reports task success, interaction steps, token consumption, scaling
behavior, retrieval ablations, and the effect of memory-bank size.

## Strengths

- Strong cross-benchmark evaluation including software engineering.
- Reports both effectiveness and process cost.
- Shows that excessive or noisy memories can create conflict and reduce
  success.

## Limitations Relative To This Paper

- The memory objects are general reasoning strategies, not one frozen
  task-family procedural artifact.
- Memory construction is not framed as low-shot induction from a few debugging
  trajectories.
- Harm from retrieval noise is an aggregate ablation rather than explicit
  per-task negative-transfer attribution.
- No length-matched reflection or structure-shuffled artifact control.

## Role In Related Work

This is the strongest comparator against any claim that coding-agent memory
work lacks efficiency metrics. The current paper must claim a narrower joint
evaluation gap.
