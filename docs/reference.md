# API reference

The program is a single module, `serve.py`, with no public package structure. This page documents the main pieces for developers or scripters who import or extend the code.

## Entry point

**`main() -> int`**

- Parses command-line arguments (`file`, `--port`, `--bind`, `-q`).
- Validates that `file` is a regular file (after `os.path.abspath`; symlinks are followed to the target).
- Copies the file to a temp dir with a URL-safe name, starts the server, prints the URL, waits until the download-done event (first GET that serves the file at `/<safe_name>`), then cleans up and returns 0 or 1. `GET /health` / `HEAD /health` do not set that event.
- Called when the script is run as `__main__`; exit code is passed to `sys.exit(main())`.

## Functions

**`url_safe_basename(path: str) -> str`**

- Returns a URL-safe version of the basename of `path`.
- Rules: spaces → `_`; any character not in `[a-zA-Z0-9_.-]` (ASCII) → `_`; collapse repeated `_`, strip leading/trailing `_`; if empty, return `"download"`.
- Used for the HTTP path and the `Content-Disposition` filename. Does not touch the filesystem.

## Classes

**`SingleFileHandler(SimpleHTTPRequestHandler)`**

- HTTP request handler that serves exactly one file, plus a fixed **`/health`** route.
- Expects the server instance to have:
  - `_served_path` — absolute path to the file to serve
  - `_safe_name` — exact path segment that must match (e.g. `file.apk`)
  - `_on_download_done()` — callable invoked once after a **file** GET response is sent (used to trigger shutdown). Not called for `/health`.
- **`_normalized_path(self) -> str`** — Strips query string, URL-unquotes, removes one leading `/`; used for path matching.
- **`_handle_health(self) -> bool`** — If the normalized path is `health`, sends `200` with `text/plain; charset=utf-8` and body `ok\n` for GET (headers only for HEAD), then returns `True`. Otherwise returns `False`. Never calls `_on_download_done()`.
- **`do_GET(self)`** — If `_handle_health()`, return. Else same as before: compare normalized path to `_safe_name`; if different, 404. Read the **entire file** at `_served_path`, send 200 with appropriate headers, write body, flush, then call `_on_download_done()`. See [Behavior](behavior.md#whole-file-buffering).
- **`do_HEAD(self)`** — If `_handle_health()`, return. Else same as before for the file path: headers only, no `_on_download_done()`.
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
