from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class ValidationError(ValueError):
    """Validation error with a JSON-path-like location."""

    def __init__(self, path: str, message: str) -> None:
        super().__init__(f"{path}: {message}")
        self.path = path
        self.message = message


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValidationError("$schema", f"unsupported schema type {expected!r}")


def _format_expected_type(expected: Any) -> str:
    if isinstance(expected, list):
        return " or ".join(str(item) for item in expected)
    return str(expected)


def validate_instance(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    """Validate the subset of JSON Schema used by this project.

    This is intentionally small and dependency-free. It supports the fields used
    by schemas/task.schema.json and schemas/trajectory.schema.json: type,
    required, properties, additionalProperties=false, enum, items, minItems, and
    minimum.
    """

    expected_type = schema.get("type")
    if expected_type is not None:
        allowed = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_type_matches(value, item) for item in allowed):
            raise ValidationError(
                path,
                f"expected {_format_expected_type(expected_type)}, got {type(value).__name__}",
            )

    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(path, f"expected one of {schema['enum']!r}, got {value!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema:
        if value < schema["minimum"]:
            raise ValidationError(path, f"expected >= {schema['minimum']}, got {value}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise ValidationError(path, f"expected at least {schema['minItems']} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                validate_instance(item, item_schema, f"{path}[{index}]")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ValidationError(path, f"missing required property {key!r}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                raise ValidationError(path, f"unexpected properties: {', '.join(extra)}")

        for key, child_schema in properties.items():
            if key in value:
                validate_instance(value[key], child_schema, f"{path}.{key}")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def iter_json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(item for item in path.rglob("*.json") if item.is_file())
    raise FileNotFoundError(path)


def validate_json_files(target: Path, schema_path: Path) -> int:
    schema = load_json(schema_path)
    files = iter_json_files(target)
    if not files:
        print(f"No JSON files found under {target}")
        return 1

    failures = 0
    for file_path in files:
        try:
            data = load_json(file_path)
            validate_instance(data, schema)
            print(f"OK {file_path}")
        except Exception as exc:  # Keep CLI output compact and actionable.
            failures += 1
            print(f"FAIL {file_path}: {exc}")
    return 1 if failures else 0


def build_parser(description: str, default_schema: Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("target", type=Path, help="JSON file or directory to validate")
    parser.add_argument(
        "--schema",
        type=Path,
        default=default_schema,
        help=f"Schema path (default: {default_schema})",
    )
    return parser
