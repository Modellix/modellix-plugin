#!/usr/bin/env python3
"""Report whether this interpreter can import moviepy 2.x and Pillow.

This script only checks the current interpreter. It prints an install command
and stops. It does not run that command or change the environment.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import re
import sys

INSTALL_COMMAND = 'python3 -m pip install "moviepy>=2,<3" Pillow'


def report() -> dict:
    """Build the JSON report. Import failures are recorded; nothing is installed."""
    moviepy_version = _distribution_version("moviepy")
    moviepy_imported = _importable("moviepy")
    pillow_imported = _importable("PIL")
    major = _major(moviepy_version)
    missing: list[str] = []
    if not moviepy_imported or major != 2:
        missing.append("moviepy")
    if not pillow_imported:
        missing.append("PIL")
    ok = not missing
    return {
        "ok": ok,
        "missing": missing,
        "moviepy_version": moviepy_version,
        "install_command": INSTALL_COMMAND,
        "action": "continue" if ok else "stop",
        "message": _message(ok, moviepy_version, major, missing),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check moviepy 2.x and Pillow. Does not install them."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the report as JSON.",
    )
    args = parser.parse_args(argv)
    if not args.json:
        parser.error("--json is required")
    payload = report()
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if payload["ok"] else 1


def _distribution_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _importable(name: str) -> bool:
    try:
        importlib.import_module(name)
    except Exception:
        return False
    return True


def _major(version: str | None) -> int | None:
    if not version:
        return None
    match = re.match(r"(\d+)", version)
    if match is None:
        return None
    return int(match.group(1))


def _message(ok: bool, version: str | None, major: int | None, missing: list[str]) -> str:
    wait = "Show install_command to the user and wait for confirmation before running it."
    if ok:
        return "moviepy 2.x and Pillow are available."
    if version and major != 2 and "moviepy" in missing:
        lead = f"moviepy {version} is installed, but this skill needs moviepy 2.x."
    else:
        lead = "moviepy 2.x or Pillow is not available for this interpreter."
    return f"{lead} {wait}"


if __name__ == "__main__":
    sys.exit(main())
