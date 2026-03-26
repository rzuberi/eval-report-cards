"""Input and output helpers."""

from __future__ import annotations

import csv
import json
import os
import tomllib
from typing import Any


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def coerce_scalar(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if text == "":
        return value
    lowered = text.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    try:
        if "." not in text and "e" not in lowered:
            return int(text)
        return float(text)
    except ValueError:
        return value


def load_table(path: str) -> list[dict[str, Any]]:
    suffix = os.path.splitext(path)[1].lower()
    if suffix in (".csv", ".tsv"):
        delimiter = "\t" if suffix == ".tsv" else ","
        with open(path, newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            return [{key: coerce_scalar(value) for key, value in row.items()} for row in reader]
    if suffix == ".jsonl":
        rows = []
        with open(path) as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows
    if suffix == ".json":
        with open(path) as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("records"), list):
            return payload["records"]
    raise ValueError("Unsupported table format for %s" % path)


def load_mapping(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    suffix = os.path.splitext(path)[1].lower()
    if suffix == ".json":
        with open(path) as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {"payload": payload}
    if suffix == ".toml":
        with open(path, "rb") as handle:
            payload = tomllib.load(handle)
        return payload if isinstance(payload, dict) else {"payload": payload}
    if suffix in (".csv", ".tsv"):
        delimiter = "\t" if suffix == ".tsv" else ","
        with open(path, newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            mapping: dict[str, Any] = {}
            for row in reader:
                if "metric" in row and "value" in row:
                    mapping[row["metric"]] = coerce_scalar(row["value"])
            return mapping
    raise ValueError("Unsupported mapping format for %s" % path)


def write_json(path: str, payload: dict[str, Any]) -> None:
    with open(path, "w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: str, content: str) -> None:
    with open(path, "w") as handle:
        handle.write(content)

