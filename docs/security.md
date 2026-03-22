# Security

## Bind address: localhost by default

The server **defaults to `127.0.0.1`**. Only connections from the same host are accepted. No one on the network can access the file unless you explicitly use `--bind 0.0.0.0`.

- **`127.0.0.1`:** Loopback only. Intended for “open this URL in a browser on this machine.”
- **`0.0.0.0`:** All interfaces. The file is then reachable at `http://<your-ip>:<port>/<filename>` by anyone who can reach your IP (same LAN, same device, etc.). Use only when you need it (e.g. Android app isolation) and only on networks you trust.

## Termux / Android: is it really localhost?

On Android, the browser and Termux may or may not share the same loopback:

- If they **do** share it, opening `http://127.0.0.1:8765/...` in the phone’s browser will reach the server in Termux. That connection is localhost.
- If they **don’t** (some setups isolate app network namespaces), the browser’s `127.0.0.1` will not reach Termux. In that case you need to bind with `--bind 0.0.0.0` and open `http://<device-ip>:8765/...` in the browser. That is still “this device only” but not strictly loopback; use a trusted network.

## No authentication

The server does not implement authentication or TLS. It is meant for short-lived, local use. Do not use it to expose sensitive files on untrusted networks.

## Path and URL handling

- Only the **exact** path `/<safe_name>` is served (after URL-unquoting). No directory traversal: the safe name is derived from the original basename and contains no slashes; requests with `/` or `%2f` in the path do not match.
- Query strings are stripped before path matching: `/<safe_name>?x=1` is treated the same as `/<safe_name>` and will serve the file.
- The `Content-Disposition` filename is the safe name (alphanumeric, `_`, `-`, `.` only), so header injection from the filename is not an issue.

## File handling

- The **source file** you pass is only read from (for copying). It is not modified or deleted.
- The **copy** is in a temp dir and is deleted after the first successful response (or left behind only if cleanup fails or the process is killed).
- The entire file is read into memory before sending. Very large files may use a lot of memory; the program does not stream.

## Summary

- Default binding is localhost-only.
- Use `0.0.0.0` only when necessary and on trusted networks.
- No auth, no TLS; intended for local, single-use serving.
