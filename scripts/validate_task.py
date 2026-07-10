from __future__ import annotations

import sys
from pathlib import Path

from _schema_validate import build_parser, validate_json_files


DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "task.schema.json"


def main() -> int:
    parser = build_parser("Validate debugging task JSON files.", DEFAULT_SCHEMA)
    args = parser.parse_args()
    return validate_json_files(args.target, args.schema)


if __name__ == "__main__":
    sys.exit(main())

