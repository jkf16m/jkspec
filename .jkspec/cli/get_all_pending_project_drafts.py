#!/usr/bin/env python3
"""List dot-delimited paths for all draft project specs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_DIR = REPO_ROOT / ".jkspec-project"
PROJECT_PATH = PROJECT_DIR / "project.json"

PROJECT_TEMPLATE = {
    "project": {
        "name": "your-project-name",
        "description": "Your project description",
        "version": "0.1.0",
        "architecture": {
            "style": "Define your architecture style",
            "pattern": "Define your patterns",
        },
        "conventions": {
            "spec_location": ".jkspec-project/project.json",
        },
        "decisions": [],
    },
    "specs": {},
}


def ensure_project_file(path: Path) -> dict:
    if not path.exists():
        PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(PROJECT_TEMPLATE, handle, indent=2)
    with path.open("r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
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


def include_project_spec(path: List[str]) -> bool:
    return len(path) >= 1 and path[0] == "specs"


def main() -> None:
    data = ensure_project_file(PROJECT_PATH)
    draft_paths = sorted(
        ".".join(path)
        for path in iter_draft_paths(data, [])
        if include_project_spec(path)
    )

    for entry in draft_paths:
        print(entry)

    if draft_paths:
        raise SystemExit(0)

    raise SystemExit(2)


if __name__ == "__main__":
    main()
