"""Unit tests for SingleFileHandler."""
import os
import tempfile
from io import BytesIO
from unittest.mock import Mock

import pytest

from serve import SingleFileHandler
from http.server import HTTPServer


@pytest.mark.unit
class TestSingleFileHandler:
    def _make_request(self, path: str, server_safe_name: str, content: bytes = b"content"):
        """Build a minimal request and handler; call do_GET. Uses a real temp file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(content)
            served_path = f.name
        try:
            server = Mock(spec=HTTPServer)
            server._served_path = served_path
            server._safe_name = server_safe_name
            server._on_download_done = Mock()
            # Minimal handler setup: request line, headers, rfile, wfile
            request = Mock()
            request.makefile.return_value = BytesIO(b"")
            handler = SingleFileHandler(request, ("127.0.0.1", 0), server)
            handler.path = path
            handler.wfile = BytesIO()
            handler.requestline = "GET / HTTP/1.1"
            handler.command = "GET"
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.send_error = Mock()
            handler.do_GET()
            return handler, server
        finally:
            try:
                os.unlink(served_path)
            except OSError:
                pass

    def test_serves_file_for_matching_path(self):
        handler, server = self._make_request("/foo.bin", "foo.bin")
        handler.send_response.assert_called_once_with(200)
        assert handler.wfile.getvalue() == b"content"
        server._on_download_done.assert_called_once()

    def test_404_for_wrong_path(self):
        handler, server = self._make_request("/other.bin", "foo.bin")
        handler.send_error.assert_called_once_with(404, "Not Found")
        server._on_download_done.assert_not_called()

    def test_serves_file_when_path_has_query_string(self):
        """Real HTTP: path can include query string; we strip it and match path only."""
        handler, server = self._make_request("/foo.bin?x=1&y=2", "foo.bin")
        handler.send_response.assert_called_once_with(200)
        assert handler.wfile.getvalue() == b"content"
        server._on_download_done.assert_called_once()

    def test_404_when_path_with_query_string_does_not_match(self):
        handler, server = self._make_request("/other.bin?x=1", "foo.bin")
        handler.send_error.assert_called_once_with(404, "Not Found")

    def test_serves_file_for_encoded_path_segment(self):
        """Path is unquoted before comparison; %2E is '.' (e.g. file%2Ebin -> file.bin)."""
        handler, server = self._make_request("/file%2Ebin", "file.bin")
        handler.send_response.assert_called_once_with(200)
        server._on_download_done.assert_called_once()

    def test_500_when_server_missing_attrs(self):
        server = Mock(spec=HTTPServer)
        server._served_path = None
        server._safe_name = None
        request = Mock()
        request.makefile.return_value = BytesIO(b"")
        handler = SingleFileHandler(request, ("127.0.0.1", 0), server)
        handler.path = "/foo"
        handler.wfile = BytesIO()
        handler.send_error = Mock()
        handler.do_GET()
        handler.send_error.assert_called_once_with(500, "Server misconfigured")
