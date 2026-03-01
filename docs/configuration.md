# Configuration

The program is configured only via command-line options. There are no config files or environment variables.

## Bind address (`--bind`)

- **Default:** `127.0.0.1` (localhost only). Only connections from the same machine are accepted.
- **`0.0.0.0`:** Listen on all interfaces. Other devices on the same network (or other apps on the same device, depending on the OS) can connect using the machine’s IP address.

Use `0.0.0.0` when:

- You’re in Termux and the phone’s browser can’t reach `127.0.0.1` (e.g. because of Android app isolation). In that case, open `http://<phone-ip>:<port>/<filename>` in the browser.
- You want to download the file from another computer on the same LAN.

Security note: binding to `0.0.0.0` makes the file reachable by anyone who can reach your IP and port. Use only on trusted networks. See [Security](security.md).

## Timeout (`--timeout`)

- **Default:** None (wait indefinitely for the first request for the file).
- If set to a positive number of seconds (e.g. `--timeout 60`), the server will exit if no successful download has occurred within that time. On timeout, the temp directory is removed (if possible), the server shuts down, and the process exits with code 1. Useful for scripts or unattended use to avoid hanging forever and leaving temp files on disk.

## Port (`--port`)

- **Default:** `8765`.
- Any valid TCP port number (1–65535) can be used. Ports below 1024 may require privilege on some systems.
- No check is done for port availability before starting; if the port is in use, the server will fail at bind and exit.

## URL-safe filename

The file you pass is copied into a temp directory. Its **basename** is sanitized for use in the URL and in the `Content-Disposition` header:

- Spaces → underscores (`_`).
- Any character that is not alphanumeric, `-`, `.`, or `_` (ASCII) → `_`.
- Repeated underscores are collapsed; leading/trailing underscores are stripped.
- If the result is empty (e.g. the name was only spaces or invalid chars), the name `download` is used.

Examples:

| Input path (basename) | URL path |
|------------------------|----------|
| `app-release.apk`     | `app-release.apk` |
| `my file (1).apk`      | `my_file_1_.apk`   |
| `doc.pdf`              | `doc.pdf`          |
| `a%b#c.d`              | `a_b_c.d`          |

The **original file** is never renamed or moved; only the **copy** in the temp dir uses this name. The download URL is:

`http://<bind>:<port>/<safe_name>`

## No config file

All behavior is controlled by the options (`--port`, `--bind`, `--quiet`, `--timeout`) and the single positional file argument. There is no support for config files or env vars.
