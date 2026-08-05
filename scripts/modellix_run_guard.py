#!/usr/bin/env python3
"""Pre-execution guard for paid Modellix submissions.

Asks for confirmation before a repeated `model run` / `model invoke` or an
unbounded `model batch`, and reminds the agent to run `doctor` when no credential
is discoverable. Never blocks non-Modellix commands and always fails open.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _hook_lib as lib  # noqa: E402

HISTORY_HINT = "Check `modellix-cli task history` (or the console) before spending again."


def build_message(state: dict, fp: str) -> str | None:
    record = (state.get("submits") or {}).get(fp)
    if not record:
        return None
    count = int(record.get("count") or 0)
    status = str(record.get("status") or "unknown")
    if count < 1:
        return None
    if status == "succeeded":
        task_ids = ", ".join(record.get("task_ids") or []) or "unknown"
        return (
            f"This paid submission already succeeded in this session (task: {task_ids}). "
            f"Re-running charges again. Reuse the existing task or `task download` instead. {HISTORY_HINT}"
        )
    return (
        "An identical paid submission was already sent in this session and its outcome is "
        f"{status}. Do not blind-retry paid submits. {HISTORY_HINT}"
    )


def credentials_missing(command: str) -> bool:
    if (os.getenv("MODELLIX_API_KEY") or "").strip():
        return False
    if os.getenv("MODELLIX_PROFILE"):
        return False
    return not lib.has_flag(command, "--api-key", "--profile")


def main() -> int:
    payload = lib.read_payload()
    event = lib.normalize(payload)
    command = event["command"]

    tool_name = event["tool_name"]
    if tool_name and tool_name not in {"Bash", "Shell"}:
        return lib.emit()
    if not lib.is_modellix_command(command):
        return lib.emit()

    key = lib.session_key(event)
    state = lib.load_state(key)
    fp = lib.fingerprint(command)

    known = (state.get("submits") or {}).get(fp) or {}
    last_seen = lib.mark_event(state, f"guard:{fp}")
    if lib.is_double_fire(last_seen, float(known.get("last_watch_at") or 0)):
        lib.save_state(key, state)
        return lib.emit()

    if not lib.is_paid_submit(command):
        lib.save_state(key, state)
        return lib.emit()

    reason = build_message(state, fp)
    if not reason and lib.submit_kind(command) == "batch" and not lib.has_flag(command, "--max-tasks"):
        reason = (
            "`model batch` without `--max-tasks` has no cost ceiling. "
            "Set `--max-tasks N` to bound the spend before submitting."
        )

    if reason:
        lib.save_state(key, state)
        return lib.emit(lib.ask(reason))

    notices = state.setdefault("notices", {})
    if credentials_missing(command) and not notices.get("credentials_hinted"):
        notices["credentials_hinted"] = True
        lib.save_state(key, state)
        return lib.emit(
            lib.advise(
                "No MODELLIX_API_KEY, MODELLIX_PROFILE, or --api-key/--profile in this command. "
                "Unless a saved CLI profile covers it, run `modellix-cli doctor --json` "
                "so a paid submit does not fail on auth."
            )
        )

    lib.save_state(key, state)
    return lib.emit()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - fail open, never block the host
        raise SystemExit(lib.emit())
