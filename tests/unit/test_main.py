"""Unit tests for main() entry point and validation."""
import io
import os
import sys
import tempfile
from unittest.mock import patch

import pytest

from serve import main, _remove_tmpdir


@pytest.mark.unit
class TestMainPortValidation:
    def test_invalid_port_zero_rejected(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"x")
            path = f.name
        try:
            old_argv = sys.argv
            sys.argv = ["serve.py", path, "--port", "0"]
            try:
                assert main() == 1
            finally:
                sys.argv = old_argv
        finally:
            os.unlink(path)

    def test_invalid_port_negative_rejected(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"x")
            path = f.name
        try:
            old_argv = sys.argv
            sys.argv = ["serve.py", path, "--port", "-1"]
            try:
                assert main() == 1
            finally:
                sys.argv = old_argv
        finally:
            os.unlink(path)

    def test_invalid_port_too_high_rejected(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"x")
            path = f.name
        try:
            old_argv = sys.argv
            sys.argv = ["serve.py", path, "--port", "65536"]
            try:
                assert main() == 1
            finally:
                sys.argv = old_argv
        finally:
            os.unlink(path)


@pytest.mark.unit
class TestTimeoutValidation:
    def test_timeout_zero_rejected(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"x")
            path = f.name
        try:
            old_argv = sys.argv
            sys.argv = ["serve.py", path, "--timeout", "0"]
            try:
                assert main() == 1
            finally:
                sys.argv = old_argv
        finally:
            os.unlink(path)

    def test_timeout_negative_rejected(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"x")
            path = f.name
        try:
            old_argv = sys.argv
            sys.argv = ["serve.py", path, "--timeout", "-1"]
            try:
                assert main() == 1
            finally:
                sys.argv = old_argv
        finally:
            os.unlink(path)


@pytest.mark.unit
class TestCleanupFailure:
    """Cleanup failure is reported to stderr and process exits non-zero."""

    def test_remove_tmpdir_failure_returns_false_and_prints_stderr(self):
        with patch("serve.shutil.rmtree") as rmtree:
            rmtree.side_effect = OSError(13, "Permission denied")
            stderr = io.StringIO()
            with patch("sys.stderr", stderr):
                result = _remove_tmpdir("/tmp/termux-serve-xyz")
            assert result is False
            assert "failed to remove temp directory" in stderr.getvalue()
            assert "/tmp/termux-serve-xyz" in stderr.getvalue()
