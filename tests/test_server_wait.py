import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/modellix-design/scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("media_wait_helper", SCRIPTS / "invoke_and_poll.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class ServerWaitTests(unittest.TestCase):
    def test_wait_query_and_transport_budget(self):
        with patch.object(helper, "http_request", return_value={"code": 0}) as request:
            helper.run_rest_poll("task-1", "test-key", remaining_seconds=60)
        kwargs = request.call_args.kwargs
        self.assertTrue(kwargs["url"].endswith("/tasks/task-1?wait=true&timeout=45"))
        self.assertEqual(kwargs["timeout_seconds"], 50)

    def test_server_wait_has_no_local_sleep(self):
        pending = {"code": 0, "data": {"task_id": "task-1", "status": "pending", "wait": {"timed_out": True, "elapsed_ms": 1}}}
        complete = {"code": 0, "data": {"task_id": "task-1", "status": "success"}}
        with patch.object(helper, "run_rest_poll", side_effect=[pending, complete]) as request, patch.object(helper.time, "sleep") as sleep:
            result = helper.wait_rest_task("task-1", "test-key", 5)
        self.assertEqual(result, complete)
        self.assertEqual(request.call_count, 2)
        sleep.assert_not_called()

    def test_missing_wait_metadata_is_explicitly_rejected(self):
        with patch.object(helper, "run_rest_poll", return_value={"code": 0, "data": {"task_id": "task-1", "status": "pending"}}):
            with self.assertRaisesRegex(RuntimeError, "server-side wait"):
                helper.wait_rest_task("task-1", "test-key", 5)

    def test_timeout_preserves_task_id_and_never_submits(self):
        with patch.object(helper.time, "monotonic", side_effect=[0, 6]), patch.object(helper, "run_rest_submit") as submit:
            with self.assertRaisesRegex(TimeoutError, "task-1"):
                helper.wait_rest_task("task-1", "test-key", 5)
        submit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
