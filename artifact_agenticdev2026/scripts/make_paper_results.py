"""Generate paper-ready result tables, SVG figures, and analysis notes.

This script intentionally uses only the Python standard library so the result
package can be regenerated on machines without pandas/matplotlib.
"""

from __future__ import annotations

import csv
import html
import math
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
PAPER_DIR = ROOT / "paper"
FIGURE_DIR = PAPER_DIR / "figures"
TABLE_DIR = PAPER_DIR / "tables"

METHOD_ORDER = [
    "auto_skill",
    "generic_checklist",
    "reflexion",
    "length_matched_reflexion",
    "no_memory",
]

METHOD_LABELS = {
    "auto_skill": "Auto SKILL.md",
    "generic_checklist": "Generic checklist",
    "reflexion": "Reflexion memory",
    "length_matched_reflexion": "Length-matched Reflexion",
    "no_memory": "No memory",
}

SHORT_LABELS = {
    "auto_skill": ["Auto", "SKILL.md"],
    "generic_checklist": ["Generic", "checklist"],
    "reflexion": ["Reflexion", "memory"],
    "length_matched_reflexion": ["Length", "matched", "Reflexion"],
    "no_memory": ["No", "memory"],
}

COLORS = {
    "auto_skill": "#0072B2",
    "generic_checklist": "#009E73",
    "reflexion": "#D55E00",
    "length_matched_reflexion": "#CC79A7",
    "no_memory": "#6B6B6B",
}


def ensure_dirs() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def f(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "")
    if value == "" or value is None:
        return None
    return float(value)


def i(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    if value == "" or value is None:
        return 0
    return int(float(value))


def method_sort(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    order = {method: idx for idx, method in enumerate(METHOD_ORDER)}
    return sorted(rows, key=lambda row: order.get(row["method"], 999))


def fmt_float(value: float | None, digits: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def fmt_tokens(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:,.0f}"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_text(
    x: float,
    y: float,
    text: str,
    *,
    size: int = 13,
    anchor: str = "middle",
    weight: str = "400",
    fill: str = "#222222",
    rotate: float | None = None,
) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}"{transform}>'
        f"{esc(text)}</text>"
    )


def svg_multiline_text(
    x: float,
    y: float,
    lines: list[str],
    *,
    size: int = 12,
    anchor: str = "middle",
    fill: str = "#222222",
    line_height: int = 14,
) -> str:
    tspans = []
    for idx, line in enumerate(lines):
        dy = 0 if idx == 0 else line_height
        tspans.append(f'<tspan x="{x:.1f}" dy="{dy}">{esc(line)}</tspan>')
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-size="{size}" fill="{fill}">' + "".join(tspans) + "</text>"
    )


def svg_rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    *,
    stroke: str = "none",
    stroke_width: float = 1,
    radius: float = 0,
    opacity: float = 1.0,
) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{radius:.1f}" ry="{radius:.1f}" fill="{fill}" opacity="{opacity:.3f}" '
        f'stroke="{stroke}" stroke-width="{stroke_width:.1f}" />'
    )


def svg_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str = "#333333",
    stroke_width: float = 1,
    dash: str | None = None,
) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{stroke}" stroke-width="{stroke_width:.1f}"{dash_attr} />'
    )


def svg_arrow(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str = "#333333",
    stroke_width: float = 2,
) -> str:
    angle = math.atan2(y2 - y1, x2 - x1)
    head = 10
    spread = 0.45
    p1 = (x2 - head * math.cos(angle - spread), y2 - head * math.sin(angle - spread))
    p2 = (x2 - head * math.cos(angle + spread), y2 - head * math.sin(angle + spread))
    return (
        svg_line(x1, y1, x2, y2, stroke=stroke, stroke_width=stroke_width)
        + f'\n<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{stroke}" />'
    )


