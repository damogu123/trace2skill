from __future__ import annotations

import argparse
import random
import re
import sys
from pathlib import Path


HEADING_RE = re.compile(r"^#{1,6}\s+")
LIST_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :])
    return text


def normalize_unit(line: str) -> str:
    line = line.strip()
    line = LIST_RE.sub("", line).strip()
    return line


def extract_units(markdown: str) -> list[str]:
    body = strip_frontmatter(markdown)
    units: list[str] = []
    in_code_block = False

    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not line:
            continue
        if HEADING_RE.match(line):
            continue
        if line.startswith("|"):
            continue
        unit = normalize_unit(line)
        if unit:
            units.append(unit)
    return units


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def build_shuffled_markdown(units: list[str], seed: int) -> str:
    shuffled = list(units)
    random.Random(seed).shuffle(shuffled)
    bullets = "\n".join(f"- {unit}" for unit in shuffled)
    return (
        "# Debugging Notes\n\n"
        "The following notes were derived from prior debugging experience.\n\n"
        f"{bullets}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a format-shuffled baseline from an Auto-SKILL.md file."
    )
    parser.add_argument("input", type=Path, help="Path to Auto-SKILL.md")
    parser.add_argument("output", type=Path, help="Path for shuffled Markdown output")
    parser.add_argument("--seed", type=int, default=1, help="Shuffle seed")
    parser.add_argument(
        "--max-delta",
        type=float,
        default=0.10,
        help="Allowed word-count delta ratio before warning (default: 0.10)",
    )
    args = parser.parse_args()

    source = args.input.read_text(encoding="utf-8")
    units = extract_units(source)
    if not units:
        print(f"No shuffleable content found in {args.input}", file=sys.stderr)
        return 1

    shuffled = build_shuffled_markdown(units, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(shuffled, encoding="utf-8", newline="\n")

    source_words = word_count(strip_frontmatter(source))
    shuffled_words = word_count(shuffled)
    delta = (shuffled_words - source_words) / max(source_words, 1)
    print(f"Wrote {args.output}")
    print(f"source_words={source_words} shuffled_words={shuffled_words} delta={delta:.2%}")
    if abs(delta) > args.max_delta:
        print(
            "Warning: shuffled output differs from source by more than "
            f"{args.max_delta:.0%}. Review whether headings/frontmatter explain the gap.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

