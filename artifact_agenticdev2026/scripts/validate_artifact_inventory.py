from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path


IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an artifact FILE_INVENTORY.tsv against files on disk."
    )
    parser.add_argument("artifact_root", type=Path)
    parser.add_argument("--inventory", type=Path)
    args = parser.parse_args()

    root = args.artifact_root.resolve()
    inventory = (args.inventory or root / "FILE_INVENTORY.tsv").resolve()
    errors: list[str] = []

    if not root.is_dir():
        print(f"ERROR: artifact root is not a directory: {root}", file=sys.stderr)
        return 1
    if not inventory.is_file():
        print(f"ERROR: inventory does not exist: {inventory}", file=sys.stderr)
        return 1

    inventory_relative = inventory.relative_to(root).as_posix()
    expected: dict[str, tuple[int, str]] = {}
    with inventory.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"path", "bytes", "sha256"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            print("ERROR: inventory must contain path, bytes, and sha256 columns", file=sys.stderr)
            return 1

        for line_number, row in enumerate(reader, start=2):
            raw_path = row["path"]
            if raw_path in expected:
                errors.append(f"duplicate inventory path on line {line_number}: {raw_path}")
                continue
            try:
                size = int(row["bytes"])
            except ValueError:
                errors.append(f"invalid byte count on line {line_number}: {row['bytes']}")
                continue
            digest = row["sha256"].lower()
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                errors.append(f"invalid SHA-256 on line {line_number}: {digest}")
                continue
            expected[raw_path] = (size, digest)

    actual = {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
        and path.resolve() != inventory
        and not is_ignored(path.relative_to(root))
    }

    for relative, (expected_size, expected_hash) in expected.items():
        candidate = (root / Path(relative)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"inventory path escapes artifact root: {relative}")
            continue
        if relative not in actual:
            errors.append(f"missing file: {relative}")
            continue
        actual_size = candidate.stat().st_size
        if actual_size != expected_size:
            errors.append(
                f"size mismatch: {relative} (expected {expected_size}, found {actual_size})"
            )
        actual_hash = sha256(candidate)
        if actual_hash != expected_hash:
            errors.append(f"SHA-256 mismatch: {relative}")

    for relative in sorted(set(actual) - set(expected)):
        errors.append(f"file missing from inventory: {relative}")

    if inventory_relative in expected:
        errors.append("FILE_INVENTORY.tsv must not list itself")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK {inventory}: {len(expected)} files verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
