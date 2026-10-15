import importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import socket
from threading import Event, Thread
import time
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/modellix-design/scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("deadline_wait_helper", SCRIPTS / "invoke_and_poll.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class HttpDeadlineTests(unittest.TestCase):
    def assert_trickle_is_bounded(self, stage):
        sending = Event()

        class Trickle(BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    self.wfile.write(b"HTTP/1.1 200 OK\r\n")
                    if stage == "headers":
                        for index in range(8):
                            self.wfile.write(f"X-Progress-{index}: yes\r\n".encode())
                            self.wfile.flush()
                            sending.set()
                            time.sleep(0.10)
                    body = b'{"code":0,"data":{"task_id":"task-1","status":"success"}}'
                    self.wfile.write(f"Content-Length: {len(body)}\r\n\r\n".encode())
                    for offset in range(0, len(body), 8):
                        self.wfile.write(body[offset:offset + 8])
                        self.wfile.flush()
                        if stage == "body":
                            sending.set()
                            time.sleep(0.10)
                except OSError:
                    pass

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("localhost", 0), Trickle)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            addresses = socket.getaddrinfo("localhost", server.server_port, server.address_family, socket.SOCK_STREAM)
            started = time.monotonic()
            with patch.object(helper, "BASE_URL", f"http://localhost:{server.server_port}"), patch.object(helper, "run_rest_submit") as submit, patch("http_deadline.socket.getaddrinfo", return_value=addresses):
                with self.assertRaisesRegex(RuntimeError, "task-1"):
                    helper.wait_rest_task("task-1", "fake-deadline-key", timeout_seconds=0.25)
            self.assertLess(time.monotonic() - started, 0.70)
            self.assertTrue(sending.is_set(), "The real server must reach the tested header/body stage")
            submit.assert_not_called()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_slow_response_headers_cannot_extend_the_total_wait_budget(self):
        self.assert_trickle_is_bounded("headers")

    def test_slow_response_body_cannot_extend_the_total_wait_budget(self):
        self.assert_trickle_is_bounded("body")


if __name__ == "__main__":
    unittest.main()
