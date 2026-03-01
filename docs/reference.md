# API reference

The program is a single module, `serve.py`, with no public package structure. This page documents the main pieces for developers or scripters who import or extend the code.

## Entry point

**`main() -> int`**

- Parses command-line arguments (`file`, `--port`, `--bind`, `-q`).
- Validates that `file` is a regular file (after `os.path.abspath`; symlinks are followed to the target).
- Copies the file to a temp dir with a URL-safe name, starts the server, prints the URL, waits for the first GET that serves the file, then cleans up and returns 0 or 1.
- Called when the script is run as `__main__`; exit code is passed to `sys.exit(main())`.

## Functions

**`url_safe_basename(path: str) -> str`**

- Returns a URL-safe version of the basename of `path`.
- Rules: spaces → `_`; any character not in `[a-zA-Z0-9_.-]` (ASCII) → `_`; collapse repeated `_`, strip leading/trailing `_`; if empty, return `"download"`.
- Used for the HTTP path and the `Content-Disposition` filename. Does not touch the filesystem.

## Classes

**`SingleFileHandler(SimpleHTTPRequestHandler)`**

- HTTP request handler that serves exactly one file.
- Expects the server instance to have:
  - `_served_path` — absolute path to the file to serve
  - `_safe_name` — exact path segment that must match (e.g. `file.apk`)
  - `_on_download_done()` — callable invoked once after the response is sent (used to trigger shutdown).
- **`do_GET(self)`**
  - Unquotes `self.path`, strips a single leading `/`, and compares to `_safe_name`. If different, sends 404.
  - Reads the **entire file** at `_served_path` into memory, sends 200 with `Content-Type: application/octet-stream` and `Content-Disposition: attachment; filename="<safe_name>"`, writes the body, flushes, then calls `_on_download_done()`. No streaming; large files increase memory use. See [Behavior](behavior.md#whole-file-buffering).
- **`log_message(self, format, *args)`** — Overridden to no-op (quiet by default).

## Server setup (inside `main()`)

The server is an `HTTPServer` subclass created inside `main()` with:

- **`(bind, port)`** — Listening address and port.
- **`SingleFileHandler`** — Request handler class.
- **`_served_path`**, **`_safe_name`** — Set as class attributes from locals in `main()`.
- **`_on_download_done()`** — Sets a `threading.Event` that the main thread waits on.

The server runs in a daemon thread; the main thread blocks on the event, then calls `server.shutdown()`, `server.server_close()`, and removes the temp dir with `shutil.rmtree(tmpdir)`. Cleanup failure is reported to stderr and exits with code 1.

## Dependencies

All from the Python standard library:

- `argparse`, `os`, `re`, `shutil`, `sys`, `tempfile`, `threading`
- `http.server.HTTPServer`, `http.server.SimpleHTTPRequestHandler`
- `urllib.parse.unquote`

No third-party packages are required to run the script.
