#!/usr/bin/env python3
"""Post-execution watcher for Modellix CLI commands.

Records task ids produced by paid submissions so the stop hook can remind the
agent to download before the 7-day expiry, and clears them once `task download`
succeeds. Observational only: it never changes the agent's decision.
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _hook_lib as lib  # noqa: E402


def main() -> int:
    payload = lib.read_payload()
    event = lib.normalize(payload)
    command = event["command"]
    output = event["output"]

    tool_name = event["tool_name"]
    if tool_name and tool_name not in {"Bash", "Shell"}:
        return lib.emit()
    if not lib.is_modellix_command(command):
        return lib.emit()

    key = lib.session_key(event)
    state = lib.load_state(key)
    task_ids = lib.extract_task_ids(output)

    last_seen = lib.mark_event(state, f"watch:{lib.fingerprint(command)}:{','.join(task_ids)}")
    if lib.is_double_fire(last_seen):
        lib.save_state(key, state)
        return lib.emit()

    failed = lib.looks_failed(output, event["exit_code"])
    pending = state.setdefault("pending_tasks", {})

    if lib.is_download(command):
        explicit = lib.positional_after(command, "download") or lib.flag_value(command, "--task-id")
        targets = [t for t in ([explicit] if explicit else []) + task_ids if t] or list(pending)
        for task_id in targets:
            record = pending.get(task_id)
            if not record:
                continue
            if failed:
                record["private_network_hint"] = bool(lib.PRIVATE_NETWORK_RE.search(output))
            else:
                pending.pop(task_id, None)
        lib.save_state(key, state)
        return lib.emit()

    if lib.is_paid_submit(command):
        fp = lib.fingerprint(command)
        record = state.setdefault("submits", {}).setdefault(
            fp, {"count": 0, "status": "unknown", "task_ids": []}
        )
        record["count"] = int(record.get("count") or 0) + 1
        record["slug"] = lib.model_slug(command)
        record["kind"] = lib.submit_kind(command)
        record["status"] = "failed" if failed else ("succeeded" if task_ids else "unknown")
        record["last_watch_at"] = time.time()
        for task_id in task_ids:
            if task_id not in record.setdefault("task_ids", []):
                record["task_ids"].append(task_id)

        if not failed:
            slug = lib.model_slug(command)
            for task_id in task_ids:
                pending.setdefault(
                    task_id,
                    {
                        "slug": slug,
                        "created_at": int(time.time()),
                        "private_network_hint": False,
                    },
                )

    lib.save_state(key, state)
    return lib.emit()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - fail open, never disturb the host
        raise SystemExit(lib.emit())