def write_svg(path: Path, width: int, height: int, elements: list[str]) -> None:
    body = "\n  ".join(elements)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff" />
  <style>
    text {{ font-family: Arial, Helvetica, sans-serif; }}
  </style>
  {body}
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def draw_bar_panel(
    elements: list[str],
    rows: list[dict[str, str]],
    *,
    x0: float,
    y0: float,
    width: float,
    height: float,
    metric: str,
    title: str,
    y_label: str,
    max_value: float,
    value_formatter,
) -> None:
    elements.append(svg_text(x0 + width / 2, y0 - 22, title, size=20, weight="700"))
    plot_y = y0
    plot_h = height
    axis_x = x0 + 48
    axis_y = plot_y + plot_h
    plot_w = width - 64

    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        value = tick * max_value
        y = axis_y - (value / max_value) * plot_h
        elements.append(svg_line(axis_x, y, axis_x + plot_w, y, stroke="#E0E0E0"))
        elements.append(svg_text(axis_x - 10, y + 5, value_formatter(value), size=15, anchor="end", fill="#555555"))

    elements.append(svg_line(axis_x, plot_y, axis_x, axis_y, stroke="#333333"))
    elements.append(svg_line(axis_x, axis_y, axis_x + plot_w, axis_y, stroke="#333333"))
    elements.append(svg_text(x0 + 8, plot_y + plot_h / 2, y_label, size=17, weight="700", rotate=-90, fill="#333333"))

    n = len(rows)
    gap = 18
    bar_w = (plot_w - gap * (n + 1)) / n
    for idx, row in enumerate(rows):
        method = row["method"]
        value = f(row, metric) or 0.0
        x = axis_x + gap + idx * (bar_w + gap)
        bar_h = (value / max_value) * plot_h if max_value else 0
        y = axis_y - bar_h
        elements.append(svg_rect(x, y, bar_w, bar_h, COLORS[method], radius=3))
        elements.append(svg_text(x + bar_w / 2, y - 9, value_formatter(value), size=16, weight="700", fill="#222222"))
        elements.append(svg_multiline_text(x + bar_w / 2, axis_y + 27, SHORT_LABELS[method], size=15, line_height=18))


def make_main_bar_figure(rows: list[dict[str, str]], path: Path, title: str, subtitle: str) -> None:
    width, height = 1120, 620
    elements: list[str] = []
    elements.append(svg_text(width / 2, 36, title, size=26, weight="700"))
    elements.append(svg_text(width / 2, 64, subtitle, size=17, fill="#555555"))
    ordered = method_sort(rows)
    max_tokens = max(f(row, "tokens_per_solved_task") or 0 for row in ordered)
    max_tokens = math.ceil(max_tokens / 20000) * 20000
    draw_bar_panel(
        elements,
        ordered,
        x0=40,
        y0=125,
        width=510,
        height=320,
        metric="solve_rate",
        title="Solve rate",
        y_label="Rate",
        max_value=1.0,
        value_formatter=lambda value: f"{value:.2f}",
    )
    draw_bar_panel(
        elements,
        ordered,
        x0=590,
        y0=125,
        width=510,
        height=320,
        metric="tokens_per_solved_task",
        title="Tokens per solved task",
        y_label="Tokens",
        max_value=max_tokens,
        value_formatter=lambda value: f"{value/1000:.0f}k",
    )
    elements.append(svg_text(width / 2, 590, "Lower token use indicates greater process efficiency among solved tasks.", size=16, fill="#555555"))
    write_svg(path, width, height, elements)


def make_protocol_diagram(path: Path) -> None:
    width, height = 1180, 560
    elements: list[str] = []
    elements.append(svg_text(width / 2, 34, "Evaluation protocol for procedural skill transfer", size=21, weight="700"))
    elements.append(svg_text(width / 2, 58, "Low-shot trajectories are compressed into a natural-language procedural memory artifact and compared against memory controls.", size=12, fill="#555555"))

    def box(x: float, y: float, w: float, h: float, lines: list[str], fill: str, stroke: str = "#444444") -> None:
        elements.append(svg_rect(x, y, w, h, fill, stroke=stroke, stroke_width=1.4, radius=6))
        elements.append(svg_multiline_text(x + w / 2, y + 32, lines, size=13, line_height=17))

    y_top = 125
    y_bot = 365
    w = 175
    h = 108
    xs = [55, 290, 525, 760, 995]

    elements.append(svg_text(377.5, 99, "Training experience", size=12, weight="700", fill="#0072B2"))
    elements.append(svg_text(965, 99, "Held-out evaluation", size=12, weight="700", fill="#333333"))

    box(xs[0], y_top, w, h, ["Low-shot", "debugging", "trajectories"], "#E8F1FA", "#0072B2")
    box(xs[1], y_top, w, h, ["Trajectory-to-", "SKILL.md", "induction"], "#E8F1FA", "#0072B2")
    box(xs[2], y_top, w, h, ["Auto SKILL.md", "Trigger", "Procedure", "Failures"], "#E8F1FA", "#0072B2")
    box(xs[3], y_top, w, h, ["Held-out", "debugging", "agent runs"], "#F0F0F0")
    box(xs[4], y_top, w, h, ["Metrics", "Solve rate", "Cycles", "Tokens", "Transfer"], "#F8F8F8")

    elements.append(svg_arrow(xs[0] + w, y_top + h / 2, xs[1] - 10, y_top + h / 2, stroke="#333333"))
    elements.append(svg_arrow(xs[1] + w, y_top + h / 2, xs[2] - 10, y_top + h / 2, stroke="#333333"))
    merge_x = 742
    merge_y = y_top + h / 2
    elements.append(svg_line(xs[2] + w, merge_y, merge_x, merge_y, stroke="#333333", stroke_width=2.0))
    elements.append(f'<circle cx="{merge_x}" cy="{merge_y}" r="5" fill="#333333" />')
    elements.append(svg_arrow(merge_x + 5, merge_y, xs[3] - 10, merge_y, stroke="#333333"))
    elements.append(svg_arrow(xs[3] + w, merge_y, xs[4] - 10, merge_y, stroke="#333333"))

    box(135, y_bot, 190, 88, ["No-memory", "baseline"], "#F4F4F4")
    box(365, y_bot, 190, 88, ["Reflexion-style", "memory"], "#FFF3E8", "#D55E00")
    box(595, y_bot, 190, 88, ["Length-matched", "Reflexion"], "#FCE8F4", "#CC79A7")
    box(825, y_bot, 190, 88, ["Generic debugging", "checklist"], "#E8F6F0", "#009E73")

    bus_y = y_bot - 32
    elements.append(svg_text(430, bus_y - 18, "Memory controls: same tasks, agent, and evaluation harness", size=13, weight="700"))
    for x in [230, 460, 690, 920]:
        elements.append(svg_line(x, y_bot, x, bus_y, stroke="#777777", stroke_width=1.8))
    elements.append(svg_line(230, bus_y, 920, bus_y, stroke="#777777", stroke_width=1.8))
    elements.append(svg_line(merge_x, bus_y, merge_x, merge_y + 5, stroke="#777777", stroke_width=1.8))

    elements.append(svg_text(width / 2, 525, "Primary claim target: low-shot within-family process efficiency with explicit negative-transfer accounting.", size=13, fill="#444444"))
    write_svg(path, width, height, elements)


