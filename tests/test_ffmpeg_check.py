from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "modellix-ffmpeg" / "scripts" / "check_ffmpeg.py"
SPEC = importlib.util.spec_from_file_location("modellix_ffmpeg_check_test", MODULE_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class CheckFfmpegTests(unittest.TestCase):
    def test_install_commands_match_the_platform(self):
        self.assertEqual(CHECK.install_command("Darwin"), "brew install ffmpeg")
        self.assertEqual(
            CHECK.install_command("Windows"),
            "winget install --id Gyan.FFmpeg -e",
        )
        debian = 'ID=ubuntu\nID_LIKE="debian"\n'
        fedora = "ID=fedora\nID_LIKE=rhel\n"
        self.assertEqual(
            CHECK.install_command("Linux", debian),
            "sudo apt-get update && sudo apt-get install -y ffmpeg",
        )
        self.assertEqual(
            CHECK.install_command("Linux", fedora),
            "sudo dnf install -y ffmpeg",
        )
        self.assertEqual(CHECK.install_command("Linux", "ID=arch\n"), "")
        self.assertNotIn("curl", CHECK.install_command("Darwin"))

    def test_encoder_name_does_not_match_a_longer_codec(self):
        text = " V..... libx264rgb           libx264rgb\n A..... libfdk_aac           Fraunhofer AAC\n"
        self.assertFalse(CHECK._has_encoder(text, "libx264"))
        self.assertFalse(CHECK._has_encoder(text, "aac"))
        text = " V..... libx264              H.264\n A..... aac                  AAC\n"
        self.assertTrue(CHECK._has_encoder(text, "libx264"))
        self.assertTrue(CHECK._has_encoder(text, "aac"))

    def test_missing_binaries_do_not_spawn_or_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(CHECK.subprocess, "run", side_effect=AssertionError("spawn")):
                payload = CHECK.report(
                    env={"PATH": temporary},
                    platform_name="Darwin",
                    os_release="",
                )
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["action"], "stop")
        self.assertEqual(payload["install_command"], "brew install ffmpeg")
        self.assertIn("ffmpeg", payload["missing"])
        self.assertIn("ffprobe", payload["missing"])
        self.assertIn("wait for confirmation", payload["message"])
        self.assertIn("Do not download a binary", payload["message"])

    def test_incomplete_build_stops_with_the_install_command(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            _write_fake(directory, "ffmpeg", encoders=" A..... aac                  AAC\n")
            _write_fake(directory, "ffprobe", encoders="")
            payload = CHECK.report(env={"PATH": temporary}, platform_name="Darwin")
        self.assertFalse(payload["ok"])
        self.assertIn("libx264", payload["missing"])
        self.assertNotIn("aac", payload["missing"])
        self.assertIn("incomplete", payload["message"])
        self.assertEqual(payload["install_command"], "brew install ffmpeg")

    def test_cli_accepts_a_fake_path_and_a_missing_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            missing = _run_cli(directory)
            self.assertEqual(missing.returncode, 1)
            missing_payload = json.loads(missing.stdout)
            self.assertFalse(missing_payload["ok"])
            self.assertIn("install_command", missing_payload)
            self.assertNotIn("curl", missing_payload["install_command"])

            _write_fake(directory, "ffmpeg", encoders=" V..... libx264              H.264\n A..... aac                  AAC\n")
            _write_fake(directory, "ffprobe", encoders="")
            ready = _run_cli(directory)
            self.assertEqual(ready.returncode, 0, ready.stderr)
            ready_payload = json.loads(ready.stdout)
            self.assertTrue(ready_payload["ok"])
            self.assertEqual(ready_payload["action"], "continue")
            self.assertEqual(ready_payload["missing"], [])
            self.assertEqual(ready_payload["ffmpeg_version"], "7.0.2")
            self.assertEqual(ready_payload["ffprobe_version"], "7.0.2")


def _run_cli(directory: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = str(directory)
    return subprocess.run(
        [sys.executable, str(MODULE_PATH), "--json"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=20,
    )


def _write_fake(directory: Path, name: str, encoders: str) -> None:
    if os.name == "nt":
        path = directory / f"{name}.cmd"
        path.write_text(
            "\r\n".join(
                [
                    "@echo off",
                    "echo %* | findstr /C:\"encoders\" >nul",
                    "if %errorlevel%==0 (",
                    f"  echo {encoders.strip()}",
                    ") else (",
                    f"  echo {name} version 7.0.2 Copyright",
                    ")",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return
    path = directory / name
    script = "\n".join(
        [
            "#!/bin/sh",
            'case "$*" in',
            "  *encoders*)",
            *[f"    printf '%s\\n' '{line}'" for line in encoders.splitlines() if line],
            "    ;;",
            "  *)",
            f"    printf '%s\\n' '{name} version 7.0.2 Copyright'",
            "    ;;",
            "esac",
            "",
        ]
    )
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
