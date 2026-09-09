from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class ProjectPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.html_lang = ""
        self.json_ld_blocks: list[str] = []
        self._json_ld_buffer: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value for name, value in attrs if value is not None}
        if tag == "html":
            self.html_lang = values.get("lang", "")
        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.add(element_id)
            self.ids.add(element_id)
        for attribute in ("href", "src", "data"):
            reference = values.get(attribute)
            if reference:
                self.references.append(reference)
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._json_ld_buffer = []

    def handle_data(self, data: str) -> None:
        if self._json_ld_buffer is not None:
            self._json_ld_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_ld_buffer is not None:
            self.json_ld_blocks.append("".join(self._json_ld_buffer))
            self._json_ld_buffer = None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate local resources and structured metadata for the project page."
    )
    parser.add_argument("docs_root", type=Path, nargs="?", default=Path("docs"))
    args = parser.parse_args()

    docs_root = args.docs_root.resolve()
    index = docs_root / "index.html"
    if not index.is_file():
        print(f"ERROR: project page does not exist: {index}", file=sys.stderr)
        return 1

    document = index.read_text(encoding="utf-8-sig")
    page = ProjectPageParser()
    page.feed(document)
    errors: list[str] = []

    if page.html_lang.lower() != "zh-cn":
        errors.append(
            f"the html lang attribute must be zh-CN, found {page.html_lang or 'missing'}"
        )
    if page.duplicate_ids:
        errors.append(f"duplicate element IDs: {', '.join(sorted(page.duplicate_ids))}")

    local_targets: set[Path] = set()
    pdf_targets: set[Path] = set()
    for reference in page.references:
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc or reference.startswith("//"):
            continue
        relative_path = unquote(parsed.path)
        target = index if not relative_path else index.parent / relative_path.lstrip("/")
        target = target.resolve()
        try:
            target.relative_to(docs_root)
        except ValueError:
            errors.append(f"local reference escapes docs root: {reference}")
            continue
        if not target.exists():
            errors.append(f"missing local resource: {reference}")
            continue
        local_targets.add(target)
        if target.suffix.lower() == ".pdf":
            pdf_targets.add(target)
        if parsed.fragment and target == index and parsed.fragment not in page.ids:
            errors.append(f"missing fragment target: #{parsed.fragment}")

    if not page.json_ld_blocks:
        errors.append("no application/ld+json metadata block found")
    for block_number, block in enumerate(page.json_ld_blocks, start=1):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON-LD block {block_number}: {exc}")

    svg_files = sorted((docs_root / "static" / "images").glob("*.svg"))
    for svg_file in svg_files:
        try:
            ET.parse(svg_file)
        except ET.ParseError as exc:
            errors.append(f"invalid SVG {svg_file.relative_to(docs_root)}: {exc}")

    for pdf_file in pdf_targets:
        if not pdf_file.read_bytes().startswith(b"%PDF-"):
            errors.append(f"invalid PDF header: {pdf_file.relative_to(docs_root)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"OK {index}: lang={page.html_lang}, {len(local_targets)} local resources, "
        f"{len(page.ids)} IDs, {len(page.json_ld_blocks)} JSON-LD block(s), "
        f"{len(svg_files)} SVG files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
