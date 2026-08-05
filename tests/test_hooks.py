from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HOOK_LIB = load_module("modellix_hook_lib_test", ROOT / "scripts" / "_hook_lib.py")
INVOKE = load_module(
    "modellix_invoke_and_poll_test",
    ROOT / "skills" / "modellix" / "scripts" / "invoke_and_poll.py",
)


class HookTests(unittest.TestCase):
    def run_hook(self, script: str, payload: dict, temp_dir: str, *, with_key: bool = True):
        env = os.environ.copy()
        env.update({"TMP": temp_dir, "TEMP": temp_dir, "TMPDIR": temp_dir})
        if with_key:
            env["MODELLIX_API_KEY"] = "test-only-key"
        else:
            env.pop("MODELLIX_API_KEY", None)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / script)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_paid_prompt_is_never_persisted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = {
                "session_id": "prompt-privacy",
                "command": (
                    "modellix-cli model run --model-slug google/nano-banana-2-lite "
                    "--body '{\"prompt\":\"private user prompt\"}' --wait --json"
                ),
            }
            self.run_hook("modellix_run_guard.py", payload, temp_dir)
            self.run_hook(
                "modellix_task_watch.py",
                {
                    **payload,
                    "exit_code": 0,
                    "output": '{"status":"success","task_id":"task-private-123"}',
                },
                temp_dir,
            )
            states = list((Path(temp_dir) / "modellix-hooks").glob("*.json"))
            self.assertEqual(len(states), 1)
            state_text = states[0].read_text(encoding="utf-8")
            self.assertNotIn("private user prompt", state_text)
            state = json.loads(state_text)
            record = next(iter(state["submits"].values()))
            self.assertNotIn("command", record)

    def test_repeated_paid_submit_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = {
                "session_id": "repeat-guard",
                "command": (
                    "modellix-cli model run --model-slug google/nano-banana-2-lite "
                    "--body '{\"prompt\":\"same\"}' --wait --json"
                ),
            }
            self.assertEqual(self.run_hook("modellix_run_guard.py", payload, temp_dir), {})
            self.run_hook(
                "modellix_task_watch.py",
                {
                    **payload,
                    "exit_code": 0,
                    "output": '{"status":"success","task_id":"task-repeat-123"}',
                },
                temp_dir,
            )
            second = self.run_hook("modellix_run_guard.py", payload, temp_dir)
            permission = second.get("permission") or second.get("hookSpecificOutput", {}).get(
                "permissionDecision"
            )
            self.assertEqual(permission, "ask")

    def test_rejected_pre_submit_does_not_count_as_executed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = {
                "session_id": "bounded-batch",
                "command": "modellix-cli model batch --body-file jobs.json",
            }
            response = self.run_hook("modellix_run_guard.py", payload, temp_dir)
            permission = response.get("permission") or response.get(
                "hookSpecificOutput", {}
            ).get("permissionDecision")
            self.assertEqual(permission, "ask")
            state_path = next((Path(temp_dir) / "modellix-hooks").glob("*.json"))
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["submits"], {})

    def test_success_output_with_null_error_is_not_failed(self):
        self.assertFalse(HOOK_LIB.looks_failed('{"ok":true,"error":null}', 0))
        self.assertFalse(HOOK_LIB.looks_failed('{"error":null}'))
        self.assertTrue(HOOK_LIB.looks_failed('{"ok":false,"error":{"message":"bad"}}', 1))

    def test_cross_platform_launcher_fails_open(self):
        result = subprocess.run(
            ["node", str(ROOT / "scripts" / "run_python_hook.mjs"), "modellix_run_guard"],
            input='{"command":"echo safe"}',
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {})


class InvokeAndPollTests(unittest.TestCase):
    def test_paid_rest_submit_is_attempted_once(self):
        args = SimpleNamespace(model_slug="google/nano-banana-2-lite")
        response = {"code": 503, "message": "temporary failure"}
        with mock.patch.object(INVOKE, "http_request", return_value=response) as request:
            with self.assertRaisesRegex(RuntimeError, "was not retried"):
                INVOKE.run_rest_submit(args, {"prompt": "test"}, "test-key")
        self.assertEqual(request.call_count, 1)

    def test_paid_rest_transport_error_is_not_retried(self):
        args = SimpleNamespace(model_slug="google/nano-banana-2-lite")
        error = INVOKE.urllib.error.URLError("temporary failure")
        with mock.patch.object(INVOKE, "http_request", side_effect=error) as request:
            with self.assertRaisesRegex(RuntimeError, "was not retried"):
                INVOKE.run_rest_submit(args, {"prompt": "test"}, "test-key")
        self.assertEqual(request.call_count, 1)

    def test_cli_key_uses_environment_not_arguments(self):
        args = SimpleNamespace(
            model_slug="google/nano-banana-2-lite",
            timeout="5m",
            body_file=None,
            body='{"prompt":"test"}',
            api_key="test-key",
        )
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"task_id":"task-test","status":"success"}',
            stderr="",
        )
        with mock.patch.object(INVOKE.subprocess, "run", return_value=completed) as run:
            INVOKE.run_cli(args)
        command = run.call_args.args[0]
        self.assertNotIn("--api-key", command)
        self.assertEqual(run.call_args.kwargs["env"]["MODELLIX_API_KEY"], "test-key")


if __name__ == "__main__":
    unittest.main()
