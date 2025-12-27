#!/usr/bin/env python3
"""Bootstrap project principles for worker context initialization.

This utility outputs a summary of the project object from .jkspec-project/project.json
to initialize the worker with project-specific context before working with user specs.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def resolve_repo_root() -> Path:
    """Return repository root (two levels up from this file)."""
    return Path(__file__).resolve().parents[2]


def create_minimal_project_json(project_path: Path) -> None:
    """Create a minimal project.json file if it doesn't exist."""
    project_dir = project_path.parent
    project_dir.mkdir(parents=True, exist_ok=True)

    minimal_project = {
        "project": {
            "__meta": {
                "description": "User project specifications",
                "done": False,
                "goal": "Project structure initialized",
            },
            "name": "user-project",
            "version": "0.1.0",
        },
        "specs": {},
    }

    with open(project_path, "w") as f:
        json.dump(minimal_project, f, indent=2)

    print(f"Created minimal project.json at {project_path}", file=sys.stderr)


def main() -> None:
    """Run the project bootstrap to output project configuration."""
    root = resolve_repo_root()
    project_path = root / ".jkspec-project" / "project.json"

    # Auto-create project.json if it doesn't exist
    if not project_path.exists():
        print(
            "Project file does not exist - creating minimal template", file=sys.stderr
        )
        create_minimal_project_json(project_path)

    # Load and summarize the project object
    try:
        with open(project_path) as f:
            project_data = json.load(f)
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"error: failed to load project config: {exc}", file=sys.stderr)
        sys.exit(1)

    # Build jq filter to summarize the project object
    # Keep primitive fields, summarize nested objects with their description
    jq_filter = (
        ".project | "
        'with_entries(.value |= (if type == "object" then (.description // "nested object") else . end))'
    )

    cmd = ["jq", jq_filter, str(project_path)]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout, end="")
    except subprocess.CalledProcessError as exc:
        print(f"error: project bootstrap command failed: {exc.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("error: jq command not found - please install jq", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
