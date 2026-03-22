# Usage

## Basic usage

```bash
python3 serve.py <file>
```

Example:

```bash
python3 serve.py ./app-release.apk
```

The program will:

1. Copy the file to a temporary directory with a URL-safe name.
2. Start an HTTP server (default: `127.0.0.1:8765`).
3. Print the download URL.
4. Wait for the first GET request for that file (see [Behavior](behavior.md) for when “done” is triggered).
5. After the response is sent, delete the temp copy and exit.

While waiting, you can probe **`GET http://<host>:<port>/health`** or **`HEAD .../health`** as often as you like: they return `200` and plain text `ok` (body on GET only) and **do not** end the server or count as the file download. See [Behavior — Health endpoint](behavior.md#health-endpoint).

## Command-line options

| Option | Short | Default | Description |
|--------|--------|--------|-------------|
| `--port` | — | `8765` | Port number for the HTTP server. |
| `--bind` | — | `127.0.0.1` | Address to bind to. Use `0.0.0.0` to listen on all interfaces (e.g. to reach the server from another app on the same device). |
| `--timeout` | — | none | If set (e.g. `--timeout 60`), exit with code 1 if no download within that many seconds. Temp dir is cleaned up on timeout. |
| `--quiet` | `-q` | off | Print only the download URL (one line), no extra messages. Useful for scripting. |

Positional argument:

- **`file`** — Path to the file to serve. Must be a regular file (not a directory). Symlinks are followed to the target file.

## Examples

**Serve an APK on default host and port:**

```bash
python3 serve.py /data/data/com.termux/files/home/build/app.apk
```

**Use a different port (e.g. 9000):**

```bash
python3 serve.py ./file.zip --port 9000
```

**Bind on all interfaces** (so another app on the same phone can download via the device’s IP):

```bash
python3 serve.py ./file.apk --bind 0.0.0.0
```

Output will still show a localhost URL and a note like “or http://<this-device-ip>:8765/... from another app/device”.

**Quiet mode** (only the URL on stdout, for scripts):

```bash
python3 serve.py ./file.apk -q
# Output: http://127.0.0.1:8765/file.apk
```

**Combined:**

```bash
python3 serve.py ./doc.pdf --bind 0.0.0.0 --port 8080 -q
```

**Health check** (server stays up until the real file is downloaded):

```bash
curl -sf http://127.0.0.1:8765/health
# ok
```

## Output

**Normal (non-quiet):**

```
Download at:
  http://127.0.0.1:8765/filename.apk
(Server exits after first request for the file.)
```

When `--bind 0.0.0.0`:

```
Download at:
  http://127.0.0.1:8765/filename.apk (or http://<this-device-ip>:8765/filename.apk from another app/device)
(Server exits after first request for the file.)
```

**Quiet (`-q`):** Only the URL line (e.g. `http://127.0.0.1:8765/filename.apk`).

## Exit codes

- **0** — Server ran and shut down after a download (or after serving the file once).
- **1** — Error: file not found, not a regular file, or copy failed. A message is printed to stderr.

## See also

- [Configuration](configuration.md) — Details on `--bind`, `--port`, and URL-safe names
- [Behavior](behavior.md) — First GET vs completed transfer; when the server exits
