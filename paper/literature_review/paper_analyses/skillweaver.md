# SkillWeaver: Web Agents Can Self-Improve by Discovering and Honing Skills

## Basic Information

- Authors: Boyuan Zheng, Michael Y. Fatemi, Xiaolong Jin, Zora Zhiruo Wang,
  Apurva Gandhi, Yueqi Song, Yu Gu, Jayanth Srinivasa, Gaowen Liu, Graham
  Neubig, and Yu Su
- Year: 2025
- Venue: arXiv preprint
- Access: Full text
- Source: https://arxiv.org/abs/2504.07079

## One-Sentence Summary

SkillWeaver explores websites, proposes executable API skills, tests and
debugs them, and reuses the verified skill library on later web tasks.

## Problem And Method

The paper targets repetitive low-level web interaction. Its explorer proposes
website-specific skills from interaction traces, implements them as APIs,
practices their execution, refines failures, and stores successful APIs for
new tasks.

## Evaluation

The paper evaluates website-specific skill discovery and held-out WebArena
task success, together with exploration and skill-library ablations.

## Strengths

- Makes skill preconditions explicit.
- Verifies skills through execution before reuse.
- Studies autonomous skill discovery, debugging, and library growth.

## Limitations Relative To This Paper

- The skills are executable browser APIs, not natural-language debugging
  procedures.
- Skill discovery uses substantial website exploration rather than a few fixed
  source trajectories.
- The verified record is a preprint.
- Failure analysis does not provide a memory-attributed negative-transfer
  metric.

## Role In Related Work

Use SkillWeaver to cover executable skill discovery and to contrast program
skills with an inspectable natural-language memory artifact.
