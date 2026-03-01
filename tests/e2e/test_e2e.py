"""End-to-end tests: run serve.py as subprocess, request file, verify exit and cleanup.

Cleanup removes global termux-serve-* dirs in gettempdir(). If adding parallel e2e tests,
consider process- or test-specific temp dirs to avoid one test removing another's dirs.
"""
import glob
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest
from urllib.request import urlopen


@pytest.mark.e2e
class TestE2E:
    def test_full_flow_exits_after_download_and_cleans_up(self, free_port: int):
        tmpdir = tempfile.gettempdir()
        for d in glob.glob(f"{tmpdir}/termux-serve-*"):
            shutil.rmtree(d, ignore_errors=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"e2e test content")
            src = f.name
        try:
            proc = subprocess.Popen(
                [sys.executable, "-u", "serve.py", src, "--port", str(free_port), "-q"],
                cwd=Path(__file__).resolve().parent.parent.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            url = None
            for _ in range(50):
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break
                line = line.strip()
                if line.startswith("http://"):
                    url = line
                    break
                time.sleep(0.05)
            stderr_diag = (proc.stderr.read() if proc.stderr else "") if url is None else ""
            assert url is not None, f"Expected URL in stdout. stderr: {stderr_diag}"
            # GET thread triggers server to serve and exit; we then wait for the process to exit.
            body = []
            def do_get():
                try:
                    with urlopen(url, timeout=5) as resp:
                        body.append(resp.read())
                except Exception as e:
                    body.append(e)
            t = threading.Thread(target=do_get)
            t.start()
            proc.wait(timeout=10)
            t.join(timeout=5)
            assert len(body) == 1, body
            if isinstance(body[0], Exception):
                raise body[0]
            assert body[0] == b"e2e test content"
            assert proc.returncode == 0
            time.sleep(0.5)
            leftovers = [d for d in glob.glob(f"{tmpdir}/termux-serve-*")]
            assert not leftovers, f"Expected no leftover temp dirs, got: {leftovers}"
        finally:
            Path(src).unlink(missing_ok=True)
            for d in glob.glob(f"{tempfile.gettempdir()}/termux-serve-*"):
                shutil.rmtree(d, ignore_errors=True)
