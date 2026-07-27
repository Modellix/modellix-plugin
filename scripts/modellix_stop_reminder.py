#!/usr/bin/env python3
"""Stop hook: remind the agent to persist Modellix results before finishing.

Fires at most once per session; pending tasks are cleared as soon as the reminder
is sent so the agent never loops on it.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _hook_lib as lib  # noqa: E402

MAX_LISTED_TASKS = 5


def main() -> int:
    payload = lib.read_payload()
    event = lib.normalize(payload)
    key = lib.session_key(event)
    state = lib.load_state(key)

    pending = state.get("pending_tasks") or {}
    if not pending:
        return lib.emit()

    notices = state.setdefault("notices", {})
    if notices.get("download_reminded"):
        return lib.emit()

    task_ids = list(pending)[:MAX_LISTED_TASKS]
    extra = len(pending) - len(task_ids)
    listed = ", ".join(task_ids) + (f" (+{extra} more)" if extra > 0 else "")
    private_network = any(record.get("private_network_hint") for record in pending.values())

    lines = [
        f"Modellix tasks in this session have no confirmed local copy yet: {listed}.",
        "Resource URLs expire in about 7 days, so download before finishing:",
        f"  modellix-cli task download {task_ids[0]} --output-dir ./outputs --json",
    ]
    if private_network:
        lines.append(
            "A previous download failed on a private/reserved network address. "
            "Retry with `--allow-private-network` for trusted Modellix CDN hosts, "
            "or fetch `result.resources[].url` with curl."
        )
    lines.append("If the user already has the files, say so and stop.")

    notices["download_reminded"] = True
    state["pending_tasks"] = {}
    lib.save_state(key, state)
    return lib.emit(lib.followup("\n".join(lines)))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - fail open, never trap the agent in a stop loop
        raise SystemExit(lib.emit())
