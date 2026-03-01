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
import os
import re
import shutil
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
    """Serves one file; after sending it, triggers shutdown and cleanup."""

    def do_GET(self):
        served_path = getattr(self.server, "_served_path", None)
        safe_name = getattr(self.server, "_safe_name", None)
        if not served_path or not safe_name:
            self.send_error(500, "Server misconfigured")
            return
        path = unquote(self.path)
        if path.startswith("/"):
            path = path[1:]
        if path != safe_name:
            self.send_error(404, "Not Found")
            return
        try:
            with open(served_path, "rb") as f:
                data = f.read()
        except OSError:
            self.send_error(404, "Not Found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'attachment; filename="{safe_name}"')
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()
        getattr(self.server, "_on_download_done", lambda: None)()

    def log_message(self, format, *args):
        pass  # Quiet by default; remove to re-enable request logging


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve one file over HTTP, then cleanup after download.")
    parser.add_argument("file", help="Path to the file to share")
    parser.add_argument("--port", type=int, default=8765, help="Port (default: 8765)")
    parser.add_argument(
        "--bind",
        default="127.0.0.1",
        metavar="ADDR",
        help="Address to bind to (default: 127.0.0.1). Use 0.0.0.0 to allow other devices/interfaces.",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Only print the download URL")
    args = parser.parse_args()

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
        shutil.rmtree(tmpdir, ignore_errors=True)
        return 1

    shutdown_event = threading.Event()
    port = args.port
    bind = args.bind

    class Server(HTTPServer):
        _served_path = served_path
        _safe_name = safe_name

        def _on_download_done(self):
            shutdown_event.set()

    server = Server((bind, port), SingleFileHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

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

    shutdown_event.wait()
    server.shutdown()
    server.server_close()
    shutil.rmtree(tmpdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
