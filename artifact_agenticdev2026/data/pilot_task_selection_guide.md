# Pilot Task Selection Guide

## Goal

Select a small, reproducible set of Python test-failure debugging tasks for the first pilot of low-shot procedural skill transfer.

Primary data sources:

- BugsInPy
- PyBugHive

## Inclusion Criteria

A task may be included if all conditions hold:

1. The project is Python-based.
2. The buggy version can be checked out locally.
3. Dependencies can be installed in a clean environment.
4. The initial failing test is reproducible.
5. The test command is explicit and stable.
6. The reference fix makes the failing test pass.
7. The failure log provides enough signal for debugging.
8. The task belongs to `test_failure_triage` or a closely related family.
9. Single test runtime is under 120 seconds.
10. The reference patch modifies no more than 3 files.
11. The reference patch is under 100 changed lines.
12. The task does not require network services, GPUs, databases, or large external data.

## Exclusion Criteria

Exclude tasks when any condition holds:

1. Environment cannot be reproduced.
2. Dependencies are unavailable or conflict irreparably.
3. Tests are flaky.
4. The bug is mainly dependency, configuration, CI, or fixture setup.
5. The fix requires broad refactoring.
6. The task requires deep domain knowledge beyond ordinary code inspection.
7. The failure log is uninformative.
8. The reference patch modifies more than 3 files.
9. The reference patch changes more than 100 lines.
10. The test command relies on external services.

## Adversarial Task Criteria

Adversarial tasks should look superficially similar to test-failure triage tasks but should not be solved by the induced skill.

Examples:

- Dependency version mismatch.
- Missing optional package.
- Test fixture misconfiguration.
- Flaky timing issue.
- Changed external API.
- Environment-only failure.

The purpose is to test whether the skill is misapplied when its trigger conditions do not hold.

## Reproducibility Checklist

Before a task enters the pilot set:

1. Clean checkout.
2. Run install command.
3. Run initial failing test and save log.
4. Apply reference patch.
5. Rerun failing test and save log.
6. Run full test command when available.
7. Record modified files and patch size.
8. Assign bug family and surface/root-cause labels.

Task status progression:

```text
candidate -> reproducible -> labeled -> pilot_ready
```

## First Pilot Size

Recommended first pilot:

```text
training tasks: 3
held-out tasks: 8
adversarial tasks: 4
methods:
  - no_memory
  - reflexion
  - length_matched_reflexion
  - generic_checklist
  - auto_skill
seeds: 1
```

If this run is stable, expand to:

```text
training tasks: 5 and 10
held-out tasks: 20-30
adversarial tasks: 10
additional methods:
  - raw_trajectory_retrieval
  - format_shuffled_skill
  - oracle_skill
seeds: 3
```

## Pilot Success Criteria

Proceed to MVP only if:

- At least 90% of runs have complete trajectory logs.
- All tasks reproduce from clean checkout.
- The induction prompt does not leak task-specific patch details.
- The evaluator can reliably classify solved vs unsolved.
- The repeated mistake taxonomy is usable.
- Adversarial tasks induce plausible misuse risk.
- Token and tool-call accounting is reliable.
