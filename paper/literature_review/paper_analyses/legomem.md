# LEGOMem: Modular Procedural Memory for Multi-Agent LLM Systems

## Basic Information

- Authors: Dongge Han, Camille Couturier, Daniel Madrigal Diaz, Xuchao Zhang,
  Victor Ruhle, and Saravan Rajmohan
- Year: 2026
- Venue: AAMAS 2026
- Access: Full text
- Source: https://arxiv.org/abs/2510.04851

## One-Sentence Summary

LEGOMem decomposes past workflow trajectories into reusable procedural-memory
units and allocates those units across orchestrators and task agents.

## Problem And Method

The paper studies where procedural memory should be placed in a multi-agent
workflow system, how it should be retrieved, and which roles benefit. The
orchestrator uses memory for decomposition and delegation, while task agents
use finer-grained memory for execution.

## Evaluation

The paper evaluates OfficeBench and reports workflow success with ablations
over memory placement and retrieval.

## Strengths

- Treats procedural memory as composable modules.
- Separates orchestrator memory from task-agent memory.
- Evaluates procedural-memory placement in a multi-agent workflow.

## Limitations Relative To This Paper

- The task domain is multi-agent office workflow automation.
- Memory construction depends on successful workflow executions rather than a
  fixed few-trajectory debugging induction set.
- Irrelevant retrieval is discussed, but per-task negative transfer is not an
  explicit outcome.
- The artifact is role-specific workflow memory rather than a natural-language
  debugging guide.

## Role In Related Work

LEGOMem supports the trend toward modular procedural memory and provides an
efficiency comparator outside software debugging.
