"""Integration tests: real HTTP server, real request, verify response and shutdown."""
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import HTTPServer
from urllib.request import urlopen

import pytest

from serve import SingleFileHandler


@pytest.mark.integration
class TestServeIntegration:
    def test_server_serves_file_then_shuts_down(self, free_port: int, sample_content: bytes):
        tmpdir = tempfile.mkdtemp(prefix="termux-serve-test-")
        try:
            served_path = f"{tmpdir}/testfile.bin"
            with open(served_path, "wb") as f:
                f.write(sample_content)
            safe_name = "testfile.bin"
            shutdown_event = threading.Event()

            class Server(HTTPServer):
                _served_path = served_path
                _safe_name = safe_name

                def _on_download_done(self):
                    shutdown_event.set()

            server = Server(("", free_port), SingleFileHandler)
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            url = f"http://127.0.0.1:{free_port}/{safe_name}"
            try:
                with urlopen(url, timeout=5) as resp:
                    assert resp.status == 200
                    assert resp.read() == sample_content
                shutdown_event.wait(timeout=2)
                assert shutdown_event.is_set()
            finally:
                server.shutdown()
                server.server_close()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_server_returns_404_for_wrong_path(self, free_port: int, sample_content: bytes):
        tmpdir = tempfile.mkdtemp(prefix="termux-serve-test-")
        try:
            served_path = f"{tmpdir}/real.bin"
            with open(served_path, "wb") as f:
                f.write(sample_content)
            safe_name = "real.bin"
            shutdown_event = threading.Event()

            class Server(HTTPServer):
                _served_path = served_path
                _safe_name = safe_name

                def _on_download_done(self):
                    shutdown_event.set()

            server = Server(("", free_port), SingleFileHandler)
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            try:
                with pytest.raises(Exception):  # HTTPError 404
                    urlopen(f"http://127.0.0.1:{free_port}/wrong.bin", timeout=5)
                assert not shutdown_event.is_set()
            finally:
                server.shutdown()
                server.server_close()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_timeout_exits_without_download(self, free_port: int):
        """With --timeout, if no request is made, process exits 1 and cleans up."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"x")
            path = f.name
        try:
            root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            proc = subprocess.run(
                [sys.executable, "serve.py", path, "--port", str(free_port), "--timeout", "1"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=root,
            )
            assert proc.returncode == 1
            assert "no download within timeout" in proc.stderr
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
