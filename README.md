# termux-single-file-serve

**Code:** AGPL-3.0 — see [LICENSE](LICENSE).  
**Non-code content (docs, README, etc.):** CC BY-SA 4.0 — see [LICENSE-DOCS](LICENSE-DOCS).

Single-use HTTP server for Termux: serve one file over localhost, then cleanup and exit after the first request for the file.

- **[Skills & technologies](SKILLS.md)** — What this project is built with and what you need to contribute.

## Documentation

Full documentation is in the **[docs](docs/)** folder:

- **[Documentation index](docs/README.md)** — Start here; links to all docs.
- [Overview](docs/overview.md) — What it is, when to use it.
- [Installation](docs/installation.md) — Requirements, no install step.
- [Usage](docs/usage.md) — Command-line options and examples.
- [Configuration](docs/configuration.md) — Bind address, port, URL-safe names.
- [Behavior](docs/behavior.md) — How single-use serving and cleanup work.
- [Security](docs/security.md) — Localhost vs 0.0.0.0, Termux/Android notes.
- [Development](docs/development.md) — Venv, tests, project layout.
- [API reference](docs/reference.md) — Module and function reference.
- [Troubleshooting](docs/troubleshooting.md) — Common problems and fixes.

## Usage

```bash
python serve.py /path/to/file.apk
# or
python3 serve.py /path/to/your-file.apk
```

- Copies the file into a temporary directory with a URL-safe name.
- Starts a minimal HTTP server (default: bind `127.0.0.1`, port `8765`) and prints the download link (e.g. `http://127.0.0.1:8765/filename.apk`). The server is localhost-only by default; use `--bind 0.0.0.0` to listen on all interfaces (e.g. when the browser can’t reach loopback, such as on some Android setups).
- Optional **`GET /health`** / **`HEAD /health`**: return `200` and do not shut down the server (for probes until you fetch the file URL).
- After the first **file** GET, deletes the temporary copy and shuts down the server.

No dependencies: Python 3 stdlib only.

## Development and testing

Create a venv, install dev deps, and run the test suite:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest tests/ -v
```

- **Unit:** `pytest tests/unit/ -v` or `pytest -m unit -v`
- **Integration:** `pytest tests/integration/ -v` or `pytest -m integration -v`
- **E2E:** `pytest tests/e2e/ -v` or `pytest -m e2e -v`

## Why

On a phone (Termux), you can build or have a file and need to grab it in the browser (e.g. to install an APK). This runs once, serves that one file, then cleans up so there’s no leftover temp files or long-lived server.
