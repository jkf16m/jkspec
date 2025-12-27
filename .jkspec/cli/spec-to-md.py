#!/usr/bin/env python3
"""
spec-to-md.py - Cross-platform JSON to Markdown renderer for jkspec

Renders any JSON path into human-readable Markdown for change review.
"""

import json
import sys
import os
from pathlib import Path
from typing import Any, Optional


def sanitize_path_for_filename(json_path: str) -> str:
    """Convert JSON path to safe filename (dots to underscores)."""
    return json_path.replace(".", "_")


def resolve_json_path(data: dict, path: str) -> Optional[Any]:
    """
    Traverse nested JSON structure using dot-notation path.

    Args:
        data: The JSON data dictionary
        path: Dot-notation path (e.g., "specs.__jkspec.components.worker")

    Returns:
        The value at the path, or None if not found
    """
    parts = path.split(".")
    current = data

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None

    return current


def render_meta(meta: dict, level: int = 2, indent: int = 0) -> str:
    """Render __meta object with special formatting."""
    if not meta or not isinstance(meta, dict):
        return ""

    indent_str = "  " * indent
    lines = []

    # Use heading or list item depending on level
    if level <= 6:
        lines.append(f"{'#' * level} Meta\n")
    else:
        lines.append(f"{indent_str}- **Meta**")

    # Render in priority order
    list_indent = "  " * (indent + 1) if level > 6 else ""
    if "status" in meta:
        lines.append(f"{list_indent}- **Status:** `{meta['status']}`")
    if "type" in meta:
        lines.append(f"{list_indent}- **Type:** `{meta['type']}`")
    if "description" in meta:
        lines.append(f"{list_indent}- **Description:** {meta['description']}")
    if "goal" in meta:
        lines.append(f"{list_indent}- **Goal:** {meta['goal']}")
    if "tags" in meta and isinstance(meta["tags"], list):
        tags_str = ", ".join(f"`{tag}`" for tag in meta["tags"])
        lines.append(f"{list_indent}- **Tags:** {tags_str}")

    # Render any other fields
    standard_fields = {"status", "type", "description", "goal", "tags"}
    for key, value in meta.items():
        if key not in standard_fields:
            lines.append(f"{list_indent}- **{key}:** {value}")

    return "\n".join(lines) + "\n"


def render_array(arr: list, level: int = 2, indent: int = 0) -> str:
    """Render array as numbered or bulleted list."""
    if not arr:
        return ""

    lines = []
    indent_str = "  " * indent

    for i, item in enumerate(arr, 1):
        if isinstance(item, dict):
            # For object items, show title/name if available
            title = (
                item.get("title")
                or item.get("name")
                or item.get("description", f"Item {i}")
            )
            lines.append(f"{indent_str}{i}. **{title}**")

            # Render nested content with indentation
            for key, value in item.items():
                if key in ("title", "name"):
                    continue  # Already used as title
                if key == "__meta":
                    continue  # Skip meta in nested items for brevity

                if isinstance(value, (str, int, float, bool)):
                    lines.append(f"{indent_str}   - **{key}:** {value}")
                elif isinstance(value, list):
                    lines.append(f"{indent_str}   - **{key}:**")
                    for sub_item in value:
                        lines.append(f"{indent_str}     - {sub_item}")
                elif isinstance(value, dict):
                    lines.append(f"{indent_str}   - **{key}:** (nested object)")

        elif isinstance(item, str):
            lines.append(f"{indent_str}- {item}")
        else:
            lines.append(f"{indent_str}- {item}")

    return "\n".join(lines) + "\n"


