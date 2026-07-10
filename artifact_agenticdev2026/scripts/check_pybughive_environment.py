from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASK_SCHEMA = ROOT / "schemas" / "task.schema.json"


def common_windows_executables(name: str) -> list[Path]:
    if sys.platform != "win32":
        return []
    program_files = Path("C:/Program Files")
    candidates: dict[str, list[Path]] = {
        "docker": [
            program_files / "Docker" / "Docker" / "resources" / "bin" / "docker.exe",
        ],
        "pipenv": [],
        "git": [
            program_files / "Git" / "cmd" / "git.exe",
        ],
    }
    return candidates.get(name, [])


def resolve_executable(name: str) -> str:
    resolved = shutil.which(name)
    if resolved:
        return resolved
    for candidate in common_windows_executables(name):
        if candidate.is_file():
            return str(candidate)
    return name


def iter_json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(item for item in path.rglob("*.json") if item.is_file())
    raise FileNotFoundError(path)


def load_tasks(paths: list[Path], schema_path: Path) -> list[dict[str, Any]]:
    schema = load_json(schema_path)
    tasks: list[dict[str, Any]] = []
    for path in paths:
        for file_path in iter_json_files(path):
            data = load_json(file_path)
            validate_instance(data, schema)
            if data["repo"]["source"] == "pybughive":
                tasks.append(data)
    return tasks


def run_text(command: list[str], timeout: int = 20) -> tuple[int, str]:
    try:
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, f"{command[0]} not found"
    except subprocess.TimeoutExpired:
        return 124, "command timed out"
    return process.returncode, process.stdout.strip()


def py_launcher_versions() -> dict[str, str]:
    code, output = run_text(["py", "-0p"])
    if code != 0:
        return {}
    versions: dict[str, str] = {}
    for line in output.splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        version = parts[0].removeprefix("-V:")
        path = parts[-1]
        versions[version] = path
    return versions


def direct_python_versions(required_versions: list[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for version in required_versions:
        executable = f"python{version}"
        code, output = run_text([executable, "--version"])
        if code == 0:
            versions[version] = f"{executable}: {output}"
    return versions


def required_python_versions(tasks: list[dict[str, Any]]) -> list[str]:
    versions = {
        str(task["environment"].get("python_version"))
        for task in tasks
        if task["environment"].get("python_version")
    }
    return sorted(versions)


def summarize(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    git_command = resolve_executable("git")
    docker_command = resolve_executable("docker")
    pipenv_command = resolve_executable("pipenv")
    git_code, git_output = run_text([git_command, "--version"])
    docker_code, docker_output = run_text([docker_command, "--version"])
    docker_engine_code, docker_engine_output = run_text(
        [docker_command, "info", "--format", "{{.ServerVersion}}"],
        timeout=30,
    )
    pipenv_code, pipenv_output = run_text([pipenv_command, "--version"])
    required_versions = required_python_versions(tasks)
    py_launcher = py_launcher_versions()
    direct_versions = direct_python_versions(required_versions)
    py_versions = {**py_launcher, **direct_versions}
    missing_versions = [
        version
        for version in required_versions
        if version not in py_versions and f"{version}.0" not in py_versions
    ]
    can_run_native = git_code == 0 and pipenv_code == 0 and not missing_versions
    can_run_docker = docker_code == 0 and docker_engine_code == 0

    return {
        "n_pybughive_tasks": len(tasks),
        "required_python_versions": required_versions,
        "tools": {
            "git": {
                "available": git_code == 0,
                "command": git_command,
                "output": git_output,
            },
            "docker": {
                "available": docker_code == 0,
                "engine_available": docker_engine_code == 0,
                "command": docker_command,
                "output": docker_output,
                "engine_output": docker_engine_output,
            },
            "pipenv": {
                "available": pipenv_code == 0,
                "command": pipenv_command,
                "output": pipenv_output,
            },
            "py_launcher": {
                "available": bool(py_launcher),
                "versions": py_launcher,
            },
            "direct_python": {
                "available": bool(direct_versions),
                "versions": direct_versions,
            },
        },
        "missing_python_versions": missing_versions,
        "can_run_native_windows_probe": can_run_native,
        "can_run_docker_probe": can_run_docker,
        "ready": can_run_native or can_run_docker,
        "recommended_path": "native" if can_run_native else "docker" if can_run_docker else "setup_required",
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    tools = report["tools"]
    lines = [
        "# PyBugHive Environment Check",
        "",
        f"- PyBugHive tasks: {report['n_pybughive_tasks']}",
        f"- Required Python versions: {', '.join(report['required_python_versions']) or 'none'}",
        f"- Ready: `{str(report['ready']).lower()}`",
        f"- Recommended path: `{report['recommended_path']}`",
        "",
        "## Tools",
        "",
        "| Tool | Available | Detail |",
        "| --- | ---: | --- |",
        f"| git | {tools['git']['available']} | `{tools['git']['command']}`: `{tools['git']['output']}` |",
        f"| docker CLI | {tools['docker']['available']} | `{tools['docker']['command']}`: `{tools['docker']['output']}` |",
        f"| docker engine | {tools['docker']['engine_available']} | `{tools['docker']['engine_output']}` |",
        f"| pipenv | {tools['pipenv']['available']} | `{tools['pipenv']['command']}`: `{tools['pipenv']['output']}` |",
        f"| py launcher | {tools['py_launcher']['available']} | `{tools['py_launcher']['versions']}` |",
        f"| direct python | {tools['direct_python']['available']} | `{tools['direct_python']['versions']}` |",
        "",
        "## Missing",
        "",
        f"- Python versions: {', '.join(report['missing_python_versions']) or 'none'}",
        "",
        "## Next Action",
        "",
    ]
    if report["ready"]:
        lines.append("Run `scripts/verify_pybughive_tasks.py` with execution enabled.")
    else:
        lines.append(
            "Install and start Docker Desktop, or provide `pipenv` plus the required Python versions before full reproducibility verification."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether this machine can execute PyBugHive tasks.")
    parser.add_argument("tasks", nargs="*", type=Path, default=[ROOT / "tasks" / "pybughive"])
    parser.add_argument("--schema", type=Path, default=DEFAULT_TASK_SCHEMA)
    parser.add_argument("--output-json", type=Path, default=ROOT / "results" / "pybughive_environment_check.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "results" / "pybughive_environment_check.md")
    args = parser.parse_args()

    tasks = load_tasks(args.tasks, args.schema)
    report = summarize(tasks)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ready"] else 2


if __name__ == "__main__":
    sys.exit(main())
