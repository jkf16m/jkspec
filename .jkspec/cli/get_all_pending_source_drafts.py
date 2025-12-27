#!/usr/bin/env python3
"""List dot-delimited paths for all draft internal specs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPO_ROOT / ".jkspec" / "source.json"


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        print(f"error: missing required file: {path}", file=sys.stderr)
        raise SystemExit(1) from exc
    except json.JSONDecodeError as exc:
        print(f"error: failed to parse JSON at {path}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def iter_draft_paths(node, path: List[str]) -> Iterable[List[str]]:
    if isinstance(node, dict):
        meta = node.get("__meta")
        if isinstance(meta, dict) and meta.get("status") == "draft":
            yield path
        for key, value in node.items():
            yield from iter_draft_paths(value, path + [str(key)])
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            yield from iter_draft_paths(value, path + [str(idx)])


def include_internal_spec(path: List[str]) -> bool:
    return len(path) >= 2 and path[0] == "specs" and path[1] == "__jkspec"


def main() -> None:
    data = load_json(SOURCE_PATH)
    
    # Convert to dot-delimited strings
    draft_paths = [
        ".".join(path)
        for path in iter_draft_paths(data, [])
        if include_internal_spec(path)
    ]
    
    # Sort by path length (most specific first = longest path = most dots)
    # Then alphabetically for same length
    draft_paths.sort(key=lambda p: (-p.count('.'), p))

    for entry in draft_paths:
        print(entry)

    if draft_paths:
        raise SystemExit(0)

    raise SystemExit(2)


if __name__ == "__main__":
    main()
