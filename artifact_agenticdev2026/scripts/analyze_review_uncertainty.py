#!/usr/bin/env python3
"""Compute small-sample uncertainty and sensitivity summaries for the paper.

The analysis is intentionally task-level. It does not estimate run-to-run
variation because each task/method configuration has only one execution.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PRIMARY_PATH = RESULTS / "pybughive_hard_first6_by_task_metrics.csv"
AUTO_GPT55_PATH = RESULTS / "pybughive_hard_auto_skill_first6_gpt55_by_task_metrics.csv"
SHUFFLED_GPT55_PATH = RESULTS / "pybughive_hard_format_shuffled_first6_gpt55_by_task_metrics.csv"
OUTPUT_JSON = RESULTS / "reviewer_uncertainty_analysis.json"
OUTPUT_MD = ROOT / "paper" / "tables" / "reviewer_uncertainty_analysis.md"


METHOD_LABELS = {
    "auto_skill": "Auto SKILL.md",
    "generic_checklist": "Generic checklist",
    "reflexion": "Reflexion memory",
    "length_matched_reflexion": "Length-matched Reflexion",
    "no_memory": "No memory",
    "format_shuffled_skill": "Format-shuffled SKILL.md",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "")
    return float(value) if value not in {None, ""} else None


def wilson_interval(successes: int, total: int, confidence: float = 0.95) -> tuple[float, float]:
    if total == 0:
        raise ValueError("Wilson interval requires at least one observation")
    z = NormalDist().inv_cdf(0.5 + confidence / 2)
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total))
        / denominator
    )
    return center - margin, center + margin


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def exact_bootstrap_mean_interval(values: list[float]) -> tuple[float, float]:
    """Enumerate all n**n task-resampling bootstrap means for small n."""
    if not values:
        raise ValueError("Bootstrap interval requires observations")
    n = len(values)
    means = [
        statistics.fmean(values[index] for index in sample)
        for sample in itertools.product(range(n), repeat=n)
    ]
    return percentile(means, 0.025), percentile(means, 0.975)


def leave_one_out_mean_range(values: list[float]) -> tuple[float, float]:
    if len(values) < 2:
        raise ValueError("Leave-one-out analysis requires at least two observations")
    means = [statistics.fmean(values[:index] + values[index + 1 :]) for index in range(len(values))]
    return min(means), max(means)


def primary_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    by_method: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_method[row["method"]].append(row)

    solve_intervals: dict[str, object] = {}
    token_sensitivity: dict[str, object] = {}
    for method, method_rows in sorted(by_method.items()):
        successes = sum(int(float(row["solved"])) for row in method_rows)
        low, high = wilson_interval(successes, len(method_rows))
        solved_tokens = [
            value
            for row in method_rows
            if int(float(row["solved"]))
            for value in [number(row, "tokens_per_solved_task")]
            if value is not None
        ]
        solve_intervals[method] = {
            "solved": successes,
            "tasks": len(method_rows),
            "rate": successes / len(method_rows),
            "wilson_95": [low, high],
        }
        token_sensitivity[method] = {
            "mean": statistics.fmean(solved_tokens),
            "median": statistics.median(solved_tokens),
            "leave_one_out_mean_range": list(leave_one_out_mean_range(solved_tokens)),
        }

    by_key = {(row["method"], row["task_id"]): row for row in rows}
    auto_tasks = {row["task_id"] for row in by_method["auto_skill"] if int(float(row["solved"]))}
    paired: dict[str, object] = {}
    for baseline in [
        "generic_checklist",
        "reflexion",
        "length_matched_reflexion",
        "no_memory",
    ]:
        baseline_tasks = {
            row["task_id"] for row in by_method[baseline] if int(float(row["solved"]))
        }
        common = sorted(auto_tasks & baseline_tasks)
        cycle_deltas = [
            number(by_key[("auto_skill", task)], "cycles_per_solved_task")
            - number(by_key[(baseline, task)], "cycles_per_solved_task")
            for task in common
        ]
        token_deltas = [
            number(by_key[("auto_skill", task)], "tokens_per_solved_task")
            - number(by_key[(baseline, task)], "tokens_per_solved_task")
            for task in common
        ]
        paired[baseline] = {
            "tasks": common,
            "n": len(common),
            "auto_minus_baseline_cycles_mean": statistics.fmean(cycle_deltas),
            "cycles_bootstrap_95": list(exact_bootstrap_mean_interval(cycle_deltas)),
            "cycles_leave_one_out_mean_range": list(leave_one_out_mean_range(cycle_deltas)),
            "auto_minus_baseline_tokens_mean": statistics.fmean(token_deltas),
            "tokens_bootstrap_95": list(exact_bootstrap_mean_interval(token_deltas)),
            "tokens_leave_one_out_mean_range": list(leave_one_out_mean_range(token_deltas)),
        }

    return {
        "solve_rate_wilson_intervals": solve_intervals,
        "solve_conditional_token_sensitivity": token_sensitivity,
        "paired_common_solved": paired,
    }


def structural_summary(auto_rows: list[dict[str, str]], shuffled_rows: list[dict[str, str]]) -> dict[str, object]:
    by_method = {
        "auto_skill": auto_rows,
        "format_shuffled_skill": shuffled_rows,
    }
    output: dict[str, object] = {}
    for method, rows in by_method.items():
        tokens = [number(row, "tokens_per_solved_task") for row in rows]
        cycles = [number(row, "cycles_per_solved_task") for row in rows]
        output[method] = {
            "tokens_mean": statistics.fmean(tokens),
            "tokens_median": statistics.median(tokens),
            "tokens_leave_one_out_mean_range": list(leave_one_out_mean_range(tokens)),
            "cycles_mean": statistics.fmean(cycles),
            "cycles_median": statistics.median(cycles),
        }

    without_black_193: dict[str, float] = {}
    for method, rows in by_method.items():
        tokens = [
            number(row, "tokens_per_solved_task")
            for row in rows
            if row["task_id"] != "pybughive_black_193"
        ]
        without_black_193[method] = statistics.fmean(tokens)
    output["without_black_193_tokens_mean"] = without_black_193
    return output


def format_interval(interval: list[float], digits: int = 2) -> str:
    return f"[{interval[0]:.{digits}f}, {interval[1]:.{digits}f}]"


def render_markdown(analysis: dict[str, object]) -> str:
    primary = analysis["primary"]
    structural = analysis["structural_control_gpt55"]
    lines = [
        "# Reviewer-requested uncertainty and sensitivity analysis",
        "",
        "These are task-level descriptive analyses. They do not estimate run-to-run",
        "variation because each task/method configuration has one execution.",
        "",
        "## Solve-rate uncertainty",
        "",
        "| Method | Solved | Rate | Wilson 95% interval |",
        "|---|---:|---:|---:|",
    ]
    for method in [
        "auto_skill",
        "generic_checklist",
        "reflexion",
        "length_matched_reflexion",
        "no_memory",
    ]:
        row = primary["solve_rate_wilson_intervals"][method]
        lines.append(
            f"| {METHOD_LABELS[method]} | {row['solved']}/{row['tasks']} | "
            f"{row['rate']:.3f} | {format_interval(row['wilson_95'], 3)} |"
        )

    lines.extend(
        [
            "",
            "## Paired common-solved uncertainty",
            "",
            "Negative deltas favor Auto SKILL.md. Intervals are exact-enumeration",
            "task-resampling bootstrap percentile intervals over the common-solved tasks.",
            "",
            "| Baseline | n | Cycle delta (95% interval) | Token delta (95% interval) |",
            "|---|---:|---:|---:|",
        ]
    )
    for method in [
        "generic_checklist",
        "reflexion",
        "length_matched_reflexion",
        "no_memory",
    ]:
        row = primary["paired_common_solved"][method]
        lines.append(
            f"| {METHOD_LABELS[method]} | {row['n']} | "
            f"{row['auto_minus_baseline_cycles_mean']:.2f} "
            f"{format_interval(row['cycles_bootstrap_95'], 2)} | "
            f"{row['auto_minus_baseline_tokens_mean']:,.0f} "
            f"{format_interval(row['tokens_bootstrap_95'], 0)} |"
        )

    lines.extend(
        [
            "",
            "## Token sensitivity",
            "",
            "| Method | Mean | Median | Leave-one-task-out mean range |",
            "|---|---:|---:|---:|",
        ]
    )
    for method in [
        "auto_skill",
        "generic_checklist",
        "reflexion",
        "length_matched_reflexion",
        "no_memory",
    ]:
        row = primary["solve_conditional_token_sensitivity"][method]
        lines.append(
            f"| {METHOD_LABELS[method]} | {row['mean']:,.0f} | {row['median']:,.0f} | "
            f"{format_interval(row['leave_one_out_mean_range'], 0)} |"
        )

    lines.extend(
        [
            "",
            "## Structural-control outlier check",
            "",
            f"Auto SKILL.md mean/median tokens: {structural['auto_skill']['tokens_mean']:,.0f} / "
            f"{structural['auto_skill']['tokens_median']:,.0f}.",
            f"Format-shuffled mean/median tokens: "
            f"{structural['format_shuffled_skill']['tokens_mean']:,.0f} / "
            f"{structural['format_shuffled_skill']['tokens_median']:,.0f}.",
            f"After excluding black_193, means are "
            f"{structural['without_black_193_tokens_mean']['auto_skill']:,.0f} and "
            f"{structural['without_black_193_tokens_mean']['format_shuffled_skill']:,.0f}, "
            "respectively. This confirms that the aggregate token ranking is outlier-sensitive.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    analysis = {
        "scope_note": (
            "Task-level descriptive uncertainty only; one execution per task/method means "
            "run-to-run variance is not estimable."
        ),
        "primary": primary_summary(read_rows(PRIMARY_PATH)),
        "structural_control_gpt55": structural_summary(
            read_rows(AUTO_GPT55_PATH), read_rows(SHUFFLED_GPT55_PATH)
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(analysis), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
