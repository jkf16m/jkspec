#!/usr/bin/env python3
"""Project initialization helper for jkspec.

This utility sets up a virtual environment and installs requirements so the
agent has a predictable runtime regardless of platform.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_command(cmd: list[str], *, cwd: Optional[Path] = None) -> None:
    """Run a subprocess command with logging."""
    display = " ".join(str(part) for part in cmd)
    print(f"[initialize] $ {display}")
    subprocess.run(cmd, cwd=cwd, check=True)


def resolve_repo_root() -> Path:
    """Return repository root (two levels up from this file)."""
    return Path(__file__).resolve().parents[2]


def resolve_cli_dir() -> Path:
    """Return the directory containing this CLI script."""
    return Path(__file__).resolve().parent


def resolve_path(raw: str, base: Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else (base / path)


def get_venv_binaries(venv_path: Path) -> tuple[Path, Path]:
    if os.name == "nt":
        bin_dir = venv_path / "Scripts"
        python_bin = bin_dir / "python.exe"
        pip_bin = bin_dir / "pip.exe"
    else:
        bin_dir = venv_path / "bin"
        python_bin = bin_dir / "python"
        pip_bin = bin_dir / "pip"
    return python_bin, pip_bin


def ensure_venv(python_exe: str, venv_path: Path, recreate: bool) -> None:
    if recreate and venv_path.exists():
        print(f"[initialize] Removing existing virtual environment at {venv_path}")
        shutil.rmtree(venv_path)

    if venv_path.exists():
        print(f"[initialize] Using existing virtual environment at {venv_path}")
        return

    print(f"[initialize] Creating virtual environment at {venv_path}")
    run_command([python_exe, "-m", "venv", str(venv_path)])


def upgrade_pip(python_bin: Path) -> None:
    run_command([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"])


def install_requirements(pip_bin: Path, requirements: Path) -> None:
    run_command([str(pip_bin), "install", "-r", str(requirements)])


def parse_args(root: Path, cli_dir: Path) -> argparse.Namespace:
    default_venv = cli_dir / ".venv"
    default_req = root / "requirements.txt"

    parser = argparse.ArgumentParser(
        description="Initialize the jkspec project environment by creating a virtual environment and installing dependencies."
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python interpreter to use for creating the virtual environment (defaults to the current interpreter).",
    )
    parser.add_argument(
        "--venv",
        default=str(default_venv),
        help="Path to the virtual environment directory (relative paths are resolved from the CLI directory).",
    )
    parser.add_argument(
        "--requirements",
        default=str(default_req) if default_req.exists() else None,
        help="Requirements file to install after provisioning the virtual environment (optional).",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip dependency installation even if a requirements file is provided.",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and recreate the virtual environment if it already exists.",
    )
    return parser.parse_args()


def main() -> None:
    root = resolve_repo_root()
    cli_dir = resolve_cli_dir()
    print(f"[initialize] Repository root: {root}")
    print(f"[initialize] CLI directory: {cli_dir}")

    args = parse_args(root, cli_dir)
    venv_path = resolve_path(args.venv, cli_dir)
    requirements = Path(args.requirements) if args.requirements else None

    ensure_venv(args.python, venv_path, recreate=args.recreate)

    python_bin, pip_bin = get_venv_binaries(venv_path)
    if not python_bin.exists():
        raise FileNotFoundError(
            f"Expected interpreter inside venv not found: {python_bin}"
        )

    upgrade_pip(python_bin)

    if not args.skip_install and requirements:
        requirements = (
            requirements if requirements.is_absolute() else root / requirements
        )
        if requirements.exists():
            print(f"[initialize] Installing dependencies from {requirements}")
            install_requirements(pip_bin, requirements)
        else:
            print(
                f"[initialize] Requirements file not found at {requirements}; skipping installation."
            )
    else:
        print(
            "[initialize] Dependency installation skipped by flag or missing requirements file."
        )

    activation_hint = (
        f"source {venv_path / 'bin' / 'activate'}"
        if os.name != "nt"
        else f"{venv_path}\\Scripts\\activate"
    )
    print("[initialize] Done. Activate the environment with:")
    print(f"  {activation_hint}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"[initialize] Command failed with exit code {exc.returncode}")
        sys.exit(exc.returncode)
