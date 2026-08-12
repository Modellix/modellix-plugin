from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "modellix" / "scripts" / "cli_runtime.py"
SPEC = importlib.util.spec_from_file_location("modellix_cli_runtime_test", MODULE_PATH)
CLI_RUNTIME = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = CLI_RUNTIME
SPEC.loader.exec_module(CLI_RUNTIME)


class CliRuntimeTests(unittest.TestCase):
    def test_versions_are_validated_and_compared_without_downgrade(self):
        self.assertEqual(CLI_RUNTIME.valid_version("1.2.3-beta.1+build.2"), "1.2.3-beta.1+build.2")
        with self.assertRaisesRegex(ValueError, "invalid"):
            CLI_RUNTIME.valid_version("../latest")
        self.assertTrue(CLI_RUNTIME.is_newer("0.0.9", "0.0.8"))
        self.assertTrue(CLI_RUNTIME.is_newer("1.0.0", "1.0.0-rc.1"))
        self.assertFalse(CLI_RUNTIME.is_newer("0.0.8", "0.0.9"))

    def test_auto_update_can_be_disabled(self):
        self.assertTrue(CLI_RUNTIME.auto_update_enabled({}))
        for value in ("0", "false", "OFF"):
            with self.subTest(value=value):
                self.assertFalse(
                    CLI_RUNTIME.auto_update_enabled({"MODELLIX_CLI_AUTO_UPDATE": value})
                )

    def test_public_npm_environment_drops_credentials(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment = CLI_RUNTIME._public_npm_environment(
                {
                    "PATH": "/tools",
                    "NPM_TOKEN": "secret",
                    "NODE_AUTH_TOKEN": "secret",
                    "npm_config_auth": "secret",
                    "npm_config_password": "secret",
                },
                Path(temporary),
            )
        self.assertEqual(environment["PATH"], "/tools")
        self.assertNotIn("NPM_TOKEN", environment)
        self.assertNotIn("NODE_AUTH_TOKEN", environment)
        self.assertNotIn("npm_config_auth", environment)
        self.assertNotIn("npm_config_password", environment)
        self.assertEqual(environment["npm_config_registry"], CLI_RUNTIME.PUBLIC_REGISTRY)

    def test_missing_cli_installs_exact_public_latest_before_use(self):
        with tempfile.TemporaryDirectory() as temporary:
            calls: list[list[str]] = []
            installed = False

            def which(command: str):
                if command == "npm":
                    return "/tools/npm"
                if command == "modellix-cli" and installed:
                    return "/tools/modellix-cli"
                return None

            def run(command, **_kwargs):
                nonlocal installed
                calls.append(command)
                if command[1] == "view":
                    return subprocess.CompletedProcess(command, 0, '"0.0.9"\n', "")
                if command[1] == "install":
                    installed = True
                    return subprocess.CompletedProcess(command, 0, "", "")
                if command[-1] == "--version":
                    return subprocess.CompletedProcess(command, 0, "modellix-cli/0.0.9\n", "")
                raise AssertionError(command)

            runtime = CLI_RUNTIME.resolve_cli_runtime(
                environment={},
                run_command=run,
                which_command=which,
                lock_root=Path(temporary) / ".update.lock",
            )

        self.assertTrue(runtime.available)
        self.assertTrue(runtime.updated)
        self.assertEqual(runtime.installed_version, "0.0.9")
        install = next(command for command in calls if command[1] == "install")
        self.assertIn("modellix-cli@0.0.9", install)
        self.assertIn("--registry", install)
        self.assertIn("--ignore-scripts", install)

    def test_registry_failure_keeps_existing_cli(self):
        with tempfile.TemporaryDirectory() as temporary:
            def which(command: str):
                return {"npm": "/tools/npm", "modellix-cli": "/tools/modellix-cli"}.get(command)

            def run(command, **_kwargs):
                if command[-1] == "--version":
                    return subprocess.CompletedProcess(command, 0, "0.0.8\n", "")
                if command[1] == "view":
                    return subprocess.CompletedProcess(command, 1, "", "registry offline")
                raise AssertionError(command)

            runtime = CLI_RUNTIME.resolve_cli_runtime(
                environment={},
                run_command=run,
                which_command=which,
                lock_root=Path(temporary) / ".update.lock",
            )

        self.assertEqual(runtime.source, "installed-fallback")
        self.assertEqual(runtime.installed_version, "0.0.8")
        self.assertIn("Could not check", runtime.update_warning or "")

    def test_newer_installed_cli_is_never_downgraded(self):
        with tempfile.TemporaryDirectory() as temporary:
            calls: list[list[str]] = []

            def which(command: str):
                return {"npm": "/tools/npm", "modellix-cli": "/tools/modellix-cli"}.get(command)

            def run(command, **_kwargs):
                calls.append(command)
                if command[-1] == "--version":
                    return subprocess.CompletedProcess(command, 0, "0.0.9\n", "")
                if command[1] == "view":
                    return subprocess.CompletedProcess(command, 0, '"0.0.8"\n', "")
                raise AssertionError(command)

            runtime = CLI_RUNTIME.resolve_cli_runtime(
                environment={},
                run_command=run,
                which_command=which,
                lock_root=Path(temporary) / ".update.lock",
            )

        self.assertEqual(runtime.source, "installed-newer")
        self.assertFalse(any(command[1] == "install" for command in calls))


if __name__ == "__main__":
    unittest.main()
