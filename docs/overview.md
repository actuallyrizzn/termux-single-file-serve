# Overview

## What it is

**termux-single-file-serve** is a minimal, single-use HTTP server. You give it one file; it copies that file into a temporary directory, serves it over HTTP on a configurable address and port, and prints a download URL. As soon as the first GET request for that file is responded to (response sent and flushed), the server deletes the temporary copy and exits. See [Behavior](behavior.md) for the exact semantics (e.g. client disconnecting mid-transfer).

- **Single use:** One file, one download, then shutdown. No long-lived server or leftover temp files.
- **No dependencies:** Python 3 standard library only.
- **Designed for Termux/Android:** Handy when you have a file in Termux (e.g. a built APK) and want to open it in the phone’s browser or another app on the same device.

## Goals

1. **Simple:** One command, one file, one URL. No config files or daemons.
2. **Safe by default:** Binds to localhost only unless you opt in to `--bind 0.0.0.0`.
3. **Clean:** Temp copy and server are removed after the first successful request.

## When to use it

- You’re in Termux (or any terminal) and have a file you want to download in a browser on the same machine (e.g. to install an APK).
- You want a one-off way to serve one file without leaving a process or temp dir behind.
- You need a scriptable “serve this file once” step in a pipeline.

## When not to use it

- Serving many files or a directory: use a normal HTTP server or `python3 -m http.server`.
- Long-lived or multi-request serving: this tool exits after the first request for the file.
- Production or multi-user use: this is a minimal, local, single-file helper.

## Related docs

- [Installation](installation.md) — what you need to run it
- [Usage](usage.md) — command-line options and examples
- [Behavior](behavior.md) — exact flow and “first request” semantics