def make_scatter_figure(rows: list[dict[str, str]], path: Path) -> None:
    width, height = 1000, 580
    x0, y0, plot_w, plot_h = 110, 105, 605, 375
    elements: list[str] = []
    elements.append(svg_text(width / 2, 38, "Process efficiency among solved tasks", size=26, weight="700"))
    elements.append(svg_text(width / 2, 68, "First-six hard tasks, same-model aggregate", size=17, fill="#555555"))
    ordered = method_sort(rows)
    max_x = max(f(row, "cycles_per_solved_task") or 0 for row in ordered)
    max_y = max(f(row, "tokens_per_solved_task") or 0 for row in ordered)
    x_max = math.ceil(max_x * 1.25 * 10) / 10
    y_max = math.ceil(max_y * 1.15 / 20000) * 20000
    y_base = y0 + plot_h

    for tick in range(0, int(math.ceil(x_max)) + 1):
        x = x0 + (tick / x_max) * plot_w
        elements.append(svg_line(x, y0, x, y_base, stroke="#E8E8E8"))
        elements.append(svg_text(x, y_base + 27, str(tick), size=15, fill="#555555"))
    for value in range(0, int(y_max) + 1, 20000):
        y = y_base - (value / y_max) * plot_h
        elements.append(svg_line(x0, y, x0 + plot_w, y, stroke="#E8E8E8"))
        elements.append(svg_text(x0 - 12, y + 5, f"{value//1000}k", size=15, anchor="end", fill="#555555"))

    elements.append(svg_line(x0, y0, x0, y_base, stroke="#333333"))
    elements.append(svg_line(x0, y_base, x0 + plot_w, y_base, stroke="#333333"))
    elements.append(svg_text(x0 + plot_w / 2, 548, "Diagnosis-edit-test cycles per solved task", size=18, weight="700"))
    elements.append(svg_text(30, y0 + plot_h / 2, "Tokens per solved task", size=18, weight="700", rotate=-90))

    marker_ids = {
        "auto_skill": "A",
        "generic_checklist": "G",
        "reflexion": "R",
        "length_matched_reflexion": "L",
        "no_memory": "N",
    }
    for row in ordered:
        method = row["method"]
        cycles = f(row, "cycles_per_solved_task") or 0
        tokens = f(row, "tokens_per_solved_task") or 0
        solve_rate = f(row, "solve_rate") or 0
        x = x0 + (cycles / x_max) * plot_w
        y = y_base - (tokens / y_max) * plot_h
        radius = 8 + solve_rate * 10
        elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{COLORS[method]}" opacity="0.88" stroke="#222222" stroke-width="1.0" />')
        marker_fill = "#222222" if method == "length_matched_reflexion" else "#FFFFFF"
        elements.append(svg_text(x, y + 5, marker_ids[method], size=14, weight="700", fill=marker_fill))

    legend_x = 755
    elements.append(svg_text(legend_x, 125, "Methods", size=18, anchor="start", weight="700"))
    for idx, row in enumerate(ordered):
        method = row["method"]
        y = 165 + idx * 54
        elements.append(f'<circle cx="{legend_x + 14}" cy="{y:.1f}" r="14" fill="{COLORS[method]}" opacity="0.88" stroke="#222222" stroke-width="1.0" />')
        marker_fill = "#222222" if method == "length_matched_reflexion" else "#FFFFFF"
        elements.append(svg_text(legend_x + 14, y + 5, marker_ids[method], size=13, weight="700", fill=marker_fill))
        elements.append(svg_text(legend_x + 40, y + 5, METHOD_LABELS[method], size=15, anchor="start", weight="700", fill="#222222"))

    write_svg(path, width, height, elements)


