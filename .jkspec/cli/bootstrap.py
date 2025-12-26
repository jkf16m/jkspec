#!/usr/bin/env python3
"""Bootstrap entrypoint that outputs the worker configuration for context initialization.

This utility executes the first command defined in the worker bootstrap config,
which displays a high-level overview of the worker object for agent context.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def resolve_repo_root() -> Path:
    """Return repository root (two levels up from this file)."""
    return Path(__file__).resolve().parents[2]


def main() -> None:
    """Run the bootstrap command to output worker configuration."""
    root = resolve_repo_root()
    source_path = root / ".jkspec" / "source.json"

    if not source_path.exists():
        print(f"error: source.json not found at {source_path}", file=sys.stderr)
        sys.exit(1)

    # Execute the first_command defined in worker.bootstrap
    cmd = [
        "jq",
        '.specs.__jkspec.components.worker | with_entries(.value |= (if type == "object" then .description else . end))',
        str(source_path),
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout, end="")
    except subprocess.CalledProcessError as exc:
        print(f"error: bootstrap command failed: {exc.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("error: jq command not found - please install jq", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
