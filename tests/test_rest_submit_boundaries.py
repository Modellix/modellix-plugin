import argparse
import importlib.util
import io
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from threading import Thread
import unittest
import urllib.error
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/modellix-design/scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("media_submit_helper", SCRIPTS / "invoke_and_poll.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class RestSubmitBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.args = argparse.Namespace(model_slug="openai/gpt-image-2")

    def test_invalid_json_after_paid_post_is_unknown_and_not_retried(self):
        with patch.object(helper, "http_request", side_effect=ValueError("invalid response")) as request:
            with self.assertRaisesRegex(RuntimeError, "outcome.*unknown"):
                helper.run_rest_submit(self.args, {"prompt": "library"}, "test-key")
        self.assertEqual(request.call_count, 1)

    def test_unusable_success_responses_are_unknown(self):
        for payload in (None, [], {"code": "invalid"}, {"code": 0}, {"code": 0, "data": {"task_id": "\n"}}):
            with self.subTest(payload=payload), patch.object(helper, "http_request", return_value=payload) as request:
                with self.assertRaisesRegex(RuntimeError, "outcome.*unknown"):
                    helper.run_rest_submit(self.args, {"prompt": "library"}, "test-key")
                self.assertEqual(request.call_count, 1)

    def test_submit_failure_does_not_echo_upstream_fields(self):
        secret = "fake-test-key-never-log"
        with patch.object(helper, "http_request", return_value={"code": 400, "message": secret, "request": {"prompt": "private prompt"}}):
            with self.assertRaises(RuntimeError) as caught:
                helper.run_rest_submit(self.args, {"prompt": "library"}, secret)
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn("private prompt", str(caught.exception))

    def test_http_error_preserves_http_failure_and_does_not_consume_error_body(self):
        class ErrorBody(io.BytesIO):
            def read(self, size=-1):
                raise AssertionError("Upstream HTTP error bodies must not be consumed or echoed")

        body = ErrorBody(b'{"code":0,"message":"untrusted"}')
        failure = urllib.error.HTTPError("https://api.modellix.ai/api/v1/test", 503, "Unavailable", {}, body)
        with patch.object(helper.urllib.request.OpenerDirector, "open", side_effect=failure):
            result = helper.http_request("https://api.modellix.ai/api/v1/test", "POST", "test-key", {})
        self.assertEqual(result, {"code": 503})
        self.assertTrue(body.closed)

    def test_authenticated_request_does_not_follow_cross_origin_redirect(self):
        received = []

        class Destination(BaseHTTPRequestHandler):
            def do_GET(self):
                received.append(self.headers.get("Authorization"))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"code":0}')

            def log_message(self, *args):
                pass

        destination = ThreadingHTTPServer(("localhost", 0), Destination)

        class Redirect(BaseHTTPRequestHandler):
            def do_POST(self):
                self.send_response(302)
                self.send_header("Location", f"http://localhost:{destination.server_port}/different-origin")
                self.end_headers()

            def log_message(self, *args):
                pass

        redirect = ThreadingHTTPServer(("localhost", 0), Redirect)
        threads = [Thread(target=server.serve_forever, daemon=True) for server in (destination, redirect)]
        for thread in threads:
            thread.start()
        try:
            result = helper.http_request(f"http://localhost:{redirect.server_port}/submit", "POST", "fake-redirect-key", {})
            self.assertEqual(received, [], "Never forward the credential to a redirect destination")
            self.assertEqual(result, {"code": 302})
        finally:
            for server in (redirect, destination):
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
