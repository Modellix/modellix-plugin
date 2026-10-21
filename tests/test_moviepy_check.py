from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "modellix-moviepy" / "scripts" / "check_moviepy.py"
SPEC = importlib.util.spec_from_file_location("modellix_moviepy_check_test", MODULE_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)

INSTALL = 'python3 -m pip install "moviepy>=2,<3" Pillow'


class CheckMoviepyTests(unittest.TestCase):
    def test_source_never_invokes_pip(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("os.system", source)
        self.assertEqual(CHECK.INSTALL_COMMAND, INSTALL)

    def test_missing_imports_stop_without_installing(self):
        with mock.patch.object(CHECK, "_distribution_version", return_value=None):
            with mock.patch.object(CHECK, "_importable", return_value=False):
                payload = CHECK.report()
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["action"], "stop")
        self.assertEqual(payload["missing"], ["moviepy", "PIL"])
        self.assertEqual(payload["install_command"], INSTALL)
        self.assertIn("wait for confirmation", payload["message"])

    def test_moviepy_1_is_not_accepted(self):
        def importable(name: str) -> bool:
            return name in {"moviepy", "PIL"}

        with mock.patch.object(CHECK, "_distribution_version", return_value="1.0.3"):
            with mock.patch.object(CHECK, "_importable", side_effect=importable):
                payload = CHECK.report()
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["missing"], ["moviepy"])
        self.assertIn("1.0.3", payload["message"])
        self.assertIn("2.x", payload["message"])
        self.assertEqual(payload["install_command"], INSTALL)

    def test_moviepy_2_and_pillow_continue(self):
        def importable(name: str) -> bool:
            return name in {"moviepy", "PIL"}

        with mock.patch.object(CHECK, "_distribution_version", return_value="2.1.2"):
            with mock.patch.object(CHECK, "_importable", side_effect=importable):
                payload = CHECK.report()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["action"], "continue")
        self.assertEqual(payload["missing"], [])
        self.assertEqual(payload["moviepy_version"], "2.1.2")

    def test_cli_prints_json_and_does_not_install(self):
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["install_command"], INSTALL)
        self.assertEqual(completed.returncode, 0 if payload["ok"] else 1)
        combined = f"{completed.stdout}\n{completed.stderr}"
        self.assertNotIn("Successfully installed", combined)

    def test_cli_requires_json(self):
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH)],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--json", completed.stderr)
