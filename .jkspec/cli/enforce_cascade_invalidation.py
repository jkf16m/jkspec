#!/usr/bin/env python3
"""Enforce cascade invalidation: mark specs done=false when their references change.

When a spec changes, all specs that implement it should be marked as done=false
to trigger re-validation. This prevents outdated implementations.

Usage:
    python3 .jkspec/cli/enforce_cascade_invalidation.py [--spec-path <path>] [--dry-run] [--validate]

Examples:
    # Check all specs and invalidate if references changed
    python3 .jkspec/cli/enforce_cascade_invalidation.py

    # Check specific spec only
    python3 .jkspec/cli/enforce_cascade_invalidation.py --spec-path specs.__jkspec.components.readme-documentation

    # Dry run to see what would be invalidated
    python3 .jkspec/cli/enforce_cascade_invalidation.py --dry-run

    # Invalidate and run validates queries
    python3 .jkspec/cli/enforce_cascade_invalidation.py --validate
"""

import json
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPO_ROOT / ".jkspec" / "source.json"
PROJECT_PATH = REPO_ROOT / ".jkspec-project" / "project.json"


def load_json(path: Path) -> Dict:
    """Load and parse JSON file, return empty dict if not found."""
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(3)


def save_json(path: Path, data: Dict) -> None:
    """Save JSON data to file with pretty formatting."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def resolve_path(data: Dict, path: str) -> Any:
    """Resolve dot-notation path in nested dict."""
    parts = path.split(".")
    current = data

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None

    return current


def set_path(data: Dict, path: str, value: Any) -> None:
    """Set value at dot-notation path in nested dict (handles arrays)."""
    parts = path.split(".")
    current = data

    for part in parts[:-1]:
        # Handle array indices
        if isinstance(current, list):
            idx = int(part)
            current = current[idx]
        else:
            if part not in current:
                current[part] = {}
            current = current[part]

    # Set final value
    final_part = parts[-1]
    if isinstance(current, list):
        current[int(final_part)] = value
    else:
        current[final_part] = value


def get_spec_meta(data: Dict, spec_path: str) -> Dict:
    """Get __meta object for a given spec path."""
    spec = resolve_path(data, spec_path)
    if spec and isinstance(spec, dict):
        return spec.get("__meta", {})
    return {}


def find_all_specs_with_meta(data: Dict, prefix: str = "") -> List[Tuple[str, Dict]]:
    """Find all paths with __meta objects."""
    results = []

    def recurse(obj, path):
        if isinstance(obj, dict):
            if "__meta" in obj:
                results.append((path, obj["__meta"]))
            for key, value in obj.items():
                if key != "__meta":
                    new_path = f"{path}.{key}" if path else key
                    recurse(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}.{i}"
                recurse(item, new_path)

    recurse(data, prefix)
    return results


def check_reference_status(data: Dict, reference: str) -> Tuple[bool, str]:
    """Check if a reference exists and its done status.

    Returns: (exists, status) where status is "done", "pending", or "not_found"
    """
    # Try to resolve with specs. prefix if not already there
    if not reference.startswith("specs."):
        reference = f"specs.{reference}"

    meta = get_spec_meta(data, reference)
    if not meta:
        return False, "not_found"

    done = meta.get("done")
    if done is True:
        return True, "done"
    elif done is False:
        return True, "pending"
    else:
        return True, "unknown"


def enforce_cascade_for_spec(
    spec_path: str,
    spec_meta: Dict,
    source_data: Dict,
    project_data: Dict,
    dry_run: bool = False,
    verbose: bool = True,
) -> Tuple[bool, List[str]]:
    """Check if spec should be invalidated based on its references.

    Returns: (should_invalidate, reasons)
    """
    references = spec_meta.get("references", [])
    if not references:
        return False, []

    reasons = []
    current_done = spec_meta.get("done")

    # Check each reference
    for ref in references:
        # Try both source and project
        exists_source, status_source = check_reference_status(source_data, ref)
        exists_project, status_project = check_reference_status(project_data, ref)

        if not exists_source and not exists_project:
            reasons.append(f"Reference not found: {ref}")
            continue

        # Use source if found there, otherwise project
        status = status_source if exists_source else status_project
        location = "source.json" if exists_source else "project.json"

        if status == "pending":
            reasons.append(f"Reference is pending: {ref} [{location}]")
        elif status == "unknown":
            reasons.append(f"Reference has unknown status: {ref} [{location}]")

    # Should invalidate if currently done but has pending/unknown references
    should_invalidate = current_done is True and len(reasons) > 0

    if verbose and reasons:
        status_icon = "⚠️" if should_invalidate else "ℹ️"
        print(f"{status_icon} {spec_path} (done={current_done})")
        for reason in reasons:
            print(f"   └─ {reason}")

    return should_invalidate, reasons


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enforce cascade invalidation for spec dependencies"
    )
    parser.add_argument(
        "--spec-path", help="Check specific spec only (default: check all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be invalidated without making changes",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validates queries after invalidation",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Only show specs that would be invalidated"
    )

    args = parser.parse_args()

    # Load both files
    source_data = load_json(SOURCE_PATH)
    project_data = load_json(PROJECT_PATH)

    if not source_data and not project_data:
        print("Error: Neither source.json nor project.json found", file=sys.stderr)
        sys.exit(2)

    print("🔍 Checking cascade invalidation...\n")

    # Find all specs to check
    if args.spec_path:
        # Check specific spec
        specs_to_check = []

        # Try to find in source
        meta = get_spec_meta(source_data, args.spec_path)
        if meta:
            specs_to_check.append(
                (args.spec_path, meta, source_data, SOURCE_PATH, "source.json")
            )

        # Try to find in project
        meta = get_spec_meta(project_data, args.spec_path)
        if meta:
            specs_to_check.append(
                (args.spec_path, meta, project_data, PROJECT_PATH, "project.json")
            )

        if not specs_to_check:
            print(f"Error: Spec not found: {args.spec_path}", file=sys.stderr)
            sys.exit(4)
    else:
        # Check all specs
        specs_to_check = []

        for path, meta in find_all_specs_with_meta(source_data):
            specs_to_check.append((path, meta, source_data, SOURCE_PATH, "source.json"))

        for path, meta in find_all_specs_with_meta(project_data):
            specs_to_check.append(
                (path, meta, project_data, PROJECT_PATH, "project.json")
            )

    # Check each spec
    invalidated = []
    checked = 0

    for spec_path, spec_meta, data, file_path, file_name in specs_to_check:
        should_invalidate, reasons = enforce_cascade_for_spec(
            spec_path,
            spec_meta,
            source_data,
            project_data,
            dry_run=args.dry_run,
            verbose=not args.quiet,
        )

        checked += 1

        if should_invalidate:
            invalidated.append((spec_path, file_name, reasons))

            if not args.dry_run:
                # Actually invalidate
                set_path(data, f"{spec_path}.__meta.done", False)

    # Save changes
    if invalidated and not args.dry_run:
        print(f"\n📝 Invalidating {len(invalidated)} specs...\n")

        # Determine which files to save
        files_to_save = set(file_name for _, file_name, _ in invalidated)

        if "source.json" in files_to_save:
            save_json(SOURCE_PATH, source_data)
            print(f"✓ Updated {SOURCE_PATH}")

        if "project.json" in files_to_save:
            save_json(PROJECT_PATH, project_data)
            print(f"✓ Updated {PROJECT_PATH}")

        # Validate files
        for file_name in files_to_save:
            file_path = SOURCE_PATH if file_name == "source.json" else PROJECT_PATH
            print(f"\n🔍 Validating {file_path}...")
            result = subprocess.run(
                [
                    "ajv",
                    "validate",
                    "-s",
                    str(REPO_ROOT / ".jkspec" / "jkspec.schema.json"),
                    "-d",
                    str(file_path),
                    "--spec=draft2020",
                    "--strict=false",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"✓ {file_name} valid")
            else:
                print(f"✗ {file_name} validation failed:", file=sys.stderr)
                print(result.stderr, file=sys.stderr)

    # Summary
    print(f"\n📊 Summary:")
    print(f"   Checked: {checked} specs")
    print(f"   Invalidated: {len(invalidated)} specs")

    if invalidated:
        print(f"\n{'Would invalidate' if args.dry_run else 'Invalidated'}:")
        for spec_path, file_name, reasons in invalidated:
            print(f"   ⚠️ {spec_path} [{file_name}]")
            for reason in reasons:
                print(f"      └─ {reason}")

    if args.dry_run and invalidated:
        print(f"\n💡 Run without --dry-run to apply changes")

    # Run validates if requested
    if args.validate and invalidated and not args.dry_run:
        print(f"\n🔍 Running validates queries...")
        # TODO: Implement validates query execution
        print("   (Not yet implemented)")


if __name__ == "__main__":
    main()