def make_heatmap(task_rows: list[dict[str, str]], path: Path, tasks: list[str]) -> None:
    width, height = 1040, 470
    elements: list[str] = []
    elements.append(svg_text(width / 2, 32, "Per-task outcomes on hard PyBugHive Black tasks", size=20, weight="700"))
    elements.append(svg_text(width / 2, 54, "First-six tasks only; green = solved, red = unsolved, NT = negative transfer", size=12, fill="#555555"))
    by_key = {(row["method"], row["task_id"]): row for row in task_rows}
    cell_w, cell_h = 105, 52
    x0, y0 = 255, 95

    for col, task in enumerate(tasks):
        label = task.replace("pybughive_black_", "black_")
        elements.append(svg_text(x0 + col * cell_w + cell_w / 2, y0 - 18, label, size=12, weight="700"))

    for row_idx, method in enumerate(METHOD_ORDER):
        y = y0 + row_idx * cell_h
        elements.append(svg_text(235, y + cell_h / 2 + 5, METHOD_LABELS[method], size=12, anchor="end", weight="700"))
        for col, task in enumerate(tasks):
            x = x0 + col * cell_w
            row = by_key.get((method, task))
            solved = i(row, "solved") if row else 0
            neg = (f(row, "negative_transfer_rate") or 0) > 0 if row else False
            fill = "#CFE8D5" if solved else "#F4C7C3"
            stroke = "#B00020" if neg else "#FFFFFF"
            stroke_width = 3 if neg else 1
            elements.append(svg_rect(x, y, cell_w - 3, cell_h - 3, fill, stroke=stroke, stroke_width=stroke_width, radius=2))
            text = "1" if solved else "0"
            elements.append(svg_text(x + cell_w / 2, y + 25, text, size=15, weight="700"))
            if neg:
                elements.append(svg_text(x + cell_w / 2, y + 43, "NT", size=10, weight="700", fill="#B00020"))

    legend_y = y0 + len(METHOD_ORDER) * cell_h + 26
    elements.append(svg_rect(330, legend_y, 18, 18, "#CFE8D5", stroke="#CCCCCC"))
    elements.append(svg_text(355, legend_y + 14, "Solved", size=12, anchor="start"))
    elements.append(svg_rect(430, legend_y, 18, 18, "#F4C7C3", stroke="#CCCCCC"))
    elements.append(svg_text(455, legend_y + 14, "Unsolved", size=12, anchor="start"))
    elements.append(svg_rect(555, legend_y, 18, 18, "#F4C7C3", stroke="#B00020", stroke_width=3))
    elements.append(svg_text(580, legend_y + 14, "Negative transfer flagged", size=12, anchor="start"))
    write_svg(path, width, height, elements)


def make_black234_figure(rows: list[dict[str, str]], path: Path) -> None:
    width, height = 760, 500
    elements: list[str] = []
    elements.append(svg_text(width / 2, 32, "pybughive_black_234 token cost by method", size=20, weight="700"))
    elements.append(svg_text(width / 2, 54, "Exploratory single-task result run with gpt-5.5", size=12, fill="#555555"))
    ordered = method_sort(rows)
    max_tokens = max(f(row, "tokens_per_solved_task") or 0 for row in ordered)
    max_tokens = math.ceil(max_tokens / 20000) * 20000
    draw_bar_panel(
        elements,
        ordered,
        x0=60,
        y0=95,
        width=650,
        height=280,
        metric="tokens_per_solved_task",
        title="Tokens per solved task",
        y_label="Tokens",
        max_value=max_tokens,
        value_formatter=lambda value: f"{value/1000:.0f}k",
    )
    elements.append(svg_text(width / 2, 465, "All five methods solved; this task separates mostly by token cost.", size=12, fill="#555555"))
    write_svg(path, width, height, elements)


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def latex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
    )


def latex_table(
    headers: list[str],
    rows: list[list[str]],
    caption: str,
    label: str,
    placement: str = "H",
) -> str:
    col_spec = "l" + "r" * (len(headers) - 1)
    lines = [
        f"\\begin{{table}}[{placement}]",
        "\\centering",
        "\\small",
        f"\\caption{{{latex_escape(caption)}}}",
        f"\\label{{{label}}}",
        "\\resizebox{\\linewidth}{!}{%",
        f"\\begin{{tabular}}{{{col_spec}}}",
        "\\toprule",
        " & ".join(latex_escape(h) for h in headers) + " \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(latex_escape(cell) for cell in row) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "}", "\\end{table}", ""])
    return "\n".join(lines)


