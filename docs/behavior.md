# Behavior

This page describes exactly how the program runs and when it exits.

## Flow

1. **Validate:** Resolve the given path with `os.path.abspath` and check it is a regular file. Exit with code 1 and an error message if not.
2. **Copy:** Compute a URL-safe basename (see [Configuration](configuration.md)). Create a temporary directory (prefix `termux-serve-`), copy the file there with the safe name.
3. **Serve:** Start an HTTP server bound to the configured address and port. The server handles only GET requests; any other method gets a 405 or similar from the base handler. Only the exact path `/<safe_name>` is served; all other paths return 404.
4. **Print URL:** Print the download URL (and optionally a note for `0.0.0.0`). In quiet mode, only the URL is printed.
5. **Wait:** Block until the “download done” event is set (see below).
6. **Cleanup:** Call `server.shutdown()`, `server_close()`, then `shutil.rmtree(tmpdir)`. The same cleanup runs if the process receives SIGINT (e.g. Ctrl+C) or SIGTERM: a signal handler sets the shutdown event so the main thread exits the wait and performs shutdown and temp-dir removal. If removal fails (e.g. permission, NFS, open handle), an error is printed to stderr and the process exits with code 1; otherwise exit 0.

## When is “download done” triggered?

The server uses a custom request handler. When it serves the file:

1. It sends the full response (status 200, headers, body).
2. It flushes the response stream.
3. It then calls the callback that sets the “download done” event.

So **“download done” means “we have finished sending the response for the file”**, not “the client has received every byte.” If the client disconnects mid-transfer (e.g. cancel, slow link, timeout), the server still considers the request done and will shut down and remove the temp copy. The client may end up with a truncated file.

In practice, for a single file and a normal browser download, this is rarely an issue. For scripting or unreliable networks, be aware that the server exits as soon as it has written the response, not when the client has fully received it.

## Single request only

Only one request is intended: the first GET for `/<safe_name>`. After that request is handled:

- The “download done” event is set.
- The main thread wakes, shuts down the server, and removes the temp dir.
- The process exits.

Any further connection attempts will get connection refused (server already closed). A second GET before the first one completes would be served the same file again; in normal use you open the URL once and download.

## Temp directory

- Created with `tempfile.mkdtemp(prefix="termux-serve-")` (so under the system temp dir, e.g. `/tmp` on Linux).
- Contains exactly one file: the copy of your file with the URL-safe name.
- Removed with `shutil.rmtree()` after shutdown. If removal fails (e.g. permission, NFS, open handle), an error is printed to stderr and the process exits with code 1.

## Optional timeout

With `--timeout SECONDS`, the main thread waits at most that long for the first request. If no request is made in time, the server shuts down, the temp dir is removed, and the process exits with code 1. Without `--timeout`, the process waits indefinitely for the first request.

## Signals

SIGINT (e.g. Ctrl+C) and SIGTERM are handled: a handler sets the shutdown event so the main thread exits the wait, runs shutdown and temp-dir removal, then exits. The temp directory is not left behind when you interrupt the process.
