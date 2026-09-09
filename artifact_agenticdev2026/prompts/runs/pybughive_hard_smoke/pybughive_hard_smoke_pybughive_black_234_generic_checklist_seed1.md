# Debugging Agent Run Prompt

## Run Metadata

- run_id: `pybughive_hard_smoke_pybughive_black_234_generic_checklist_seed1`
- experiment_id: `pybughive_hard_smoke`
- method: `generic_checklist`
- seed: `1`
- model: `gpt-5.5`
- temperature: `0.0`
- max_turns: `30`
- max_tokens: `60000`
- max_cycles: `10`

## Setup

If the checkout is absent or stale, prepare a clean run workspace first:

```powershell
python3 scripts/prepare_task.py tasks/pybughive_hard/heldout/pybughive_black_234.json --workspace workspaces/runs/pybughive_hard_smoke --checkout-id pybughive_hard_smoke_pybughive_black_234_generic_checklist_seed1 --force
```

Work only inside:

```text
workspaces/runs/pybughive_hard_smoke/pybughive_hard_smoke_pybughive_black_234_generic_checklist_seed1/repo
```

Write run artifacts under:

```text
runs/pybughive_hard_smoke/pybughive_hard_smoke_pybughive_black_234_generic_checklist_seed1
```

Do not open or use any ground-truth patch, ground-truth summary, future trajectory, or held-out answer. The run must depend only on the task failure information, repository state, and the method context below.


## PyBugHive WSL Execution

This PyBugHive task is configured for WSL Ubuntu on this machine. Run install and test commands from Windows by wrapping them like:

```powershell
wsl.exe -d Ubuntu-24.04 --exec /bin/bash -lc 'export PATH=$HOME/.local/bin:$PATH; export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple; export PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn; export PIP_DEFAULT_TIMEOUT=120; export PIPENV_PYPI_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple; export PIPENV_TIMEOUT=120; cd <PROJECT_ROOT>/workspaces/runs/pybughive_hard_smoke/pybughive_hard_smoke_pybughive_black_234_generic_checklist_seed1/repo; <command>'
```

Use the task's original command in place of `<command>`. Do not run `pipenv`, `pytest`, or `setup.py test` directly in Windows PowerShell for this task.


## Method Context

Use the following fixed generic checklist. It is not induced from prior trajectories.

# Generic Debugging Checklist Baseline

## Purpose

This checklist is a non-induced human-written debugging aid. It controls for the possibility that any structured checklist improves agent debugging, regardless of whether the content was induced from prior trajectories.

Use this baseline exactly as written across all tasks in the MVP unless the experimental protocol explicitly defines a versioned update.

## Checklist

1. Read the failing test name, assertion, and traceback before inspecting implementation code.
2. Identify the smallest behavior implied by the failing test.
3. Locate the implementation path most directly connected to that behavior.
4. Inspect existing nearby tests to infer expected behavior and edge cases.
5. Make the smallest code change that addresses the observed failure.
6. Rerun the narrow failing test after each patch.
7. If the narrow test passes, run the relevant broader test file or full test command when available.
8. Avoid hard-coding values that only satisfy the visible assertion.
9. Avoid modifying unrelated modules unless the traceback or call path justifies it.
10. If repeated patches fail, revisit the original failure log instead of continuing the same fix pattern.

## Out-of-Scope Signals

This checklist is not specialized for:

- Dependency installation failures.
- Missing optional packages.
- CI-only configuration failures.
- Flaky timing or ordering failures.
- External API or network failures.
- Large architectural refactors.

## Reporting

When this baseline is used, record:

```json
{
  "baseline": "generic_debugging_checklist",
  "version": "v1",
  "word_count": 165
}
```

## Task Context

```json
{
  "task_id": "pybughive_black_234",
  "repo": {
    "name": "black",
    "source": "pybughive",
    "language": "python"
  },
  "environment": {
    "python_version": "3.7",
    "install_command": "pipenv --python 3.7\npipenv run python -m pip install setuptools==68.0.0\npipenv install\npipenv run python -m pip install click==8.0.2\npipenv run python -m pip install pytest==6.2.5",
    "test_command": "pipenv run python setup.py test",
    "full_test_command": "pipenv run python setup.py test",
    "timeout_seconds": 300
  },
  "failure": {
    "failing_tests": [
      "tests/fmtonoff.py",
      "tests/import_spacing.py"
    ],
    "error_type": "PyBugHiveTestFailure",
    "error_message": "Star import after a long path produces invalid code",
    "failure_log_path": "logs/initial_failure.txt"
  }
}
```

## Debugging Protocol

1. Reproduce the failing test using the task command before editing.
2. Treat each diagnose-edit-test loop as one cycle.
3. For each cycle, record the diagnosis, inspected files and reasons, modified files, patch summary, test command, test result, and any repeated or avoidable mistakes.
4. Make the smallest patch that addresses the behavioral failure.
5. Rerun the narrow failing test after each patch.
6. When the narrow test passes, run the broader command if `full_test_command` is available.
7. Stop when the task is solved or the run budget is exhausted.

## Required Output

After the run, create the trajectory JSON with:

```powershell
python scripts/record_trajectory.py --output trajectories/pybughive_hard_smoke/pybughive_hard_smoke_pybughive_black_234_generic_checklist_seed1.json --run-id pybughive_hard_smoke_pybughive_black_234_generic_checklist_seed1 --task tasks/pybughive_hard/heldout/pybughive_black_234.json --method generic_checklist --model gpt-5.5 --temperature 0.0 --max-turns 30 --max-tokens 60000 --max-cycles 10 [add solved/cycle/token/test fields from the run]
```

The final trajectory must validate with:

```powershell
python scripts/validate_trajectory.py trajectories/pybughive_hard_smoke/pybughive_hard_smoke_pybughive_black_234_generic_checklist_seed1.json
```