def table_rows_for_method_metrics(rows: list[dict[str, str]]) -> list[list[str]]:
    out: list[list[str]] = []
    for row in method_sort(rows):
        solved = f"{i(row, 'solved')}/{i(row, 'n_tasks')}"
        out.append(
            [
                METHOD_LABELS[row["method"]],
                solved,
                fmt_float(f(row, "solve_rate"), 4),
                fmt_float(f(row, "cycles_per_solved_task"), 2),
                fmt_tokens(f(row, "tokens_per_solved_task")),
                fmt_float(f(row, "failed_patches_per_run"), 2),
                fmt_float(f(row, "negative_transfer_rate"), 4),
            ]
        )
    return out


def write_main_tables(first6: list[dict[str, str]], first7: list[dict[str, str]], black234: list[dict[str, str]]) -> None:
    headers = [
        "Method",
        "Solved",
        "Solve rate",
        "Cycles/solved",
        "Tokens/solved",
        "Failed patches/run",
        "Negative transfer",
    ]
    first6_rows = table_rows_for_method_metrics(first6)
    first7_rows = table_rows_for_method_metrics(first7)
    black_rows = table_rows_for_method_metrics(black234)
    (TABLE_DIR / "hard_first6_main_table.md").write_text(md_table(headers, first6_rows), encoding="utf-8")
    (TABLE_DIR / "hard_first7_exploratory_table.md").write_text(md_table(headers, first7_rows), encoding="utf-8")
    (TABLE_DIR / "black234_single_task_table.md").write_text(md_table(headers, black_rows), encoding="utf-8")
    (TABLE_DIR / "hard_first6_main_table.tex").write_text(
        latex_table(
            headers,
            first6_rows,
            "Same-model hard-smoke results over the first six PyBugHive Black tasks.",
            "tab:hard_first6_main",
            placement="t",
        ),
        encoding="utf-8",
    )
    (TABLE_DIR / "hard_first7_exploratory_table.tex").write_text(
        latex_table(
            headers,
            first7_rows,
            "Model-mixed exploratory results over all seven verified PyBugHive Black tasks.",
            "tab:hard_first7_exploratory",
        ),
        encoding="utf-8",
    )


def write_task_outcome_table(task_rows: list[dict[str, str]], tasks: list[str]) -> None:
    by_key = {(row["method"], row["task_id"]): row for row in task_rows}
    headers = ["Method"] + [task.replace("pybughive_black_", "black_") for task in tasks]
    rows: list[list[str]] = []
    for method in METHOD_ORDER:
        row = [METHOD_LABELS[method]]
        for task in tasks:
            metric = by_key[(method, task)]
            solved = i(metric, "solved")
            neg = (f(metric, "negative_transfer_rate") or 0) > 0
            row.append(f"{solved} (NT)" if neg else str(solved))
        rows.append(row)
    (TABLE_DIR / "hard_first6_task_outcomes.md").write_text(md_table(headers, rows), encoding="utf-8")


