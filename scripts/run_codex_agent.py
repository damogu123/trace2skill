from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


TRACE_INSTRUCTIONS = """\

---

# Experiment Harness Override

Ignore any earlier instruction that asks you to create the final trajectory JSON with `record_trajectory.py`.

The run workspace may already contain benchmark-introduced changes, such as failing
tests or task fixtures. Treat that prepared checkout as the starting state for this
run. Do not stop to ask the user about a dirty git worktree inside the run
workspace; avoid reverting existing benchmark files, and make only the minimal
debugging patch needed to satisfy the task tests.

Do not recreate, reset, reclone, or repopulate the run checkout. In particular,
do not run `scripts/prepare_task.py`, `git reset`, `git checkout --`, `git clean`,
`robocopy`, `xcopy`, `Copy-Item`, or copy files from another checkout/workspace to
repair a perceived dirty worktree. Tracked test/docs changes in the prepared
checkout are benchmark fixtures, not user changes and not contamination.

Do not use web search, browser tools, online documentation, GitHub pages, or any
external network source during this benchmark run. The run must depend only on
the prompt, the prepared checkout, and local test output.

The external harness, not the agent, will:

- collect the final patch diff;
- rerun the narrow and full tests;
- create the final `trajectory.schema.json` record.

Your only required experiment artifact is the trace JSON below.

# Required Experiment Trace

Before finishing, write a JSON file at this exact absolute path:

```text
{trace_path}
```

Do not write this trace under the repository-relative `runs/` directory. Use the exact absolute path above.

The JSON must follow this shape:

```json
{{
  "llm_turns": 0,
  "tool_calls": 0,
  "input_tokens": 0,
  "output_tokens": 0,
  "cycles": [
    {{
      "cycle_id": 1,
      "diagnosis": "short diagnosis of the failure",
      "file_inspections": [
        {{
          "path": "relative/path.py",
          "reason": "why this file was inspected"
        }}
      ],
      "modified_files": ["relative/path.py"],
      "patch_summary": "what changed",
      "test_command": null,
      "test_passed": null,
      "test_log_path": null,
      "mistakes": []
    }}
  ],
  "negative_transfer": {{
    "detected": false,
    "category": null,
    "reason": null
  }}
}}
```

Use best-effort counts for `llm_turns`, `tool_calls`, `input_tokens`, and `output_tokens` if exact usage is unavailable. Do not read ground-truth patches or files outside the run prompt and checkout.
"""


def parse_total_tokens(output: str) -> int | None:
    tokens: list[int] = []
    lines = output.splitlines()
    for index, line in enumerate(lines):
        if "tokens used" not in line.lower():
            continue
        same_line = re.search(r"([0-9][0-9,]*)", line)
        if same_line:
            tokens.append(int(same_line.group(1).replace(",", "")))
            continue
        for followup in lines[index + 1 : index + 4]:
            match = re.search(r"^\s*([0-9][0-9,]*)\s*$", followup)
            if match:
                tokens.append(int(match.group(1).replace(",", "")))
                break
    return tokens[-1] if tokens else None


def update_trace_total_tokens(trace_path: Path, total_tokens: int) -> None:
    data = json.loads(trace_path.read_text(encoding="utf-8-sig"))
    data["input_tokens"] = total_tokens
    data["output_tokens"] = 0
    trace_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_augmented_prompt(prompt_path: Path, trace_path: Path) -> str:
    prompt = prompt_path.read_text(encoding="utf-8")
    return prompt.rstrip() + "\n" + TRACE_INSTRUCTIONS.format(trace_path=trace_path)


def recover_repo_local_trace(repo_dir: Path, trace_path: Path) -> bool:
    try:
        relative_trace = trace_path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    candidate = repo_dir / relative_trace
    if not candidate.exists():
        return False
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate, trace_path)
    return True


def copy_trace_to_artifacts(source_trace: Path, target_trace: Path) -> bool:
    if not source_trace.exists():
        return False
    target_trace.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_trace, target_trace)
    try:
        source_trace.unlink()
    except OSError:
        pass
    return True


def terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def run_codex_command(
    command: list[str],
    prompt: str,
    repo_dir: Path,
    output_path: Path,
    last_message_path: Path,
    codex_trace_path: Path,
    finish_grace_seconds: int,
) -> tuple[int, str, bool]:
    forced_completion = False
    trace_ready_since: float | None = None
    with output_path.open("w", encoding="utf-8", errors="replace", newline="\n") as output_stream:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=output_stream,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=repo_dir,
        )
        if process.stdin is not None:
            try:
                process.stdin.write(prompt)
                process.stdin.close()
            except BrokenPipeError:
                pass

        while True:
            code = process.poll()
            if code is not None:
                break

            if finish_grace_seconds > 0 and last_message_path.exists() and codex_trace_path.exists():
                if trace_ready_since is None:
                    trace_ready_since = time.monotonic()
                elif time.monotonic() - trace_ready_since >= finish_grace_seconds:
                    terminate_process_tree(process)
                    forced_completion = True
                    code = 0
                    break
            else:
                trace_ready_since = None

            time.sleep(2)

    codex_output = output_path.read_text(encoding="utf-8", errors="replace") if output_path.exists() else ""
    return int(code or 0), codex_output, forced_completion


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(
        description="Codex CLI adapter for scripts/run_external_agent.py."
    )
    parser.add_argument("--prompt-path", type=Path, required=True)
    parser.add_argument("--repo-dir", type=Path, required=True)
    parser.add_argument("--artifacts-dir", type=Path, required=True)
    parser.add_argument("--trace-path", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--approval-policy", default="never")
    parser.add_argument("--sandbox", default="workspace-write")
    parser.add_argument("--extra-arg", action="append", default=[])
    parser.add_argument(
        "--finish-grace-seconds",
        type=int,
        default=30,
        help=(
            "If Codex writes both codex_last_message.md and repo-local agent_trace.json "
            "but the CLI process remains alive, terminate it after this grace period "
            "and continue as a completed run. Use 0 to disable."
        ),
    )
    args = parser.parse_args()

    args.artifacts_dir.mkdir(parents=True, exist_ok=True)
    codex_trace_path = args.repo_dir / "agent_trace.json"
    augmented_prompt = build_augmented_prompt(args.prompt_path, codex_trace_path)
    augmented_prompt_path = args.artifacts_dir / "codex_prompt.md"
    last_message_path = args.artifacts_dir / "codex_last_message.md"
    command_record_path = args.artifacts_dir / "codex_command.json"
    codex_stdout_path = args.artifacts_dir / "codex_stdout.log"

    augmented_prompt_path.write_text(augmented_prompt, encoding="utf-8", newline="\n")
    command = [
        "codex",
        "--ask-for-approval",
        args.approval_policy,
        "exec",
        "--skip-git-repo-check",
        "--cd",
        str(args.repo_dir),
        "--add-dir",
        str(args.artifacts_dir),
        "--model",
        args.model,
        "--sandbox",
        args.sandbox,
        "--output-last-message",
        str(last_message_path),
    ]
    command.extend(args.extra_arg)
    command.append("-")
    command_record_path.write_text(
        json.dumps(
            {
                "command": command,
                "prompt_path": str(args.prompt_path),
                "repo_dir": str(args.repo_dir),
                "artifacts_dir": str(args.artifacts_dir),
                "trace_path": str(args.trace_path),
                "codex_trace_path": str(codex_trace_path),
                "model": args.model,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    returncode, codex_output, forced_completion = run_codex_command(
        command,
        augmented_prompt,
        args.repo_dir,
        codex_stdout_path,
        last_message_path,
        codex_trace_path,
        args.finish_grace_seconds,
    )
    if codex_output:
        print(codex_output, end="" if codex_output.endswith("\n") else "\n")
    if forced_completion:
        print(
            "NOTE: Codex wrote the final message and trace but did not exit; "
            "terminated the lingering CLI process and continued."
        )
    if returncode != 0:
        return returncode
    if not args.trace_path.exists():
        recovered = copy_trace_to_artifacts(codex_trace_path, args.trace_path)
        if not recovered:
            recovered = recover_repo_local_trace(args.repo_dir, args.trace_path)
        if not recovered:
            print(f"ERROR: Codex completed but did not write trace: {args.trace_path}", file=sys.stderr)
            return 2
        print(f"Recovered repo-local trace to {args.trace_path}")
    total_tokens = parse_total_tokens(codex_output)
    if total_tokens is not None:
        update_trace_total_tokens(args.trace_path, total_tokens)
    return 0


if __name__ == "__main__":
    sys.exit(main())
