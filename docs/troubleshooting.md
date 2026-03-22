# Troubleshooting

## “Error: not a file”

You passed a path that is not a regular file (e.g. a directory, or a missing path). Use a path to an existing file. Symlinks are followed to the target file.

## Port in use / “Address already in use”

Another process is already using the port (default 8765). Either:

- Stop that process, or
- Use a different port: `--port 9000` (or any free port).

The program does not check if the port is free before binding; you’ll see a normal OS “address already in use” error.

## Can’t open the URL in the browser (Termux / Android)

- **If you use the default `127.0.0.1`:** On some Android setups, the browser and Termux don’t share the same loopback, so `http://127.0.0.1:8765/...` never reaches the server. Try:
  - Run with `--bind 0.0.0.0`.
  - Find your device’s IP (e.g. in WiFi settings or `termux-ifconfig` if available).
  - In the browser, open `http://<device-ip>:8765/<filename>`.
- Make sure you’re using the exact URL printed (including the filename segment). Query strings (e.g. `?x=1`) are not supported and will result in 404.

## 404 when opening the URL

- The path must be exactly `/<safe_name>` (the URL-safe filename). For example, if the program printed `http://127.0.0.1:8765/my_file.apk`, use that full URL. Requests to `/` or `/other` return 404.
- If you added a query string (e.g. `?foo=1`), the server does not strip it; the path won’t match and you’ll get 404. Use the URL without query string.

## Server never exits / temp dir left behind

- The server exits only after it has **sent** the response for the file (see [Behavior](behavior.md)). If no request is ever made, it will run until you stop it (Ctrl+C).
- If you press Ctrl+C or kill the process, cleanup (removing the temp dir) may not run. Temp dirs are under the system temp directory with prefix `termux-serve-`; you can remove them manually if needed.
- If cleanup fails for another reason (e.g. permission), the program still exits 0 and does not report the failure; the temp dir may remain.

## Large file / out of memory

The entire file is read into memory and then sent. Very large files can cause high memory use or OOM. The program does not stream. For very large files, consider another tool or splitting the file.

## Tests fail (e.g. “address already in use”, “Expected URL in stdout”)

- **Port:** Tests use a “free port” fixture that binds to `0`, then closes the socket. Another process could take that port before the test binds. Run tests in an environment with few other services, or re-run.
- **E2E:** The e2e test runs `serve.py` in a subprocess and expects the URL on stdout. It uses Python’s `-u` for unbuffered output. If the test fails with “Expected URL in stdout”, check that the subprocess actually started (e.g. no “file not found” for `serve.py`); the test prints stderr on failure.
- **Leftover temp dirs:** E2E cleans up `termux-serve-*` dirs before and after. If a previous run left one behind and the new run’s subprocess didn’t clean up, the “no leftover temp dirs” assertion can fail. Re-running often passes; you can also manually remove `/tmp/termux-serve-*` (or your OS temp dir equivalent).

## More help

- Usage and options: [Usage](usage.md)
- How the server behaves: [Behavior](behavior.md)
- Security and binding: [Security](security.md)
- Development and tests: [Development](development.md)
