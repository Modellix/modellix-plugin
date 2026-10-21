#!/usr/bin/env python3
"""Report whether ffmpeg and ffprobe can encode a normal delivery file.

This script only checks the current machine. It prints an install command and
stops. It does not run that command, download a binary, or change the system.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Mapping

DEBIAN_IDS = {"debian", "ubuntu"}
FEDORA_IDS = {"fedora", "rhel", "centos", "rocky", "almalinux"}
DEBIAN_INSTALL = "sudo apt-get update && sudo apt-get install -y ffmpeg"
FEDORA_INSTALL = "sudo dnf install -y ffmpeg"
REQUIRED_ENCODERS = ("libx264", "aac")
PROBE_TIMEOUT_SECONDS = 15


def install_command(platform_name: str, os_release: str = "") -> str:
    """Return one package-manager command for this platform, or an empty string."""
    if platform_name == "Darwin":
        return "brew install ffmpeg"
    if platform_name == "Windows":
        return "winget install --id Gyan.FFmpeg -e"
    if platform_name != "Linux":
        return ""
    primary, like = _release_ids(os_release)
    for tokens in (primary, like):
        if tokens & FEDORA_IDS:
            return FEDORA_INSTALL
        if tokens & DEBIAN_IDS:
            return DEBIAN_INSTALL
    return ""


def report(
    env: Mapping[str, str] | None = None,
    platform_name: str | None = None,
    os_release: str | None = None,
) -> dict:
    """Build the JSON report. `env` supplies PATH and is not forwarded to a shell."""
    environment = dict(env) if env is not None else None
    search_path = None if environment is None else environment.get("PATH", "")
    platform = platform_name or sys.platform
    resolved_platform = _platform_name(platform)
    if os_release is None and resolved_platform == "Linux":
        os_release = _read_os_release()
    command = install_command(resolved_platform, os_release or "")

    ffmpeg_path = shutil.which("ffmpeg", path=search_path)
    ffprobe_path = shutil.which("ffprobe", path=search_path)
    missing: list[str] = []
    versions = {"ffmpeg": None, "ffprobe": None}
    encoders = {name: False for name in REQUIRED_ENCODERS}

    if ffmpeg_path is None:
        missing.append("ffmpeg")
    else:
        version_text = _capture([ffmpeg_path, "-version"], environment)
        versions["ffmpeg"] = _version(version_text)
        if versions["ffmpeg"] is None:
            missing.append("ffmpeg")
        encoder_text = _capture([ffmpeg_path, "-hide_banner", "-encoders"], environment)
        for name in REQUIRED_ENCODERS:
            encoders[name] = _has_encoder(encoder_text, name)
            if not encoders[name]:
                missing.append(name)

    if ffprobe_path is None:
        missing.append("ffprobe")
    else:
        probe_text = _capture([ffprobe_path, "-version"], environment)
        versions["ffprobe"] = _version(probe_text)
        if versions["ffprobe"] is None:
            missing.append("ffprobe")

    ok = not missing
    incomplete = bool({"libx264", "aac"} & set(missing))
    return {
        "ok": ok,
        "ffmpeg_path": ffmpeg_path,
        "ffprobe_path": ffprobe_path,
        "ffmpeg_version": versions["ffmpeg"],
        "ffprobe_version": versions["ffprobe"],
        "encoders": encoders,
        "missing": missing,
        "install_command": command,
        "action": "continue" if ok else "stop",
        "message": _message(ok, incomplete, command),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check ffmpeg and ffprobe. Does not install them."
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


def _platform_name(platform: str) -> str:
    if platform == "darwin" or platform == "Darwin":
        return "Darwin"
    if platform == "win32" or platform == "Windows":
        return "Windows"
    if platform == "linux" or platform == "Linux":
        return "Linux"
    return platform


def _release_ids(text: str) -> tuple[set[str], set[str]]:
    primary: set[str] = set()
    like: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("ID="):
            primary = _split_release(line.split("=", 1)[1])
        elif line.startswith("ID_LIKE="):
            like = _split_release(line.split("=", 1)[1])
    return primary, like


def _split_release(value: str) -> set[str]:
    cleaned = value.strip().strip('"').strip("'")
    return {part for part in cleaned.replace(",", " ").split() if part}


def _read_os_release() -> str:
    try:
        return Path("/etc/os-release").read_text(encoding="utf-8")
    except OSError:
        return ""


def _capture(command: list[str], env: dict[str, str] | None) -> str:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT_SECONDS,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return f"{completed.stdout or ''}{completed.stderr or ''}"


def _version(text: str) -> str | None:
    match = re.search(r"\bversion\s+(\S+)", text)
    if match is None:
        return None
    return match.group(1)


def _has_encoder(text: str, name: str) -> bool:
    return re.search(rf"(?m)^.*?\s+{re.escape(name)}(?:\s|$)", text) is not None


def _message(ok: bool, incomplete: bool, command: str) -> str:
    if ok:
        return "ffmpeg and ffprobe are available with libx264 and aac."
    wait = "Show install_command to the user and wait for confirmation before running it."
    refuse = "Do not download a binary or pipe a script into a shell."
    if incomplete:
        lead = "FFmpeg is installed, but this build is incomplete."
    elif command:
        lead = "FFmpeg is not available."
    else:
        lead = "FFmpeg is not available. Ask the user which package manager installs ffmpeg with libx264 and aac."
    return f"{lead} {wait} {refuse}"


if __name__ == "__main__":
    sys.exit(main())
