#!/usr/bin/env python3
"""
Cross-platform preflight check for CLI-first routing.

Prefers `modellix-cli doctor --json` when the CLI is installed.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from typing import Any


def _run_doctor() -> tuple[bool, dict[str, Any] | None, str]:
    """Return (ok, parsed_json_or_none, raw_or_error)."""
    try:
        proc = subprocess.run(
            ["modellix-cli", "doctor", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, None, str(exc)

    raw = (proc.stdout or "").strip() or (proc.stderr or "").strip()
    parsed: dict[str, Any] | None = None
    if proc.stdout:
        try:
            parsed = json.loads(proc.stdout)
        except json.JSONDecodeError:
            parsed = None
    return proc.returncode == 0, parsed, raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Modellix CLI and API key readiness.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    notes: list[str] = []
    cli_available = shutil.which("modellix-cli") is not None
    api_key_available = bool((os.getenv("MODELLIX_API_KEY") or "").strip())
    doctor_ok: bool | None = None
    doctor_payload: dict[str, Any] | None = None

    if not cli_available:
        notes.append(
            "modellix-cli not found. Using REST fallback. "
            "Recommend: npm i -g modellix-cli@latest"
        )
    else:
        doctor_ok, doctor_payload, doctor_raw = _run_doctor()
        if doctor_payload is not None:
            notes.append("Ran modellix-cli doctor --json.")
        elif doctor_raw:
            notes.append(f"doctor output not JSON-parseable: {doctor_raw[:200]}")
        if doctor_ok:
            notes.append(
                "CLI path ready. Canonical flow: model run --wait -> task download."
            )
            # Doctor success implies usable auth even if env var is unset (saved profile).
            api_key_available = True
        else:
            notes.append(
                "doctor reported failures. Fix auth with auth login/init "
                "or set MODELLIX_API_KEY, then re-run doctor."
            )

    if not api_key_available:
        notes.append(
            "No discoverable API key (env or CLI profile). "
            "Configure MODELLIX_API_KEY or run: modellix-cli auth login"
        )

    recommended_mode = "rest"
    if cli_available and api_key_available:
        recommended_mode = "cli"
        if doctor_ok is False:
            notes.append("doctor failed; CLI may still work if the key/profile is valid.")
        notes.append(
            "Defaults when user omits model: T2I=google/nano-banana-2-lite, "
            "T2V=bytedance/seedance-2.0-mini-t2v."
        )
    elif api_key_available:
        notes.append("REST fallback is available because an API key exists.")
    else:
        notes.append("Neither CLI-auth nor REST-auth is ready. Configure API key first.")

    result = {
        "cli_available": cli_available,
        "cli_missing": not cli_available,
        "api_key_available": api_key_available,
        "doctor_ok": doctor_ok,
        "doctor": doctor_payload,
        "recommended_mode": recommended_mode,
        "notes": notes,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"cli_available      : {result['cli_available']}")
        print(f"api_key_available  : {result['api_key_available']}")
        print(f"doctor_ok          : {result['doctor_ok']}")
        print(f"recommended_mode   : {result['recommended_mode']}")
        if notes:
            print("notes:")
            for note in notes:
                print(f"- {note}")
    # Exit 0 when a usable path exists; 1 when neither CLI nor REST auth is ready.
    return 0 if api_key_available else 1


if __name__ == "__main__":
    raise SystemExit(main())
