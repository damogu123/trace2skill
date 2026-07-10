# PyBugHive Environment

The imported PyBugHive tasks need an environment with `pipenv` and historical Python versions such as 3.7 and 3.8. The current Windows host only has Python 3.13/3.14 and no Docker or `pipenv`, so full reproducibility verification is blocked on environment setup.

## Recommended Path: Docker

Install Docker Desktop. On Windows Home, Docker Desktop uses the WSL2 backend, so ensure that Windows Subsystem for Linux and Virtual Machine Platform are enabled. If Docker reports `HCS_E_HYPERV_NOT_INSTALLED` or the `dockerDesktopLinuxEngine` pipe returns HTTP 500, reboot Windows after enabling those features, then start Docker Desktop again.

After Docker Desktop reports that the engine is running, run from the project root:

```powershell
docker compose -f docker\pybughive\docker-compose.yaml up --build -d
```

The compose file uses build args for base images. By default it pulls `ubuntu:22.04` and `mongo:6.0` through `dockerproxy.net` because direct Docker Hub authentication can time out on this machine. To force official Docker Hub images, set these variables before building:

```powershell
$env:PYBUGHIVE_UBUNTU_IMAGE = "ubuntu:22.04"
$env:PYBUGHIVE_MONGO_IMAGE = "mongo:6.0"
```

Run the environment check inside the container:

```powershell
docker compose -f docker\pybughive\docker-compose.yaml exec pybughive-env bash -lc "cd /project && python3.11 scripts/check_pybughive_environment.py"
```

Run first-batch reproducibility verification:

```powershell
docker compose -f docker\pybughive\docker-compose.yaml exec pybughive-env bash -lc "cd /project && python3.11 scripts/verify_pybughive_tasks.py --force --execute-when-env-blocked"
```

Expected output files:

- `results/pybughive_environment_check.json`
- `results/pybughive_environment_check.md`
- `results/pybughive_reproducibility_status.json`
- `results/pybughive_reproducibility_status.csv`
- `results/pybughive_reproducibility_status.md`

## Native Path

Native setup is possible but more brittle on Windows. It requires:

- `pipenv`
- Python 3.7
- Python 3.8
- build tooling compatible with older Python packages

The current working fallback is WSL Ubuntu with user-local Python runtimes:

- Python 3.8.20 installed by `uv`
- Python 3.7.12 installed by `micromamba`
- `pipenv` installed by `uv tool install pipenv`
- PyPI access configured at runtime with `PIP_INDEX_URL`, `PIP_TRUSTED_HOST`, `PIP_DEFAULT_TIMEOUT`, `PIPENV_PYPI_MIRROR`, and `PIPENV_TIMEOUT`

Run the verified WSL route from PowerShell:

```powershell
wsl.exe -d Ubuntu-24.04 --exec /bin/bash -lc 'export PATH=$HOME/.local/bin:$PATH; export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple; export PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn; export PIP_DEFAULT_TIMEOUT=120; export PIPENV_PYPI_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple; export PIPENV_TIMEOUT=120; cd <PROJECT_ROOT>; python3 scripts/verify_pybughive_tasks.py tasks/pybughive --workspace workspaces/pybughive_verify_wsl_all --force --execute-when-env-blocked --timeout 2400'
```

Current WSL verification artifacts:

- `results/pybughive_wsl_py38_subset_status.json`
- `results/pybughive_wsl_py37_subset_status.json`
- `results/pybughive_wsl_verified_tasks_summary.json`
- `results/pybughive_wsl_verified_tasks_summary.csv`
- `results/pybughive_wsl_verified_tasks_summary.md`

The harness normalizes legacy PyBugHive install steps by keeping `pipenv --python ...` for environment creation while using `pipenv run python -m pip install ...` for dependency installation. This avoids Pipenv lock/import drift and stale virtualenv reuse. The original install commands remain in each task under `benchmark.original_install_steps`.

After setup:

```powershell
python scripts\check_pybughive_environment.py
python scripts\verify_pybughive_tasks.py --force --execute-when-env-blocked
```

## Status Semantics

- `environment_blocked`: machine lacks Docker or native `pipenv` plus required Python versions.
- `install_failed`: checkout and test patch worked, but dependency installation failed.
- `initial_failure_not_reproduced`: install worked, but the target test did not fail on the buggy version.
- `reference_patch_failed`: source fix patch could not apply.
- `reference_test_failed`: source fix applied, but target test still failed.
- `pilot_ready`: install worked, initial failure reproduced, reference fix applied, and fixed test passed.
