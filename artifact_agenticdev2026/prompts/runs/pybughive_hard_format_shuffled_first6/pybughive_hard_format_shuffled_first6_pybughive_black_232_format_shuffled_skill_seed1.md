# Debugging Agent Run Prompt

## Run Metadata

- run_id: `pybughive_hard_format_shuffled_first6_pybughive_black_232_format_shuffled_skill_seed1`
- experiment_id: `pybughive_hard_format_shuffled_first6`
- method: `format_shuffled_skill`
- seed: `1`
- model: `gpt-5.5`
- temperature: `0.0`
- max_turns: `30`
- max_tokens: `60000`
- max_cycles: `10`

## Setup

If the checkout is absent or stale, prepare a clean run workspace first:

```powershell
python3 scripts/prepare_task.py tasks/pybughive_hard/heldout/pybughive_black_232.json --workspace workspaces/runs/pybughive_hard_format_shuffled_first6 --checkout-id pybughive_hard_format_shuffled_first6_pybughive_black_232_format_shuffled_skill_seed1 --force
```

Work only inside:

```text
workspaces/runs/pybughive_hard_format_shuffled_first6/pybughive_hard_format_shuffled_first6_pybughive_black_232_format_shuffled_skill_seed1/repo
```

Write run artifacts under:

```text
runs/pybughive_hard_format_shuffled_first6/pybughive_hard_format_shuffled_first6_pybughive_black_232_format_shuffled_skill_seed1
```

Do not open or use any ground-truth patch, ground-truth summary, future trajectory, or held-out answer. The run must depend only on the task failure information, repository state, and the method context below.


## PyBugHive WSL Execution

This PyBugHive task is configured for WSL Ubuntu on this machine. Run install and test commands from Windows by wrapping them like:

```powershell
wsl.exe -d Ubuntu-24.04 --exec /bin/bash -lc 'export PATH=$HOME/.local/bin:$PATH; export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple; export PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn; export PIP_DEFAULT_TIMEOUT=120; export PIPENV_PYPI_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple; export PIPENV_TIMEOUT=120; cd <PROJECT_ROOT>/workspaces/runs/pybughive_hard_format_shuffled_first6/pybughive_hard_format_shuffled_first6_pybughive_black_232_format_shuffled_skill_seed1/repo; <command>'
```

Use the task's original command in place of `<command>`. Do not run `pipenv`, `pytest`, or `setup.py test` directly in Windows PowerShell for this task.


## Method Context

Use the following method-specific memory artifact for `format_shuffled_skill`.

# Debugging Notes

The following notes were derived from prior debugging experience.

- Rerun the narrow failing test immediately. If it still fails, classify the failure before editing again: wrong code path, incomplete boundary, over-specific patch, or unexpected side effect.
- Reproduce the exact failing command before editing. If the environment requires a wrapper, use that wrapper consistently for every test rerun.
- Running an invalid or inconsistent test command, then misreading harness failure as code failure.
- Passing the narrow test while breaking broader behavior; always run the full command when available.
- Compare the failing case with neighboring supported cases. Ask which general category is missing or treated as the wrong category.
- Use this skill when a failing test exposes a localized behavioral mismatch rather than an installation, dependency, permissions, or flaky-test problem.
- Repeating the same patch shape after a failed rerun instead of returning to the failure log and inspected invariant.
- Use it when the failure can be restated as a compact expected-vs-actual behavior involving an edge case, normalization rule, boundary condition, recursive structure, formatting rule, or time/date comparison.
- Treating a boundary case as a one-off special case when it belongs to a broader category.
- Compress the failure into one sentence: the input shape, the expected behavior, the observed behavior, and the boundary that makes this case special.
- Make one minimal general patch that changes the invariant, not the single observed example. Avoid unrelated cleanup, broad refactors, and edits outside the direct call path.
- Overfitting to a visible literal, fixture value, or assertion string instead of fixing the underlying rule.
- Editing a distant module before confirming the direct owner of the failed behavior.
- Once the narrow test passes, run the broader available test command to check for negative transfer. Record any repeated mistake or invalid test command in the trajectory.
- Inspect the nearest test, fixture, or traceback frame only to identify the behavioral invariant. Do not copy literals from the test into the patch.
- Do not use it when the task requires broad redesign, missing external services, benchmark setup repair, or changes whose correctness cannot be checked by the available tests.
- Open the smallest implementation path that owns the invariant. Prefer the branch, normalization point, lookup table, comparison, or recursive merge step closest to the failing behavior.
- Use it when the traceback, assertion, or fixture points to a narrow call path that can be inspected before editing.
- Do not use it when the visible failing test is only a symptom of widespread state corruption; first isolate the smaller invariant.

## Task Context

```json
{
  "task_id": "pybughive_black_232",
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
      "tests/cantfit.py"
    ],
    "error_type": "PyBugHiveTestFailure",
    "error_message": "Multiline strings cause unnecessary optional parentheses",
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
python scripts/record_trajectory.py --output trajectories/pybughive_hard_format_shuffled_first6/pybughive_hard_format_shuffled_first6_pybughive_black_232_format_shuffled_skill_seed1.json --run-id pybughive_hard_format_shuffled_first6_pybughive_black_232_format_shuffled_skill_seed1 --task tasks/pybughive_hard/heldout/pybughive_black_232.json --method format_shuffled_skill --model gpt-5.5 --temperature 0.0 --max-turns 30 --max-tokens 60000 --max-cycles 10 [add solved/cycle/token/test fields from the run]
```

The final trajectory must validate with:

```powershell
python scripts/validate_trajectory.py trajectories/pybughive_hard_format_shuffled_first6/pybughive_hard_format_shuffled_first6_pybughive_black_232_format_shuffled_skill_seed1.json
```
