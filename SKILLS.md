# Skills & technologies

This document lists the main skills and technologies used in **termux-single-file-serve**. It helps contributors assess fit and gives readers a quick overview of what the project is built with.

## Core

| Area | What we use |
|------|-------------|
| **Language** | Python 3 (stdlib only; no third-party runtime deps) |
| **HTTP** | `http.server` (HTTPServer, SimpleHTTPRequestHandler), request/response handling, headers (Content-Type, Content-Disposition, Connection) |
| **CLI** | `argparse` (positional file, `--port`, `--bind`, `--timeout`, `-q`) |
| **Concurrency** | `threading` (daemon server thread, `Event` for shutdown), `signal` (SIGINT/SIGTERM handlers) |
| **Filesystem** | `tempfile`, `shutil` (copy, rmtree), `os.path`, path sanitization and URL-safe basenames |
| **Text / URLs** | `re` (ASCII-safe basename), `urllib.parse.unquote`, query-string stripping |

## Testing

| Area | What we use |
|------|-------------|
| **Framework** | pytest (markers: `unit`, `integration`, `e2e`) |
| **Unit** | Mock, BytesIO, temp files; testing handler path/query/encoding and main() validation |
| **Integration** | Real HTTP server in process, `urlopen`, free-port fixture, subprocess for timeout behavior |
| **E2E** | Subprocess run of `serve.py`, stdout/stderr capture, real GET request, cleanup checks |

## Concepts

- **Single-use server**: one request, then shutdown and temp cleanup.
- **Binding**: localhost (127.0.0.1) vs all interfaces (0.0.0.0); security tradeoffs.
- **Cleanup on exit**: signal handlers and `Event` so Ctrl+C and SIGTERM still remove temp dirs.
- **Optional timeout**: configurable wait-for-download with exit code 1 and cleanup on timeout.

## Environment

- **Target**: Termux on Android (optional); runs on any POSIX-like system with Python 3.
- **Dev**: venv, `requirements-dev.txt`, pytest; no special IDE or tooling required.

---

*If you’re contributing, familiarity with Python’s stdlib HTTP server and threading is enough to get started; the rest is in the code and [docs](docs/README.md).*