def render_object(
    obj: dict, level: int = 2, parent_key: str = "", indent: int = 0
) -> str:
    """
    Render nested object as markdown sections.

    Uses headings for levels 1-6, then switches to nested lists for deeper levels.
    This respects Markdown's 6-heading-level limit while maintaining hierarchy.
    """
    if not obj or not isinstance(obj, dict):
        return ""

    lines = []
    indent_str = "  " * indent

    # Render __meta first if present
    if "__meta" in obj:
        lines.append(render_meta(obj["__meta"], level, indent))

    # Render other fields
    for key, value in obj.items():
        if key == "__meta":
            continue  # Already rendered

        # Format the key as title
        title = key.replace("_", " ").title()

        # Use heading if level <= 6, otherwise use nested list item
        if level <= 6:
            heading = f"{'#' * level} {title}\n"
        else:
            heading = f"{indent_str}- **{title}**\n"

        if value is None:
            lines.append(heading)
            if level <= 6:
                lines.append("_(not set)_\n")
            else:
                lines.append(f"{indent_str}  _(not set)_\n")

        elif isinstance(value, bool):
            lines.append(heading)
            if level <= 6:
                lines.append(f"`{value}`\n")
            else:
                lines.append(f"{indent_str}  `{value}`\n")

        elif isinstance(value, (int, float)):
            lines.append(heading)
            if level <= 6:
                lines.append(f"`{value}`\n")
            else:
                lines.append(f"{indent_str}  `{value}`\n")

        elif isinstance(value, str):
            lines.append(heading)
            # Use code block for long strings (>100 chars or multiline)
            if len(value) > 100 or "\n" in value:
                if level <= 6:
                    lines.append(f"```\n{value}\n```\n")
                else:
                    # For nested lists, indent the code block
                    lines.append(f"{indent_str}  ```\n{value}\n{indent_str}  ```\n")
            else:
                if level <= 6:
                    lines.append(f"{value}\n")
                else:
                    lines.append(f"{indent_str}  {value}\n")

        elif isinstance(value, list):
            lines.append(heading)
            # After level 6, increase indent for lists
            next_indent = indent + 1 if level > 6 else indent
            lines.append(render_array(value, level + 1, next_indent))

        elif isinstance(value, dict):
            lines.append(heading)
            # Cap level at 6, then increase indent
            if level < 6:
                lines.append(render_object(value, level + 1, key, indent))
            else:
                # At level 6+, stay at level 6 but increase indent
                lines.append(render_object(value, level + 1, key, indent + 1))

    return "\n".join(lines)


def render_to_markdown(data: Any, json_path: str) -> str:
    """
    Render JSON data to Markdown format.

    Args:
        data: The JSON data to render
        json_path: The path that was queried (for title)

    Returns:
        Markdown formatted string
    """
    lines = [f"# Spec: {json_path}\n"]

    if data is None:
        lines.append("_(not found)_\n")

    elif isinstance(data, dict):
        lines.append(render_object(data, level=2))

    elif isinstance(data, list):
        lines.append("## Items\n")
        lines.append(render_array(data, level=2))

    elif isinstance(data, str):
        if len(data) > 100 or "\n" in data:
            lines.append(f"```\n{data}\n```\n")
        else:
            lines.append(f"{data}\n")

    else:
        lines.append(f"`{data}`\n")

    return "\n".join(lines)


def main():
    """Main entry point."""
    # Get repository root (two levels up from this script)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent

    # Parse arguments with defaults
    json_file = (
        sys.argv[1] if len(sys.argv) > 1 else str(repo_root / ".jkspec" / "source.json")
    )
    json_path = sys.argv[2] if len(sys.argv) > 2 else "specs.__jkspec.components.cli"

    # Default output path based on json_path
    if len(sys.argv) > 3:
        output_md = sys.argv[3]
    else:
        sanitized = sanitize_path_for_filename(json_path)
        output_md = str(repo_root / ".tmp" / f"{sanitized}.md")

    # Validate JSON file exists
    if not os.path.exists(json_file):
        print(f"Error: JSON file not found: {json_file}", file=sys.stderr)
        sys.exit(2)

    # Read and parse JSON
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_file}: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Error reading file {json_file}: {e}", file=sys.stderr)
        sys.exit(2)

    # Resolve JSON path
    resolved_data = resolve_json_path(data, json_path)

    if resolved_data is None:
        print(f"Error: Path '{json_path}' not found in {json_file}", file=sys.stderr)
        print(f"Available top-level keys: {', '.join(data.keys())}", file=sys.stderr)
        sys.exit(4)

    # Render to Markdown
    markdown_content = render_to_markdown(resolved_data, json_path)

    # Create output directory
    output_path = Path(output_md)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(
            f"Error creating output directory {output_path.parent}: {e}",
            file=sys.stderr,
        )
        sys.exit(5)

    # Write output file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
    except Exception as e:
        print(f"Error writing output file {output_path}: {e}", file=sys.stderr)
        sys.exit(5)

    # Success
    print(f"✓ Generated Markdown: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
