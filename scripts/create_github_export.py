from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "github_export"

TEXT_SUFFIXES = {
    ".bib",
    ".csv",
    ".json",
    ".md",
    ".patch",
    ".py",
    ".svg",
    ".tex",
    ".toml",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}

ROOT_FILES = [
    ".gitattributes",
    ".gitignore",
    "README.md",
    "requirements.txt",
    "SESSION_HANDOFF.md",
]

ROOT_DIRS = [
    "annotation",
    "artifact_agenticdev2026",
    "baselines",
    "data",
    "docker",
    "docs",
    "fixtures",
    "manifests",
    "memory",
    "paper",
    "patches",
    "prompts",
    "results",
    "schemas",
    "scripts",
    "tasks",
    "trajectories",
]

EXCLUDED_DIRS = {
    Path(".git"),
    Path("data") / "external",
    Path("logs"),
    Path("prompts") / "runs",
    Path("runs"),
    Path("workspaces"),
    Path("github_export"),
    Path("paper") / "render_agenticdev",
    Path("paper") / "svg-inkscape",
    Path("scripts") / "__pycache__",
}

EXCLUDED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".bcf",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pdf",
    ".png",
    ".pyc",
    ".run.xml",
    ".synctex.gz",
    ".toc",
    ".xdv",
    ".xmpi",
}


def normalize_relative(path: Path) -> Path:
    return Path(*path.parts)


def ensure_within(parent: Path, child: Path) -> None:
    parent_resolved = parent.resolve()
    child_resolved = child.resolve()
    try:
        child_resolved.relative_to(parent_resolved)
    except ValueError as exc:
        raise ValueError(f"Refusing to operate outside workspace: {child_resolved}") from exc


def is_excluded_dir(relative_path: Path) -> bool:
    normalized = normalize_relative(relative_path)
    return any(normalized == item or item in normalized.parents for item in EXCLUDED_DIRS)


def is_excluded_file(relative_path: Path) -> bool:
    name = relative_path.name
    if name.endswith(".synctex.gz") or name.endswith(".run.xml"):
        return True
    return relative_path.suffix.lower() in EXCLUDED_SUFFIXES


def sanitize_text(text: str) -> str:
    root_posix = ROOT.as_posix()
    wsl_root = ""
    if len(root_posix) >= 2 and root_posix[1] == ":":
        wsl_root = f"/mnt/{root_posix[0].lower()}{root_posix[2:]}"

    local_python = Path.home() / "AppData" / "Local" / "Python"
    local_programs_python = Path.home() / "AppData" / "Local" / "Programs" / "Python"

    replacements = {
        str(ROOT): "<PROJECT_ROOT>",
        str(ROOT).replace("\\", "\\\\"): "<PROJECT_ROOT>",
        root_posix: "<PROJECT_ROOT>",
        str(local_python): "<LOCAL_PYTHON>",
        str(local_python).replace("\\", "\\\\"): "<LOCAL_PYTHON>",
        str(local_programs_python): "<LOCAL_PYTHON>",
        str(local_programs_python).replace("\\", "\\\\"): "<LOCAL_PYTHON>",
    }
    if wsl_root:
        replacements[wsl_root] = "<PROJECT_ROOT>"

    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() in TEXT_SUFFIXES:
        text = source.read_text(encoding="utf-8-sig")
        destination.write_text(sanitize_text(text), encoding="utf-8", newline="\n")
    else:
        shutil.copy2(source, destination)


def copy_tree(source_root: Path, destination_root: Path, relative_root: Path) -> tuple[int, int]:
    copied_files = 0
    skipped_files = 0
    for source in sorted(source_root.rglob("*")):
        relative = relative_root / source.relative_to(source_root)
        if source.is_dir():
            if is_excluded_dir(relative):
                continue
            (destination_root / relative).mkdir(parents=True, exist_ok=True)
            continue
        if is_excluded_dir(relative.parent) or is_excluded_file(relative):
            skipped_files += 1
            continue
        copy_file(source, destination_root / relative)
        copied_files += 1
    return copied_files, skipped_files


def build_export(output: Path, force: bool) -> dict[str, int]:
    output = output.resolve()
    ensure_within(ROOT, output)

    if output.exists():
        if not force:
            raise FileExistsError(f"{output} already exists; pass --force to recreate it")
        shutil.rmtree(output)
    output.mkdir(parents=True)

    copied_files = 0
    skipped_files = 0

    for file_name in ROOT_FILES:
        source = ROOT / file_name
        if source.exists():
            copy_file(source, output / file_name)
            copied_files += 1

    for dir_name in ROOT_DIRS:
        source = ROOT / dir_name
        if not source.exists():
            continue
        files, skipped = copy_tree(source, output, Path(dir_name))
        copied_files += files
        skipped_files += skipped

    return {"copied_files": copied_files, "skipped_files": skipped_files}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a clean GitHub export directory.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Export directory (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument("--force", action="store_true", help="Recreate an existing export")
    args = parser.parse_args()

    stats = build_export(args.output, args.force)
    print(f"Wrote {args.output.resolve()}")
    print(f"Copied files: {stats['copied_files']}")
    print(f"Skipped generated/local files: {stats['skipped_files']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
