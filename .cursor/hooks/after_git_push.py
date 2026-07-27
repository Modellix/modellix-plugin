#!/usr/bin/env python3
"""afterShellExecution hook: after a successful git push to origin/main, check community listings."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
REPO_ROOT = HOOKS_DIR.parents[1]
STATE_DIR = HOOKS_DIR / "state"
PENDING_PATH = STATE_DIR / "listings-pending.json"
SYNC_SCRIPT = HOOKS_DIR / "sync_community_listings.py"


def emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj) + "\n")


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return (proc.stdout or "").strip()


def looks_like_failed_push(output: str) -> bool:
    lower = output.lower()
    markers = (
        "error:",
        "fatal:",
        "rejected",
        "failed to push",
        "permission denied",
        "could not read from remote",
        "authentication failed",
        "non-fast-forward",
    )
    return any(m in lower for m in markers)


def is_main_push(command: str) -> bool:
    """True when this push is intended for the main line (explicit main/master or current branch is main)."""
    if re.search(r"\b(main|master)\b", command):
        return True
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    return branch in {"main", "master"}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        emit({})
        return 0

    command = str(payload.get("command") or "")
    output = str(payload.get("output") or "")

    if not re.search(r"\bgit\s+push\b", command):
        emit({})
        return 0
    if "--dry-run" in command or re.search(r"\b-n\b", command):
        emit({})
        return 0
    if looks_like_failed_push(output):
        emit({})
        return 0
    if not is_main_push(command):
        emit({})
        return 0

    tip = git("rev-parse", "HEAD")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    report_path = STATE_DIR / "listings-last-report.json"

    proc = subprocess.run(
        [sys.executable, str(SYNC_SCRIPT), "--check", "--json", "--write-state", str(report_path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    report: dict
    try:
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    except Exception:  # noqa: BLE001
        report = {"ok": False, "parse_error": True, "stderr": proc.stderr}

    pending = {
        "reason": "git_push_main",
        "command": command,
        "tip_sha": tip,
        "sync_exit": proc.returncode,
        "report_path": str(report_path.relative_to(REPO_ROOT)),
        "needs_action": bool(report.get("needs_action")),
        "errors": bool(report.get("errors")),
        "summary": {
            "ok": report.get("ok"),
            "needs_action_ids": [t.get("id") for t in report.get("needs_action") or []],
            "error_ids": [t.get("id") for t in report.get("errors") or []],
        },
    }
    PENDING_PATH.write_text(json.dumps(pending, indent=2) + "\n", encoding="utf-8")
    emit({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
