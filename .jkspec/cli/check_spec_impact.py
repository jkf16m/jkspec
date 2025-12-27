#!/usr/bin/env python3
"""Check impact of changes to a spec by showing downstream and upstream dependencies.

Works across both source.json and project.json files.

Usage:
    python3 .jkspec/cli/check_spec_impact.py <spec-path>
    
Example:
    python3 .jkspec/cli/check_spec_impact.py specs.__jkspec.components.format.structure.specs.spec_schema
    python3 .jkspec/cli/check_spec_impact.py specs.my-api
"""

import json
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPO_ROOT / ".jkspec" / "source.json"
PROJECT_PATH = REPO_ROOT / ".jkspec-project" / "project.json"


def load_json(path):
    """Load and parse JSON file, return None if not found."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(3)


def resolve_path(data, path):
    """Resolve dot-notation path in nested dict."""
    parts = path.split(".")
    current = data
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    
    return current


def get_spec_meta(data, spec_path):
    """Get __meta object for a given spec path."""
    spec = resolve_path(data, spec_path)
    if spec and isinstance(spec, dict):
        return spec.get("__meta")
    return None


def find_spec_in_files(spec_path, source_data, project_data):
    """Find spec in source or project, return (data, file_name)."""
    # Try source first if it's a __ prefixed spec
    if spec_path.startswith("specs.__") and source_data:
        meta = get_spec_meta(source_data, spec_path)
        if meta:
            return source_data, "source.json"
    
    # Try project
    if project_data:
        meta = get_spec_meta(project_data, spec_path)
        if meta:
            return project_data, "project.json"
    
    # Try source if not found in project
    if source_data:
        meta = get_spec_meta(source_data, spec_path)
        if meta:
            return source_data, "source.json"
    
    return None, None


def run_validation(validates_cmd):
    """Run validation command and return exit code and output."""
    try:
        result = subprocess.run(
            validates_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO_ROOT
        )
        return result.returncode, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return 1, "Validation timed out"
    except Exception as e:
        return 1, f"Validation error: {e}"


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 check_spec_impact.py <spec-path>", file=sys.stderr)
        print("Example: python3 check_spec_impact.py specs.__jkspec.components.format.structure.specs.spec_schema", file=sys.stderr)
        print("         python3 check_spec_impact.py specs.my-api", file=sys.stderr)
        sys.exit(1)
    
    spec_path = sys.argv[1]
    
    # Load both files
    source_data = load_json(SOURCE_PATH)
    project_data = load_json(PROJECT_PATH)
    
    if not source_data and not project_data:
        print("Error: Neither source.json nor project.json found", file=sys.stderr)
        sys.exit(2)
    
    # Find the spec
    spec_data, spec_file = find_spec_in_files(spec_path, source_data, project_data)
    
    if not spec_data:
        print(f"Error: Spec not found or has no __meta: {spec_path}", file=sys.stderr)
        sys.exit(4)
    
    meta = get_spec_meta(spec_data, spec_path)
    if not meta:
        print(f"Error: Spec has no __meta: {spec_path}", file=sys.stderr)
        sys.exit(4)
    
    print(f"📋 Impact Analysis: {spec_path}")
    print(f"📁 Location: {spec_file}\n")
    
    # Show spec description
    description = meta.get("description", "No description")
    done = meta.get("done", "unknown")
    print(f"Description: {description}")
    print(f"Status: {'✓ Done' if done else '⏳ Pending'}\n")
    
    # Show downstream dependencies (implements)
    implements = meta.get("implements", [])
    if implements:
        print("⬇️  Downstream Dependencies (implements this spec):")
        print("   These specs/implementations depend on this one.")
        print("   If you change this spec, you should check/update these:\n")
        for impl in implements:
            # Try to find implementation in both files
            impl_data, impl_file = find_spec_in_files(impl, source_data, project_data)
            if impl_data:
                impl_meta = get_spec_meta(impl_data, impl)
                if impl_meta:
                    impl_desc = impl_meta.get("description", "No description")
                    impl_done = impl_meta.get("done", "?")
                    status_icon = "✓" if impl_done is True else "⏳" if impl_done is False else "?"
                    print(f"   {status_icon} {impl} [{impl_file}]")
                    print(f"      └─ {impl_desc}")
                else:
                    print(f"   ? {impl} [found but no __meta]")
            else:
                print(f"   ? {impl} [not found]")
    else:
        print("⬇️  Downstream Dependencies: None")
    
    print()
    
    # Show upstream dependencies (references)
    references = meta.get("references", [])
    if references:
        print("⬆️  Upstream Dependencies (this spec references):")
        print("   This spec depends on these specs.")
        print("   If this spec has issues, check these for requirements:\n")
        for ref in references:
            ref_data, ref_file = find_spec_in_files(ref, source_data, project_data)
            if ref_data:
                ref_meta = get_spec_meta(ref_data, ref)
                if ref_meta:
                    ref_desc = ref_meta.get("description", "No description")
                    ref_done = ref_meta.get("done", "?")
                    status_icon = "✓" if ref_done is True else "⏳" if ref_done is False else "?"
                    print(f"   {status_icon} {ref} [{ref_file}]")
                    print(f"      └─ {ref_desc}")
                else:
                    print(f"   ? {ref} [found but no __meta]")
            else:
                print(f"   ? {ref} [not found]")
    else:
        print("⬆️  Upstream Dependencies: None")
    
    print()
    
    # Run validation if present
    validates = meta.get("validates")
    if validates:
        print("🔍 Running validation check...")
        exit_code, output = run_validation(validates)
        
        if exit_code == 0:
            print(f"   ✓ {output}")
        else:
            print(f"   ✗ {output}")
            print(f"   Exit code: {exit_code}")
    else:
        print("🔍 Validation: No validation query defined")
    
    print()
    
    # Summary
    total_deps = len(implements) + len(references)
    if total_deps > 0:
        print(f"📊 Summary: {len(implements)} downstream, {len(references)} upstream ({total_deps} total dependencies)")
    else:
        print("📊 Summary: No tracked dependencies")


if __name__ == "__main__":
    main()