def write_common_solved_pairwise(task_rows: list[dict[str, str]], tasks: list[str]) -> list[dict[str, object]]:
    by_key = {(row["method"], row["task_id"]): row for row in task_rows}
    focal = "auto_skill"
    comparisons: list[dict[str, object]] = []
    for other in METHOD_ORDER:
        if other == focal:
            continue
        common = []
        for task in tasks:
            a = by_key[(focal, task)]
            b = by_key[(other, task)]
            if i(a, "solved") and i(b, "solved"):
                common.append(task)
        if common:
            a_cycles = sum(f(by_key[(focal, task)], "cycles_per_solved_task") or 0 for task in common) / len(common)
            b_cycles = sum(f(by_key[(other, task)], "cycles_per_solved_task") or 0 for task in common) / len(common)
            a_tokens = sum(f(by_key[(focal, task)], "tokens_per_solved_task") or 0 for task in common) / len(common)
            b_tokens = sum(f(by_key[(other, task)], "tokens_per_solved_task") or 0 for task in common) / len(common)
            cycle_reduction = (b_cycles - a_cycles) / b_cycles if b_cycles else 0
            token_reduction = (b_tokens - a_tokens) / b_tokens if b_tokens else 0
        else:
            a_cycles = b_cycles = a_tokens = b_tokens = cycle_reduction = token_reduction = 0
        comparisons.append(
            {
                "baseline": other,
                "common_tasks": common,
                "auto_cycles": a_cycles,
                "baseline_cycles": b_cycles,
                "cycle_reduction": cycle_reduction,
                "auto_tokens": a_tokens,
                "baseline_tokens": b_tokens,
                "token_reduction": token_reduction,
            }
        )

    headers = [
        "Baseline",
        "Common solved tasks",
        "Auto cycles",
        "Baseline cycles",
        "Cycle reduction",
        "Auto tokens",
        "Baseline tokens",
        "Token reduction",
    ]
    rows: list[list[str]] = []
    csv_rows: list[dict[str, str]] = []
    for item in comparisons:
        tasks_short = ", ".join(task.replace("pybughive_black_", "black_") for task in item["common_tasks"])  # type: ignore[index]
        row = [
            METHOD_LABELS[item["baseline"]],  # type: ignore[index]
            tasks_short,
            fmt_float(float(item["auto_cycles"]), 2),
            fmt_float(float(item["baseline_cycles"]), 2),
            f"{float(item['cycle_reduction']) * 100:.1f}%",
            fmt_tokens(float(item["auto_tokens"])),
            fmt_tokens(float(item["baseline_tokens"])),
            f"{float(item['token_reduction']) * 100:.1f}%",
        ]
        rows.append(row)
        csv_rows.append(
            {
                "baseline": str(item["baseline"]),
                "common_solved_tasks": tasks_short,
                "auto_cycles": fmt_float(float(item["auto_cycles"]), 4),
                "baseline_cycles": fmt_float(float(item["baseline_cycles"]), 4),
                "cycle_reduction_pct": f"{float(item['cycle_reduction']) * 100:.4f}",
                "auto_tokens": fmt_float(float(item["auto_tokens"]), 4),
                "baseline_tokens": fmt_float(float(item["baseline_tokens"]), 4),
                "token_reduction_pct": f"{float(item['token_reduction']) * 100:.4f}",
            }
        )
    (TABLE_DIR / "hard_first6_common_solved_pairwise.md").write_text(md_table(headers, rows), encoding="utf-8")
    with (TABLE_DIR / "hard_first6_common_solved_pairwise.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)
    return comparisons


def pct_reduction(baseline: float, focal: float) -> float:
    if baseline == 0:
        return 0.0
    return (baseline - focal) / baseline * 100


def row_by_method(rows: list[dict[str, str]], method: str) -> dict[str, str]:
    for row in rows:
        if row["method"] == method:
            return row
    raise KeyError(method)


def write_analysis_report(
    first6: list[dict[str, str]],
    first7: list[dict[str, str]],
    black234: list[dict[str, str]],
    pairwise: list[dict[str, object]],
) -> None:
    auto = row_by_method(first6, "auto_skill")
    reflexion = row_by_method(first6, "reflexion")
    length = row_by_method(first6, "length_matched_reflexion")
    nomem = row_by_method(first6, "no_memory")
    generic = row_by_method(first6, "generic_checklist")

    auto_tokens = f(auto, "tokens_per_solved_task") or 0
    auto_cycles = f(auto, "cycles_per_solved_task") or 0
    report = f"""# Results Analysis Package

Generated from local experiment outputs on 2026-06-02.

## Recommended Result Claim

The current evidence supports a cautious efficiency-and-transfer claim, not a broad dominance claim:

> On a same-model hard-smoke slice of six PyBugHive Black debugging tasks, Auto SKILL.md matched the best solve rate (5/6) while using fewer tokens per solved task than Reflexion-style memory, a length-matched Reflexion control, a generic debugging checklist, and no memory. The result suggests that natural-language procedural memory can improve low-shot within-family transfer efficiency, but it is subfamily-sensitive and can still produce negative transfer.

## Main Same-Model Evidence

Use the first-six result as the main quantitative table because all six tasks were run under the same model setup.

- Auto SKILL.md solved {i(auto, 'solved')}/{i(auto, 'n_tasks')} tasks, tied with Generic checklist and Reflexion memory for best solve rate.
- Auto SKILL.md used {fmt_tokens(auto_tokens)} tokens per solved task.
- Relative to Reflexion memory, Auto SKILL.md reduced cycles from {fmt_float(f(reflexion, 'cycles_per_solved_task'), 2)} to {fmt_float(auto_cycles, 2)} and tokens from {fmt_tokens(f(reflexion, 'tokens_per_solved_task'))} to {fmt_tokens(auto_tokens)}.
- Relative to length-matched Reflexion, Auto SKILL.md improved solve rate from {fmt_float(f(length, 'solve_rate'), 4)} to {fmt_float(f(auto, 'solve_rate'), 4)} and reduced tokens by {pct_reduction(f(length, 'tokens_per_solved_task') or 0, auto_tokens):.1f}%.
- Relative to no memory, Auto SKILL.md improved solve rate from {fmt_float(f(nomem, 'solve_rate'), 4)} to {fmt_float(f(auto, 'solve_rate'), 4)} and reduced tokens by {pct_reduction(f(nomem, 'tokens_per_solved_task') or 0, auto_tokens):.1f}%.
- Relative to Generic checklist, Auto SKILL.md had the same solve rate and cycle average, but used {pct_reduction(f(generic, 'tokens_per_solved_task') or 0, auto_tokens):.1f}% fewer tokens.

## Important Caveats

- The first-seven aggregate is model-mixed because pybughive_black_234 used gpt-5.5 after gpt-5.3-codex became unavailable. Treat it as exploratory.
- The current hard subset is Black-only and formatting-heavy. It is valuable for controlled within-family transfer, but not enough for a general agent-debugging claim.
- Negative transfer is not zero: Auto SKILL.md failed pybughive_black_132 and was flagged for negative transfer on that task.
- Do not claim statistical significance yet. With six same-model tasks, report exact task-level outcomes, paired common-solved comparisons, and qualitative case studies.

## Pairwise Common-Solved Efficiency

This analysis compares Auto SKILL.md against each baseline only on tasks both methods solved. It avoids comparing token averages over different solved-task sets.

See `paper/tables/hard_first6_common_solved_pairwise.md`.

"""
    for item in pairwise:
        baseline = METHOD_LABELS[item["baseline"]]  # type: ignore[index]
        tasks = ", ".join(task.replace("pybughive_black_", "black_") for task in item["common_tasks"])  # type: ignore[index]
        report += (
            f"- Against {baseline} on common solved tasks ({tasks}), Auto SKILL.md reduced "
            f"cycles by {float(item['cycle_reduction']) * 100:.1f}% and tokens by "
            f"{float(item['token_reduction']) * 100:.1f}%.\n"
        )

    report += f"""
## Figure Inventory

- `paper/figures/evaluation_protocol_diagram.svg`: method and evaluation protocol diagram.
- `paper/figures/hard_first6_main_bars.svg`: main same-model solve-rate and token-efficiency figure.
- `paper/figures/hard_first6_efficiency_scatter.svg`: cycles-vs-tokens process-efficiency figure.
- `paper/figures/hard_first6_task_outcomes_heatmap.svg`: per-task outcome heatmap with negative-transfer marker.
- `paper/figures/hard_first7_exploratory_bars.svg`: supplementary model-mixed all-seven figure.
- `paper/figures/black234_tokens.svg`: supplementary single-task token-cost figure for pybughive_black_234.

## Table Inventory

- `paper/tables/hard_first6_main_table.md` and `.tex`: main paper table.
- `paper/tables/hard_first6_task_outcomes.md`: per-task solve matrix.
- `paper/tables/hard_first6_common_solved_pairwise.md` and `.csv`: paired common-solved efficiency analysis.
- `paper/tables/hard_first7_exploratory_table.md` and `.tex`: supplementary model-mixed table.
- `paper/tables/black234_single_task_table.md`: single-task exploratory table.

## Draft Results Paragraph

Table 1 reports the same-model hard-smoke results over six PyBugHive Black tasks. Auto SKILL.md matched the strongest solve rate, solving 5/6 tasks, while reducing token cost relative to Reflexion memory, length-matched Reflexion, a generic debugging checklist, and the no-memory baseline. The gain is most clearly an efficiency result: compared with Reflexion, Auto SKILL.md achieved the same solve rate with fewer diagnosis-edit-test cycles and fewer tokens per solved task. Compared with length-matched Reflexion, it improved both solve rate and process efficiency, suggesting that the procedural structure of the memory artifact matters beyond adding more text to the context. The result is not uniformly positive: Auto SKILL.md failed on pybughive_black_132 and triggered the only negative-transfer flag. We therefore interpret SKILL.md as a subfamily-sensitive procedural memory artifact that can improve low-shot within-family transfer efficiency, rather than as a universally beneficial prompt.

## Suggested Paper Placement

- Main text Figure 1: `evaluation_protocol_diagram.svg`.
- Main text Figure 2: `hard_first6_main_bars.svg`.
- Main text Figure 3: `hard_first6_task_outcomes_heatmap.svg` or the process-efficiency scatter, depending on space.
- Main text Table 1: `hard_first6_main_table.tex`.
- Appendix: first-seven exploratory table, pybughive_black_234 single-task table, and pairwise common-solved table.
"""
    (PAPER_DIR / "results_analysis.md").write_text(report, encoding="utf-8")


def write_captions() -> None:
    figure_captions = """# Figure Captions

**Figure 1. Evaluation protocol for low-shot procedural skill transfer.** Historical debugging trajectories are compressed into a natural-language SKILL.md artifact containing trigger conditions, a debugging procedure, and failure modes. The same held-out debugging tasks are then run with Auto SKILL.md and four controls: no memory, a generic debugging checklist, Reflexion-style memory, and a length-matched Reflexion control. Outcomes are evaluated by solve rate, diagnosis-edit-test cycles, token cost, repeated mistakes, and negative transfer.

**Figure 2. Same-model hard-smoke aggregate over the first six PyBugHive Black tasks.** Auto SKILL.md matches the strongest solve rate while using fewer tokens per solved task than the memory and no-memory controls. Because the comparison is solve-conditional, the per-task outcome heatmap and paired common-solved table should be reported alongside this figure.

**Figure 3. Process efficiency among solved hard-smoke tasks.** Points show each method's average diagnosis-edit-test cycles and tokens per solved task over the same-model first-six aggregate. Lower-left indicates more efficient successful repair behavior; marker size encodes solve rate.

**Figure 4. Per-task outcome matrix for the first-six hard-smoke tasks.** Green cells indicate solved tasks, red cells indicate unsolved tasks, and NT marks the negative-transfer flag. This figure makes the subfamily-sensitive nature of procedural memory visible: Auto SKILL.md wins on black_193 and black_232 but fails with negative transfer on black_132.

**Figure S1. Model-mixed exploratory all-seven aggregate.** This supplementary figure includes pybughive_black_234, which was run with gpt-5.5 after gpt-5.3-codex became unavailable. Use it as a robustness/completion check, not as the primary same-model claim.

**Figure S2. pybughive_black_234 token cost by method.** All five methods solved the task. The task primarily separates methods by token cost rather than solve rate or cycles.
"""
    table_captions = """# Table Captions

**Table 1. Same-model hard-smoke results over six PyBugHive Black debugging tasks.** Auto SKILL.md ties the best solve rate and has the lowest token cost per solved task. This table should be the main quantitative result because all included runs share the same model setup.

**Table 2. Per-task solve matrix for the same-model hard-smoke tasks.** This table reports exact task-level outcomes and negative-transfer flags, making clear that the evidence is subfamily-sensitive rather than uniformly positive.

**Table 3. Paired common-solved efficiency comparison.** Auto SKILL.md is compared against each baseline only on tasks both methods solved, reducing the risk that solve-conditional token averages are driven by different solved-task sets.

**Table S1. Model-mixed all-seven exploratory aggregate.** Includes pybughive_black_234 under gpt-5.5 and should be treated as supplementary until all tasks are rerun under one model.

**Table S2. pybughive_black_234 single-task exploratory result.** All methods solved, so the task is useful mainly for token-cost and qualitative patch-behavior discussion.
"""
    (PAPER_DIR / "figure_captions.md").write_text(figure_captions, encoding="utf-8")
    (PAPER_DIR / "table_captions.md").write_text(table_captions, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    first6 = read_rows(RESULTS_DIR / "pybughive_hard_first6_by_method_metrics.csv")
    first6_task = read_rows(RESULTS_DIR / "pybughive_hard_first6_by_task_metrics.csv")
    first7 = read_rows(RESULTS_DIR / "pybughive_hard_first7_by_method_metrics.csv")
    black234 = read_rows(RESULTS_DIR / "pybughive_hard_black234_only_smoke_metrics.csv")

    first6_tasks = [
        "pybughive_black_132",
        "pybughive_black_133",
        "pybughive_black_154",
        "pybughive_black_183",
        "pybughive_black_193",
        "pybughive_black_232",
    ]

    write_main_tables(first6, first7, black234)
    write_task_outcome_table(first6_task, first6_tasks)
    pairwise = write_common_solved_pairwise(first6_task, first6_tasks)

    make_protocol_diagram(FIGURE_DIR / "evaluation_protocol_diagram.svg")
    make_main_bar_figure(
        first6,
        FIGURE_DIR / "hard_first6_main_bars.svg",
        "Hard-smoke same-model results",
        "First six PyBugHive Black tasks",
    )
    make_scatter_figure(first6, FIGURE_DIR / "hard_first6_efficiency_scatter.svg")
    make_heatmap(first6_task, FIGURE_DIR / "hard_first6_task_outcomes_heatmap.svg", first6_tasks)
    make_main_bar_figure(
        first7,
        FIGURE_DIR / "hard_first7_exploratory_bars.svg",
        "Exploratory all-seven results",
        "Model-mixed aggregate; use as supplementary evidence",
    )
    make_black234_figure(black234, FIGURE_DIR / "black234_tokens.svg")
    write_analysis_report(first6, first7, black234, pairwise)
    write_captions()

    print("Wrote paper result package:")
    for path in [
        PAPER_DIR / "results_analysis.md",
        PAPER_DIR / "figure_captions.md",
        PAPER_DIR / "table_captions.md",
        FIGURE_DIR / "evaluation_protocol_diagram.svg",
        FIGURE_DIR / "hard_first6_main_bars.svg",
        FIGURE_DIR / "hard_first6_efficiency_scatter.svg",
        FIGURE_DIR / "hard_first6_task_outcomes_heatmap.svg",
        FIGURE_DIR / "hard_first7_exploratory_bars.svg",
        FIGURE_DIR / "black234_tokens.svg",
        TABLE_DIR / "hard_first6_main_table.md",
        TABLE_DIR / "hard_first6_main_table.tex",
        TABLE_DIR / "hard_first6_common_solved_pairwise.md",
    ]:
        print(f"- {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
