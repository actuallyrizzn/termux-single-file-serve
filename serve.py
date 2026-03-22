#!/usr/bin/env python3
"""
Single-use HTTP server: serve one file, then delete temp copy and exit after first download.
Usage: python serve.py <path-to-file>

Copyright (C) 2025  Contributors to the termux-single-file-serve project
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.
See <https://www.gnu.org/licenses/>.
"""

import argparse
import mimetypes
import os
import re
import shutil
import signal
import sys
import tempfile
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote


def url_safe_basename(path: str) -> str:
    """Return a filename safe for URLs: no spaces, no problematic chars."""
    name = os.path.basename(path)
    # Replace spaces with underscores, strip or replace unsafe chars
    name = name.replace(" ", "_")
    name = re.sub(r"[^\w\-.]", "_", name, flags=re.ASCII)
    # Collapse multiple underscores, strip leading/trailing
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "download"
    return name


class SingleFileHandler(SimpleHTTPRequestHandler):
    """Serves one file; GET triggers shutdown, HEAD is informational only."""

    def _resolve_request(self):
        """Validate request path and read file. Returns (data, safe_name) or None."""
        served_path = getattr(self.server, "_served_path", None)
        safe_name = getattr(self.server, "_safe_name", None)
        if not served_path or not safe_name:
            self.send_error(500, "Server misconfigured")
            return None
        # Strip query string, unquote, exact-match only (no slash normalization or traversal).
        path = unquote(self.path.split("?", 1)[0])
        if path.startswith("/"):
            path = path[1:]
        if path != safe_name:
            self.send_error(404, "Not Found")
            return None
        try:
            with open(served_path, "rb") as f:
                data = f.read()
        except OSError:
            self.send_error(404, "Not Found")
            return None
        return data, safe_name

    def _send_headers(self, safe_name, content_length):
        """Send response status and common headers."""
        content_type = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        # safe_name is URL-sanitized (no quotes/newlines); safe for header value.
        self.send_header("Content-Disposition", f'attachment; filename="{safe_name}"')
        self.send_header("Connection", "close")
        self.end_headers()

    def do_GET(self):
        result = self._resolve_request()
        if result is None:
            return
        data, safe_name = result
        try:
            self._send_headers(safe_name, len(data))
            self.wfile.write(data)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass
        finally:
            getattr(self.server, "_on_download_done", lambda: None)()

    def do_HEAD(self):
        """Return headers without body; does not consume the one-shot download."""
        result = self._resolve_request()
        if result is None:
            return
        data, safe_name = result
        try:
            self._send_headers(safe_name, len(data))
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass

    def log_message(self, format, *args):
        if os.environ.get("TERMUX_SERVE_DEBUG"):
            super().log_message(format, *args)


def _remove_tmpdir(tmpdir: str) -> bool:
    """Remove temp directory; on failure print to stderr and return False."""
    try:
        shutil.rmtree(tmpdir)
        return True
    except OSError as e:
        print(f"Error: failed to remove temp directory {tmpdir}: {e}", file=sys.stderr)
        return False


def _read_version() -> str:
    """Read version from VERSION file next to this script."""
    try:
        vf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")
        with open(vf) as f:
            return f.read().strip()
    except OSError:
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve one file over HTTP, then cleanup after download.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {_read_version()}")
    parser.add_argument("file", help="Path to the file to share")
    parser.add_argument("--port", type=int, default=8765, help="Port (default: 8765)")
    parser.add_argument(
        "--bind",
        default="127.0.0.1",
        metavar="ADDR",
        help="Address to bind to (default: 127.0.0.1). Use 0.0.0.0 to allow other devices/interfaces.",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Only print the download URL")
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        metavar="SECONDS",
        help="Exit if no download within SECONDS (default: wait indefinitely). On timeout, cleanup and exit with code 1.",
    )
    args = parser.parse_args()

    if args.timeout is not None and args.timeout <= 0:
        print(f"Error: timeout must be positive, got {args.timeout}", file=sys.stderr)
        return 1

    if not (1 <= args.port <= 65535):
        print(f"Error: port must be between 1 and 65535, got {args.port}", file=sys.stderr)
        return 1

    src = os.path.abspath(args.file)
    if not os.path.isfile(src):
        print(f"Error: not a file: {src}", file=sys.stderr)
        return 1

    safe_name = url_safe_basename(src)
    tmpdir = tempfile.mkdtemp(prefix="termux-serve-")
    served_path = os.path.join(tmpdir, safe_name)
    try:
        shutil.copy2(src, served_path)
    except OSError as e:
        print(f"Error copying file: {e}", file=sys.stderr)
        _remove_tmpdir(tmpdir)
        return 1

    shutdown_event = threading.Event()
    port = args.port
    bind = args.bind

    class Server(HTTPServer):
        """HTTPServer that serves one file; attributes set explicitly in __init__."""

        def __init__(self, server_address, RequestHandlerClass, served_path, safe_name, on_download_done):
            super().__init__(server_address, RequestHandlerClass)
            self._served_path = served_path
            self._safe_name = safe_name
            self._on_download_done = on_download_done

    try:
        server = Server((bind, port), SingleFileHandler, served_path, safe_name, shutdown_event.set)
    except OSError as e:
        print(f"Error: could not bind to {bind}:{port}: {e}", file=sys.stderr)
        _remove_tmpdir(tmpdir)
        return 1
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    def _on_signal(signum, frame):
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _on_signal)
        except (ValueError, OSError):
            pass  # SIGTERM not available on all platforms

    if bind == "0.0.0.0":
        url = f"http://127.0.0.1:{port}/{safe_name}"
        url_note = f" (or http://<this-device-ip>:{port}/{safe_name} from another app/device)"
    else:
        url = f"http://{bind}:{port}/{safe_name}"
        url_note = ""
    if args.quiet:
        print(url, flush=True)
    else:
        print("Download at:")
        print(f"  {url}{url_note}")
        print("(Server exits after first download.)")

    if args.timeout is None:
        shutdown_event.wait()
    else:
        if not shutdown_event.wait(timeout=args.timeout):
            print("Error: no download within timeout", file=sys.stderr)
            server.shutdown()
            server.server_close()
            _remove_tmpdir(tmpdir)
            return 1
    server.shutdown()
    server.server_close()
    if not _remove_tmpdir(tmpdir):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
