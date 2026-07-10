from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _schema_validate import load_json, validate_instance


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "run_manifest.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy a run manifest while updating model metadata.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    manifest: dict[str, Any] = load_json(args.input)
    validate_instance(manifest, load_json(args.schema))
    manifest["model"] = args.model
    if args.temperature is not None:
        manifest["temperature"] = args.temperature
    if args.notes is not None:
        manifest["notes"] = args.notes
    validate_instance(manifest, load_json(args.schema))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
