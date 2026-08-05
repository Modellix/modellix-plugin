#!/usr/bin/env python3
"""Shared helpers for Modellix plugin hooks.

Normalizes Cursor and Claude Code hook payloads, keeps a small per-session state
file (fingerprints only, never prompts or credentials), and renders host-specific
hook responses. Every helper is fail-open: callers should emit an empty object and
exit 0 when anything is unexpected.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

STATE_VERSION = 2
STATE_TTL_SECONDS = 24 * 60 * 60
DEDUPE_WINDOW_SECONDS = 5

CLI_RE = re.compile(r"\bmodellix-cli\b")
PAID_SUBMIT_RE = re.compile(r"\bmodellix-cli\b[^|;&]*?\bmodel\s+(run|invoke|batch)\b")
DOWNLOAD_RE = re.compile(r"\bmodellix-cli\b[^|;&]*?\btask\s+download\b")
SECRET_FLAG_RE = re.compile(r"(--api-key[=\s]+)(\S+)")
SECRET_ENV_RE = re.compile(r"(MODELLIX_API_KEY=)(\S+)")
TASK_ID_RE = re.compile(
    r"[\"']?task[_-]?id[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9][\w.-]{5,})",
    re.IGNORECASE,
)
PRIVATE_NETWORK_RE = re.compile(r"private or reserved network", re.IGNORECASE)
SUCCESS_STATUS_RE = re.compile(r"[\"']?status[\"']?\s*[:=]\s*[\"']?(succeeded|completed|success)", re.I)

FAILURE_MARKERS = (
    "failed",
    "timed out",
    "timeout",
    "econnreset",
    "etimedout",
    "traceback",
)


def read_payload() -> dict[str, Any]:
    """Parse the hook event JSON from stdin. Returns {} when unreadable."""
    try:
        raw = sys.stdin.read()
    except Exception:  # noqa: BLE001 - hooks must never crash the host
        return {}
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def emit(obj: dict[str, Any] | None = None) -> int:
    """Write a hook response and return the process exit code."""
    sys.stdout.write(json.dumps(obj or {}, ensure_ascii=False) + "\n")
    return 0


def is_cursor_host() -> bool:
    # CLAUDE_PROJECT_DIR is also exported by Cursor, so check Cursor markers first.
    return any(os.getenv(name) for name in ("CURSOR_PLUGIN_ROOT", "CURSOR_VERSION", "CURSOR_PROJECT_DIR"))


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        parts = [
            str(value.get(key) or "")
            for key in ("stdout", "stderr", "output", "content", "result", "error")
        ]
        text = "\n".join(part for part in parts if part)
        return text or json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "\n".join(_as_text(item) for item in value)
    return str(value)


def normalize(payload: dict[str, Any]) -> dict[str, Any]:
    """Flatten Cursor and Claude Code shapes into one event view."""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}

    command = payload.get("command") or tool_input.get("command") or ""
    output = payload.get("output")
    if output is None:
        output = payload.get("tool_response")
    if output is None:
        output = payload.get("tool_output")

    session_id = (
        payload.get("session_id")
        or payload.get("conversation_id")
        or payload.get("composer_id")
        or ""
    )

    return {
        "command": command if isinstance(command, str) else "",
        "output": _as_text(output),
        "exit_code": _exit_code(payload, output),
        "session_id": str(session_id),
        "tool_name": str(payload.get("tool_name") or ""),
        "cwd": str(payload.get("cwd") or os.getenv("CURSOR_PROJECT_DIR") or os.getcwd()),
    }


def _exit_code(payload: dict[str, Any], output: Any) -> int | None:
    """Read a shell exit code from common Cursor and Claude payload shapes."""
    values = [payload.get("exit_code"), payload.get("exitCode")]
    if isinstance(output, dict):
        values.extend((output.get("exit_code"), output.get("exitCode")))
    for value in values:
        if isinstance(value, bool):
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def redact(command: str) -> str:
    """Strip credential values before anything is stored or shown."""
    redacted = SECRET_FLAG_RE.sub(r"\1<redacted>", command)
    return SECRET_ENV_RE.sub(r"\1<redacted>", redacted)


def is_modellix_command(command: str) -> bool:
    return bool(CLI_RE.search(command))


def is_paid_submit(command: str) -> bool:
    return bool(PAID_SUBMIT_RE.search(command))


def is_download(command: str) -> bool:
    return bool(DOWNLOAD_RE.search(command))


def _tokens(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def flag_value(command: str, *names: str) -> str | None:
    tokens = _tokens(command)
    for index, token in enumerate(tokens):
        for name in names:
            if token == name and index + 1 < len(tokens):
                return tokens[index + 1]
            if token.startswith(f"{name}="):
                return token.split("=", 1)[1]
    return None


def has_flag(command: str, *names: str) -> bool:
    tokens = _tokens(command)
    return any(token == name or token.startswith(f"{name}=") for token in tokens for name in names)


def positional_after(command: str, keyword: str) -> str | None:
    """First non-flag token following `keyword` (e.g. the task id in `task download <id>`)."""
    tokens = _tokens(command)
    if keyword not in tokens:
        return None
    rest = tokens[tokens.index(keyword) + 1 :]
    skip_next = False
    for token in rest:
        if skip_next:
            skip_next = False
            continue
        if token.startswith("-"):
            skip_next = "=" not in token
            continue
        return token
    return None


def submit_kind(command: str) -> str:
    match = PAID_SUBMIT_RE.search(command)
    return match.group(1) if match else ""


def fingerprint(command: str) -> str:
    """Stable id for a paid submission: subcommand + slug + body, or the redacted command."""
    kind = submit_kind(command)
    slug = flag_value(command, "--model-slug", "--model", "-m") or ""
    body = flag_value(command, "--body", "-b") or ""
    if kind and (slug or body):
        material = f"{kind}|{slug}|{body}"
    else:
        material = redact(" ".join(_tokens(command)))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def model_slug(command: str) -> str:
    return flag_value(command, "--model-slug", "--model", "-m") or ""


def session_key(event: dict[str, Any]) -> str:
    raw = event.get("session_id") or f"cwd:{event.get('cwd') or ''}"
    return hashlib.sha256(str(raw).encode("utf-8")).hexdigest()[:16]


def state_path(key: str) -> Path:
    return Path(tempfile.gettempdir()) / "modellix-hooks" / f"{key}.json"


def _empty_state() -> dict[str, Any]:
    return {
        "version": STATE_VERSION,
        "updated_at": int(time.time()),
        "submits": {},
        "pending_tasks": {},
        "notices": {},
        "recent_events": {},
    }


def _cleanup_stale_files(directory: Path) -> None:
    """Best-effort removal of expired state without exposing its contents."""
    cutoff = time.time() - STATE_TTL_SECONDS
    try:
        candidates = directory.glob("*.json")
        for candidate in candidates:
            try:
                if candidate.stat().st_mtime < cutoff:
                    candidate.unlink(missing_ok=True)
            except OSError:
                continue
    except OSError:
        pass


def load_state(key: str) -> dict[str, Any]:
    path = state_path(key)
    _cleanup_stale_files(path.parent)
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _empty_state()
    except Exception:  # noqa: BLE001 - corrupt state degrades to allow-all
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return _empty_state()
    if not isinstance(state, dict) or state.get("version") != STATE_VERSION:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return _empty_state()
    if int(time.time()) - int(state.get("updated_at") or 0) > STATE_TTL_SECONDS:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return _empty_state()
    for field in ("submits", "pending_tasks", "notices", "recent_events"):
        if not isinstance(state.get(field), dict):
            state[field] = {}
    return state


def save_state(key: str, state: dict[str, Any]) -> None:
    path = state_path(key)
    state["version"] = STATE_VERSION
    state["updated_at"] = int(time.time())
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(path.parent, 0o700)
        _cleanup_stale_files(path.parent)
    except Exception:  # noqa: BLE001
        return
    try:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
        os.chmod(tmp, 0o600)
        tmp.replace(path)
    except Exception:  # noqa: BLE001
        return


def mark_event(state: dict[str, Any], event_id: str) -> float | None:
    """Record an event timestamp and return when the same event was last seen."""
    now = time.time()
    recent = state.get("recent_events") or {}
    last = recent.get(event_id)
    for key, seen_at in list(recent.items()):
        if now - float(seen_at) > STATE_TTL_SECONDS:
            recent.pop(key, None)
    recent[event_id] = now
    state["recent_events"] = recent
    return float(last) if last is not None else None


def is_double_fire(last_seen: float | None, since: float = 0.0) -> bool:
    """True when the same event repeats within the dedupe window and nothing ran in between.

    Protects against a host that loads both hook configs without hiding a genuine
    re-submission, which always has a completed command (`since`) after the last event.
    """
    if last_seen is None:
        return False
    if since and since > last_seen:
        return False
    return time.time() - last_seen < DEDUPE_WINDOW_SECONDS


def looks_succeeded(output: str) -> bool:
    return bool(SUCCESS_STATUS_RE.search(output))


def looks_failed(output: str, exit_code: int | None = None) -> bool:
    """Heuristic failure check; an explicit success status always wins.

    CLI JSON often carries fields like `"error": null`, so the success status is
    checked first to avoid marking a completed task as failed.
    """
    if exit_code is not None:
        return exit_code != 0
    if looks_succeeded(output):
        return False
    try:
        payload = json.loads(output)
    except (json.JSONDecodeError, TypeError, ValueError):
        payload = None
    if isinstance(payload, dict):
        if payload.get("ok") is False:
            return True
        error = payload.get("error")
        if error not in (None, "", False, {}, []):
            return True
        code = payload.get("code")
        try:
            if code is not None and int(code) != 0:
                return True
            if code is not None and int(code) == 0:
                return False
        except (TypeError, ValueError):
            pass
        if payload.get("ok") is True or ("error" in payload and error in (None, "", False, {}, [])):
            return False
    lowered = output.lower()
    if any(marker in lowered for marker in FAILURE_MARKERS):
        return True
    return bool(re.search(r"(?:^|\n)\s*(?:error|fatal):", output, re.IGNORECASE))


def extract_task_ids(output: str) -> list[str]:
    ids: list[str] = []
    for match in TASK_ID_RE.finditer(output):
        value = match.group(1)
        if value and value not in ids:
            ids.append(value)
    return ids


def ask(message: str, event_name: str = "PreToolUse") -> dict[str, Any]:
    """Request user confirmation before the command runs."""
    if is_cursor_host():
        return {"permission": "ask", "user_message": message, "agent_message": message}
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "permissionDecision": "ask",
            "permissionDecisionReason": message,
        }
    }


def advise(message: str) -> dict[str, Any]:
    """Surface a note without deciding.

    Claude Code treats `permissionDecision: "allow"` as a permission-system bypass,
    so advisory text goes through `systemMessage` there.
    """
    if is_cursor_host():
        return {"agent_message": message}
    return {"systemMessage": message}


def followup(message: str) -> dict[str, Any]:
    """Render a stop-hook follow-up for the current host."""
    if is_cursor_host():
        return {"followup_message": message}
    return {"decision": "block", "reason": message}
