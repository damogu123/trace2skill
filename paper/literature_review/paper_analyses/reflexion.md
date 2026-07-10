# Reflexion: Language Agents with Verbal Reinforcement Learning

## Basic Information

- Authors: Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath,
  Karthik Narasimhan, and Shunyu Yao
- Year: 2023
- Venue: NeurIPS 2023
- Access: Official abstract and proceedings metadata
- Source:
  https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html

## One-Sentence Summary

Reflexion converts feedback from previous attempts into verbal reflections
stored in episodic memory and reused in subsequent attempts.

## Problem And Method

The paper targets reinforcement from sparse or textual feedback without
updating model weights. An actor produces a trajectory, an evaluator scores or
critiques it, and a self-reflection model writes a compact verbal lesson for a
memory buffer.

The artifact is retrospective and episode-oriented. It records what should be
done differently, but does not require explicit applicability triggers,
ordered procedures, or stopping/failure conditions.

## Evaluation

The official record reports sequential decision-making, reasoning, and coding
experiments, including HumanEval. The central outcome is improved task
performance over repeated attempts.

## Strengths

- Establishes verbal reflection as a practical non-parametric learning signal.
- Uses inspectable natural-language memory.
- Provides the most direct baseline family for this paper.

## Limitations Relative To This Paper

- Primarily evaluates repeated attempts rather than fixed few-trajectory
  induction followed by held-out within-family debugging transfer.
- Does not operationalize per-task negative transfer.
- Does not control for length or procedural organization.

## Role In Related Work

Use Reflexion to define reflection-style memory, then distinguish `SKILL.md` as
a scoped procedure with triggers and failure modes rather than a retrospective
lesson alone.
