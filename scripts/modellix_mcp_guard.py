#!/usr/bin/env python3
"""Cursor guard for Modellix Media Generation submits.

Asks before a repeated modellix_submit_task when this session already submitted
the same model slug via MCP or the CLI. Records only the slug, task ids, and
timestamps after the call. Fails open and never submits, polls, or downloads.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _hook_lib as lib  # noqa: E402

SUBMIT_TOOL = "modellix_submit_task"
SLUG_KEYS = ("model_slug", "modelSlug", "model", "slug")
RESULT_KEYS = ("result_json", "result", "tool_response", "tool_output", "output")


def tool_name(payload: dict[str, Any]) -> str:
    values: list[Any] = [
        payload.get("tool_name"),
        payload.get("mcp_tool_name"),
        payload.get("name"),
    ]
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        values.extend((tool_input.get("name"), tool_input.get("toolName"), tool_input.get("tool")))
    for value in values:
        text = str(value or "")
        if SUBMIT_TOOL in text:
            return SUBMIT_TOOL
    return ""


def _dicts(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for key in ("arguments", "input", "params", "body"):
            nested = value.get(key)
            if isinstance(nested, dict):
                found.append(nested)
            elif isinstance(nested, str):
                found.extend(_dicts(_parse_json(nested)))
    elif isinstance(value, str):
        found.extend(_dicts(_parse_json(value)))
    return found


def _parse_json(value: str) -> Any:
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def extract_slug(payload: dict[str, Any]) -> str:
    blobs: list[dict[str, Any]] = []
    for key in ("tool_input", "arguments", "input", "params"):
        blobs.extend(_dicts(payload.get(key)))
    for blob in blobs:
        for key in SLUG_KEYS:
            slug = blob.get(key)
            if isinstance(slug, str) and "/" in slug:
                return slug.strip()
    for blob in blobs:
        for key in SLUG_KEYS:
            slug = blob.get(key)
            if isinstance(slug, str) and slug.strip():
                return slug.strip()
    return ""


def result_text(payload: dict[str, Any]) -> str | None:
    for key in RESULT_KEYS:
        if key not in payload:
            continue
        value = payload.get(key)
        if value in (None, ""):
            continue
        return lib._as_text(value)
    return None


def fingerprint(slug: str) -> str:
    return hashlib.sha256(f"mcp|{slug}".encode("utf-8")).hexdigest()[:16]


def ask_message(record: dict[str, Any]) -> str:
    task_ids = ", ".join(record.get("task_ids") or []) or "unknown"
    return (
        "This model slug was already submitted in this session "
        f"(task: {task_ids}). Calling modellix_submit_task again charges again. "
        "Reuse modellix_get_task / modellix_wait_task, or the existing CLI task, instead."
    )


def submission_unknown(output: str) -> bool:
    parsed = _parse_json(output)
    if isinstance(parsed, dict):
        if parsed.get("submission_unknown") is True:
            return True
        data = parsed.get("data")
        if isinstance(data, dict) and data.get("submission_unknown") is True:
            return True
        return False
    return '"submission_unknown": true' in output or '"submission_unknown":true' in output


def record_submit(state: dict[str, Any], slug: str, output: str) -> None:
    fp = fingerprint(slug)
    record = state.setdefault("submits", {}).setdefault(
        fp, {"count": 0, "status": "unknown", "task_ids": [], "source": "mcp"}
    )
    task_ids = lib.extract_task_ids(output)
    record["count"] = int(record.get("count") or 0) + 1
    record["slug"] = slug
    record["source"] = "mcp"
    record["kind"] = "mcp"
    if submission_unknown(output):
        record["status"] = "unknown"
    elif task_ids and not lib.looks_failed(output):
        record["status"] = "succeeded"
    elif lib.looks_failed(output):
        record["status"] = "failed"
    else:
        record["status"] = "unknown"
    record["last_watch_at"] = time.time()
    for task_id in task_ids:
        if task_id not in record.setdefault("task_ids", []):
            record["task_ids"].append(task_id)
    if record["status"] == "succeeded":
        pending = state.setdefault("pending_tasks", {})
        for task_id in task_ids:
            pending.setdefault(
                task_id,
                {"slug": slug, "created_at": int(time.time()), "private_network_hint": False},
            )


def main() -> int:
    payload = lib.read_payload()
    if tool_name(payload) != SUBMIT_TOOL:
        return lib.emit()

    event = lib.normalize(payload)
    slug = extract_slug(payload)
    key = lib.session_key(event)
    state = lib.load_state(key)
    output = result_text(payload)

    if output is None:
        if not slug:
            lib.save_state(key, state)
            return lib.emit()
        fp = fingerprint(slug)
        prior = lib.submit_for_slug(state, slug)
        last_seen = lib.mark_event(state, f"mcp-guard:{fp}")
        since = float((prior or {}).get("last_watch_at") or 0)
        if lib.is_double_fire(last_seen, since):
            lib.save_state(key, state)
            return lib.emit()
        if prior:
            lib.save_state(key, state)
            return lib.emit(lib.ask(ask_message(prior)))
        lib.save_state(key, state)
        return lib.emit()

    if slug:
        fp = fingerprint(slug)
        last_seen = lib.mark_event(state, f"mcp-watch:{fp}")
        if not lib.is_double_fire(last_seen):
            record_submit(state, slug, output)
    lib.save_state(key, state)
    return lib.emit()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - fail open, never block the host
        raise SystemExit(lib.emit())
