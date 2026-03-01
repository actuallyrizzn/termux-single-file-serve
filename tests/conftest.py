"""Pytest fixtures and config."""
import socket

import pytest


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture
def free_port() -> int:
    """Return a port number that is currently free (bind to 0, then close).
    Note: TOCTOU race—another process could take the port before the test binds.
    In noisy CI, consider retry on bind failure."""
    return _free_port()


@pytest.fixture
def sample_content() -> bytes:
    """Sample bytes for served file."""
    return b"hello world\n"
