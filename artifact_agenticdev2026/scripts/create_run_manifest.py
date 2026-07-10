from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"
DEFAULT_MANIFEST_SCHEMA = ROOT / "schemas" / "run_manifest.schema.json"
METHODS = [
    "no_memory",
    "reflexion",
    "length_matched_reflexion",
    "generic_checklist",
    "raw_trajectory_retrieval",
    "format_shuffled_skill",
    "oracle_skill",
    "auto_skill",
]
METHODS_WITHOUT_MEMORY = {"no_memory", "generic_checklist"}
GENERIC_CHECKLIST = ROOT / "baselines" / "generic_debugging_checklist.md"


def iter_json_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(item for item in path.rglob("*.json") if item.is_file()))
        else:
            raise FileNotFoundError(path)
    return sorted(files)


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_methods(value: str) -> list[str]:
    methods = parse_csv(value)
    unknown = sorted(set(methods) - set(METHODS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown methods: {', '.join(unknown)}")
    return methods


def parse_seeds(value: str) -> list[int]:
    seeds = []
    for item in parse_csv(value):
        try:
            seed = int(item)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"invalid seed: {item}") from exc
        if seed < 1:
            raise argparse.ArgumentTypeError("seeds must be >= 1")
        seeds.append(seed)
    return seeds


def sanitize_id(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    if not sanitized:
        raise ValueError(f"Cannot create run id from {value!r}")
    return sanitized


def relative_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def load_tasks(paths: list[Path], schema_path: Path) -> list[tuple[Path, dict[str, Any]]]:
    schema = load_json(schema_path)
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for file_path in iter_json_files(paths):
        task = load_json(file_path)
        validate_instance(task, schema)
        loaded.append((file_path, task))
    return loaded


def find_memory_path(memory_root: Path, task: dict[str, Any], method: str) -> Path | None:
    bug_family = sanitize_id(task["bug_family"])
    candidates = [
        memory_root / bug_family / f"{method}.md",
        memory_root / method / f"{bug_family}.md",
        memory_root / f"{method}_{bug_family}.md",
        memory_root / f"{method}.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def build_run(
    *,
    experiment_id: str,
    task_path: Path,
    task: dict[str, Any],
    method: str,
    seed: int,
    memory_root: Path,
    prompts_dir: Path,
    runs_dir: Path,
    trajectories_dir: Path,
    workspace_dir: Path,
) -> dict[str, Any]:
    run_id = sanitize_id(f"{experiment_id}_{task['task_id']}_{method}_seed{seed}")
    baseline_context_path: Path | None = None
    memory_path: Path | None = None
    requires_memory = method not in METHODS_WITHOUT_MEMORY

    if method == "generic_checklist":
        baseline_context_path = GENERIC_CHECKLIST
    elif requires_memory:
        memory_path = find_memory_path(memory_root, task, method)

    prompt_status = "ready"
    if requires_memory and memory_path is None:
        prompt_status = "missing_memory"

    workspace_path = workspace_dir / run_id / "repo"
    prepare_python = "python3" if task["repo"].get("source") == "pybughive" else "python"
    prepare_command = (
        f"{prepare_python} scripts/prepare_task.py "
        f"{relative_path(task_path)} "
        f"--workspace {relative_path(workspace_dir)} "
        f"--checkout-id {run_id} "
        "--force"
    )

    return {
        "run_id": run_id,
        "task_id": task["task_id"],
        "task_path": relative_path(task_path),
        "method": method,
        "seed": seed,
        "workspace_path": relative_path(workspace_path),
        "artifacts_dir": relative_path(runs_dir / run_id),
        "prompt_path": relative_path(prompts_dir / f"{run_id}.md"),
        "trajectory_path": relative_path(trajectories_dir / f"{run_id}.json"),
        "prepare_command": prepare_command,
        "baseline_context_path": relative_path(baseline_context_path) if baseline_context_path else None,
        "memory_path": relative_path(memory_path) if memory_path else None,
        "requires_memory_artifact": requires_memory,
        "prompt_status": prompt_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a task x baseline x seed run manifest for debugging-agent evaluation."
    )
    parser.add_argument("tasks", nargs="+", type=Path, help="Task JSON files or directories")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--methods", type=parse_methods, default=parse_methods("no_memory,generic_checklist"))
    parser.add_argument("--seeds", type=parse_seeds, default=parse_seeds("1"))
    parser.add_argument("--model", default="manual-agent")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--max-tokens", type=int, default=60000)
    parser.add_argument("--max-cycles", type=int, default=10)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--memory-root", type=Path, default=ROOT / "memory")
    parser.add_argument("--prompts-dir", type=Path, default=ROOT / "prompts" / "runs")
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "runs")
    parser.add_argument("--trajectories-dir", type=Path, default=ROOT / "trajectories")
    parser.add_argument("--workspace-dir", type=Path, default=ROOT / "workspaces" / "runs")
    parser.add_argument("--task-schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    parser.add_argument("--schema", type=Path, default=DEFAULT_MANIFEST_SCHEMA)
    args = parser.parse_args()

    experiment_id = sanitize_id(args.experiment_id)
    prompts_dir = resolve_project_path(str(args.prompts_dir)) / experiment_id
    runs_dir = resolve_project_path(str(args.runs_dir)) / experiment_id
    trajectories_dir = resolve_project_path(str(args.trajectories_dir)) / experiment_id
    workspace_dir = resolve_project_path(str(args.workspace_dir)) / experiment_id
    memory_root = resolve_project_path(str(args.memory_root))

    loaded_tasks = load_tasks(args.tasks, args.task_schema)
    if not loaded_tasks:
        print("No task JSON files found.", file=sys.stderr)
        return 1

    runs = []
    for task_path, task in loaded_tasks:
        for method in args.methods:
            for seed in args.seeds:
                runs.append(
                    build_run(
                        experiment_id=experiment_id,
                        task_path=task_path,
                        task=task,
                        method=method,
                        seed=seed,
                        memory_root=memory_root,
                        prompts_dir=prompts_dir,
                        runs_dir=runs_dir,
                        trajectories_dir=trajectories_dir,
                        workspace_dir=workspace_dir,
                    )
                )

    manifest = {
        "experiment_id": experiment_id,
        "model": args.model,
        "temperature": args.temperature,
        "notes": args.notes,
        "budget": {
            "max_turns": args.max_turns,
            "max_tokens": args.max_tokens,
            "max_cycles": args.max_cycles,
        },
        "runs": runs,
    }
    validate_instance(manifest, load_json(args.schema))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    missing = sum(1 for run in runs if run["prompt_status"] == "missing_memory")
    print(f"Wrote {args.output}")
    print(f"runs={len(runs)} missing_memory={missing}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
