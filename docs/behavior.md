# Behavior

This page describes exactly how the program runs and when it exits.

## Flow

1. **Validate:** Resolve the given path with `os.path.abspath` (which follows symlinks) and check it is a regular file. The file actually served is this resolved target, not necessarily the path the user passed. Exit with code 1 and an error message if not a file.
2. **Copy:** Compute a URL-safe basename (see [Configuration](configuration.md)). Create a temporary directory (prefix `termux-serve-`), copy the file there with the safe name.
3. **Serve:** Start an HTTP server bound to the configured address and port. The server handles GET and HEAD requests. **`GET /health`** and **`HEAD /health`** return `200` with a small plain-text response (`ok` plus newline on GET; headers only on HEAD) and **do not** trigger shutdown or consume the one-shot download—see [Health endpoint](#health-endpoint). For the file: GET serves the file and triggers shutdown; HEAD returns headers only (Content-Type, Content-Length, Content-Disposition) without consuming the one-shot download—this allows download managers that probe before fetching to work correctly. Other methods get a 405 or similar from the base handler. Aside from `/health`, only the path `/<safe_name>` is served (the query string, if any, is ignored; e.g. `GET /file.apk?x=1` is treated as `GET /file.apk`). All other paths return 404.
4. **Print URL:** Print the download URL (and optionally a note for `0.0.0.0`). In quiet mode, only the URL is printed.
5. **Wait:** Block until the “download done” event is set (see below).
6. **Cleanup:** Call `server.shutdown()`, `server_close()`, then `shutil.rmtree(tmpdir)`. The same cleanup runs if the process receives SIGINT (e.g. Ctrl+C) or SIGTERM: a signal handler sets the shutdown event so the main thread exits the wait and performs shutdown and temp-dir removal. If removal fails (e.g. permission, NFS, open handle), an error is printed to stderr and the process exits with code 1; otherwise exit 0.

## Health endpoint

- **`GET /health`** — Response `200`, `Content-Type: text/plain; charset=utf-8`, body `ok\n`. Does **not** call the download-done callback; the server keeps running.
- **`HEAD /health`** — Same status and headers as GET (including `Content-Length` for the `ok\n` body), no body. Does **not** consume the one-shot download.

Query strings are ignored for matching (e.g. `GET /health?probe=1` is still the health check).

**Reserved path:** The handler checks `/health` before the file path. If your served file’s URL-safe basename were exactly `health`, `GET /health` would hit the health endpoint, not the file. Use a different filename or extension in that rare case.

## When is “download done” triggered?

The server uses a custom request handler. When it serves the file:

1. It sends the full response (status 200, headers, body).
2. It flushes the response stream.
3. It then calls the callback that sets the “download done” event.

So **“download done” means “we have attempted to send the response”**, not “the client has received every byte.” If the client disconnects mid-transfer (e.g. cancel, slow link, timeout), the write may fail with a broken pipe; the server still triggers shutdown, cleans up the temp copy, and exits. The client may end up with a truncated or missing file.

In practice, for a single file and a normal browser download, this is rarely an issue. For scripting or unreliable networks, be aware that the server exits as soon as it has written (or attempted to write) the response, not when the client has fully received it.

## Whole-file buffering

The handler reads the entire file into memory with `f.read()` before sending the response. There is no streaming (chunked read/write). For very large files (e.g. multi-gigabyte), this can cause high memory use or out-of-memory errors. The tool is intended for typical single-file sizes (e.g. APKs, documents). If you need to serve very large files, consider a different server that streams.

## Single request only

Only one request is intended to **finish the session**: the first GET for `/<safe_name>` that is fully handled as a file download. You may issue any number of **`GET /health`** or **`HEAD /health`** requests before that; they do not count toward shutdown.

After the file GET is handled:

- The “download done” event is set.
- The main thread wakes, shuts down the server, and removes the temp dir.
- The process exits.

Any further connection attempts will get connection refused (server already closed). A second GET before the first one completes would be served the same file again; in normal use you open the URL once and download.

## Temp directory

- Created with `tempfile.mkdtemp(prefix="termux-serve-")` (so under the system temp dir, e.g. `/tmp` on Linux).
- Contains exactly one file: the copy of your file with the URL-safe name.
- Removed with `shutil.rmtree()` after shutdown. If removal fails (e.g. permission, NFS, open handle), an error is printed to stderr and the process exits with code 1.

## Optional timeout

With `--timeout SECONDS`, the main thread waits at most that long for the **download-done** event (i.e. a GET that serves the file at `/<safe_name>` and triggers shutdown). **`/health` requests do not set that event.** If the timeout expires before such a file GET, the server shuts down, the temp dir is removed, and the process exits with code 1. Without `--timeout`, the process waits indefinitely for the file download.

## Signals

SIGINT (e.g. Ctrl+C) and SIGTERM are handled: a handler sets the shutdown event so the main thread exits the wait, runs shutdown and temp-dir removal, then exits. The temp directory is not left behind when you interrupt the process.
