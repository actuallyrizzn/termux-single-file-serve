"""Pytest fixtures and config."""
import socket
import tempfile
from pathlib import Path

import pytest


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture
def free_port() -> int:
    """Return a port number that is currently free."""
    return _free_port()


@pytest.fixture
def temp_file(tmp_path: Path) -> Path:
    """A temporary file with some content."""
    f = tmp_path / "testfile.bin"
    f.write_bytes(b"test content\n")
    return f


@pytest.fixture
def sample_content() -> bytes:
    """Sample bytes for served file."""
    return b"hello world\n"
