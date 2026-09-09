# Debugging Agent Run Prompt

## Run Metadata

- run_id: `pybughive_train_trajectories_pybughive_cookiecutter_1513_no_memory_seed1`
- experiment_id: `pybughive_train_trajectories`
- method: `no_memory`
- seed: `1`
- model: `gpt-5.3-codex`
- temperature: `0.0`
- max_turns: `30`
- max_tokens: `60000`
- max_cycles: `10`

## Setup

If the checkout is absent or stale, prepare a clean run workspace first:

```powershell
python3 scripts/prepare_task.py tasks/pybughive/train/pybughive_cookiecutter_1513.json --workspace workspaces/runs/pybughive_train_trajectories --checkout-id pybughive_train_trajectories_pybughive_cookiecutter_1513_no_memory_seed1 --force
```

Work only inside:

```text
workspaces/runs/pybughive_train_trajectories/pybughive_train_trajectories_pybughive_cookiecutter_1513_no_memory_seed1/repo
```

Write run artifacts under:

```text
runs/pybughive_train_trajectories/pybughive_train_trajectories_pybughive_cookiecutter_1513_no_memory_seed1
```

Do not open or use any ground-truth patch, ground-truth summary, future trajectory, or held-out answer. The run must depend only on the task failure information, repository state, and the method context below.


## PyBugHive WSL Execution

This PyBugHive task is configured for WSL Ubuntu on this machine. Run install and test commands from Windows by wrapping them like:

```powershell
wsl.exe -d Ubuntu-24.04 --exec /bin/bash -lc 'export PATH=$HOME/.local/bin:$PATH; export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple; export PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn; export PIP_DEFAULT_TIMEOUT=120; export PIPENV_PYPI_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple; export PIPENV_TIMEOUT=120; cd <PROJECT_ROOT>/workspaces/runs/pybughive_train_trajectories/pybughive_train_trajectories_pybughive_cookiecutter_1513_no_memory_seed1/repo; <command>'
```

Use the task's original command in place of `<command>`. Do not run `pipenv`, `pytest`, or `setup.py test` directly in Windows PowerShell for this task.


## Method Context

No prior trajectories, reflections, checklists, or skill artifacts are available. Solve the task from the failing test, traceback, and repository only.

## Task Context

```json
{
  "task_id": "pybughive_cookiecutter_1513",
  "repo": {
    "name": "cookiecutter",
    "source": "pybughive",
    "language": "python"
  },
  "environment": {
    "python_version": "3.8",
    "install_command": "pipenv --python 3.8\npipenv run python -m pip install -r test_requirements.txt\npipenv run python -m pip install .",
    "test_command": "pipenv run pytest -- tests/test_get_config.py",
    "full_test_command": "pipenv run pytest",
    "timeout_seconds": 300
  },
  "failure": {
    "failing_tests": [
      "tests/test-config/valid-config.yaml",
      "tests/test_get_config.py",
      "tests/test_get_user_config.py"
    ],
    "error_type": "PyBugHiveTestFailure",
    "error_message": "Error reading yaml file using `poyo` - `ValueError: Parent of ChildMixin instance needs to be a Container.`",
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
python scripts/record_trajectory.py --output trajectories/pybughive_train_trajectories/pybughive_train_trajectories_pybughive_cookiecutter_1513_no_memory_seed1.json --run-id pybughive_train_trajectories_pybughive_cookiecutter_1513_no_memory_seed1 --task tasks/pybughive/train/pybughive_cookiecutter_1513.json --method no_memory --model gpt-5.3-codex --temperature 0.0 --max-turns 30 --max-tokens 60000 --max-cycles 10 [add solved/cycle/token/test fields from the run]
```

The final trajectory must validate with:

```powershell
python scripts/validate_trajectory.py trajectories/pybughive_train_trajectories/pybughive_train_trajectories_pybughive_cookiecutter_1513_no_memory_seed1.json
```
