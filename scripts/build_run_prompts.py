from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_SCHEMA = ROOT / "schemas" / "run_manifest.schema.json"
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def to_wsl_path(path: Path) -> str:
    resolved = path.resolve()
    if os.name != "nt":
        return resolved.as_posix()
    drive = resolved.drive.rstrip(":").lower()
    if not drive:
        return resolved.as_posix().replace("\\", "/")
    relative = resolved.relative_to(resolved.anchor)
    return f"/mnt/{drive}/" + relative.as_posix()


def load_manifest(path: Path, schema_path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    validate_instance(manifest, load_json(schema_path))
    return manifest


def load_task(path_text: str, schema_path: Path) -> dict[str, Any]:
    task = load_json(resolve_project_path(path_text))
    validate_instance(task, load_json(schema_path))
    return task


def read_optional_context(path_text: str | None) -> str | None:
    if path_text is None:
        return None
    path = resolve_project_path(path_text)
    return path.read_text(encoding="utf-8")


def method_context(run: dict[str, Any], allow_missing_memory: bool) -> str:
    method = run["method"]
    if method == "no_memory":
        return (
            "No prior trajectories, reflections, checklists, or skill artifacts are available. "
            "Solve the task from the failing test, traceback, and repository only."
        )

    if method == "generic_checklist":
        context = read_optional_context(run.get("baseline_context_path"))
        if context is None:
            raise ValueError(f"{run['run_id']} is missing generic checklist context")
        return (
            "Use the following fixed generic checklist. It is not induced from prior trajectories.\n\n"
            + context.strip()
        )

    context = read_optional_context(run.get("memory_path"))
    if context is None:
        if not allow_missing_memory:
            raise ValueError(
                f"{run['run_id']} requires a memory artifact for {method}, but memory_path is null"
            )
        return (
            f"MEMORY ARTIFACT MISSING for method `{method}`. "
            "This prompt is only a dry-run scaffold and should not be used for final evaluation."
        )
    return f"Use the following method-specific memory artifact for `{method}`.\n\n{context.strip()}"


def task_context(task: dict[str, Any]) -> str:
    public_task = {
        "task_id": task["task_id"],
        "repo": {
            "name": task["repo"]["name"],
            "source": task["repo"]["source"],
            "language": task["repo"]["language"],
        },
        "environment": task["environment"],
        "failure": task["failure"],
    }
    return json.dumps(public_task, indent=2, ensure_ascii=False)


def record_command(run: dict[str, Any], manifest: dict[str, Any]) -> str:
    return (
        "python scripts/record_trajectory.py "
        f"--output {run['trajectory_path']} "
        f"--run-id {run['run_id']} "
        f"--task {run['task_path']} "
        f"--method {run['method']} "
        f"--model {manifest['model']} "
        f"--temperature {manifest['temperature']} "
        f"--max-turns {manifest['budget']['max_turns']} "
        f"--max-tokens {manifest['budget']['max_tokens']} "
        f"--max-cycles {manifest['budget']['max_cycles']} "
        "[add solved/cycle/token/test fields from the run]"
    )


def execution_note(run: dict[str, Any], task: dict[str, Any]) -> str:
    if task["repo"]["source"] != "pybughive":
        return ""
    workspace_path = resolve_project_path(run["workspace_path"])
    wsl_workspace = to_wsl_path(workspace_path)
    return f"""
## PyBugHive WSL Execution

This PyBugHive task is configured for WSL Ubuntu on this machine. Run install and test commands from Windows by wrapping them like:

```powershell
wsl.exe -d Ubuntu-24.04 --exec /bin/bash -lc 'export PATH=$HOME/.local/bin:$PATH; export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple; export PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn; export PIP_DEFAULT_TIMEOUT=120; export PIPENV_PYPI_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple; export PIPENV_TIMEOUT=120; cd {wsl_workspace}; <command>'
```

Use the task's original command in place of `<command>`. Do not run `pipenv`, `pytest`, or `setup.py test` directly in Windows PowerShell for this task.
"""


def render_prompt(run: dict[str, Any], manifest: dict[str, Any], task: dict[str, Any], context: str) -> str:
    return f"""# Debugging Agent Run Prompt

## Run Metadata

- run_id: `{run["run_id"]}`
- experiment_id: `{manifest["experiment_id"]}`
- method: `{run["method"]}`
- seed: `{run["seed"]}`
- model: `{manifest["model"]}`
- temperature: `{manifest["temperature"]}`
- max_turns: `{manifest["budget"]["max_turns"]}`
- max_tokens: `{manifest["budget"]["max_tokens"]}`
- max_cycles: `{manifest["budget"]["max_cycles"]}`

## Setup

If the checkout is absent or stale, prepare a clean run workspace first:

```powershell
{run["prepare_command"]}
```

Work only inside:

```text
{run["workspace_path"]}
```

Write run artifacts under:

```text
{run["artifacts_dir"]}
```

Do not open or use any ground-truth patch, ground-truth summary, future trajectory, or held-out answer. The run must depend only on the task failure information, repository state, and the method context below.

{execution_note(run, task)}

## Method Context

{context}

## Task Context

```json
{task_context(task)}
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
{record_command(run, manifest)}
```

The final trajectory must validate with:

```powershell
python scripts/validate_trajectory.py {run["trajectory_path"]}
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build one debugging-agent prompt pack per run in a run manifest."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--allow-missing-memory",
        action="store_true",
        help="Write dry-run scaffold prompts even when method-specific memory artifacts are missing.",
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_MANIFEST_SCHEMA)
    parser.add_argument("--task-schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest, args.schema)
    written = 0
    for run in manifest["runs"]:
        task = load_task(run["task_path"], args.task_schema)
        context = method_context(run, args.allow_missing_memory)
        prompt = render_prompt(run, manifest, task, context)
        prompt_path = resolve_project_path(run["prompt_path"])
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(prompt, encoding="utf-8", newline="\n")
        written += 1

    print(f"Wrote {written} prompt pack(s)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
