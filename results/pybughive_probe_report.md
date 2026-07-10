# PyBugHive Probe Report

Date: 2026-05-18

## What Was Implemented

- Imported the official PyBugHive JSON dataset from `data/external/pybughive/dataset/pybughive_current.json`.
- Generated 10 metadata-screened first-batch tasks:
  - 3 train tasks under `tasks/pybughive/train/`
  - 7 held-out tasks under `tasks/pybughive/heldout/`
- Generated source fix patches and test patches under `patches/pybughive/`.
- Generated per-task source metadata under `data/pybughive/<task_id>/metadata.json`.
- Extended `schemas/task.schema.json` with optional benchmark metadata.
- Updated `scripts/prepare_task.py` to apply `benchmark.test_patch_path` before installing and reproducing the initial failure.

## First-Batch Status

The generated tasks are metadata-screened candidates, not fully environment-verified yet. They satisfy the lightweight inclusion criteria:

- single known PyBugHive issue
- available buggy parent commit and fix commit
- explicit test command
- reference source patch under 100 changed lines
- no more than 3 modified source files
- available text test patches
- not selected from the heaviest projects by default

## Probe Run

Probe task:

```text
tasks/pybughive/heldout/pybughive_black_185.json
```

Observed:

- Git clone initially hit a transient GitHub TLS error, then succeeded after retry.
- Checkout to the buggy parent commit succeeded.
- PyBugHive test patch applied successfully.
- Reference fix patch passed `git apply --check`.
- Install failed because `pipenv` is not installed on the current Windows machine.

Prepare summary:

```json
{
  "install_returncode": 1,
  "initial_test_returncode": null,
  "initial_failure_reproduced": false,
  "dataset_test_patch_applied": true
}
```

Install blocker:

```text
'pipenv' is not recognized as an internal or external command
```

## Interpretation

The PyBugHive importer and task conversion path are working. The next blocker is reproducible execution environment setup, preferably through a PyBugHive-compatible Linux/Docker environment rather than ad hoc Windows package installation.

## Recommended Next Step

Add a PyBugHive environment path:

1. Install/use `pipenv` plus the required Python versions, or preferably use the official PyBugHive Docker environment.
2. Run `prepare_task.py --verify-reference` on the 10 generated tasks.
3. Mark tasks as `pilot_ready` only after install succeeds, the initial test fails, the reference fix applies, and the fixed test passes.
