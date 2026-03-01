"""Unit tests for main() entry point and validation."""
import os
import sys
import tempfile

import pytest

from serve import main


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
