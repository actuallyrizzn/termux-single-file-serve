# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.9] - 2026-03-22

### Added

- **`GET /health`** and **`HEAD /health`**: return `200` with `text/plain` body `ok` on GET (no body on HEAD). These requests do **not** trigger the one-shot shutdown or consume the download; use for probes or readiness checks until the real file is fetched at `/<safe_name>`. The path segment `health` is reserved (see [Behavior](docs/behavior.md)).

## [1.1.8] - 2025-03-01

### Changed

- E2E: capture stderr for assertion diagnostics; comment on GET vs proc.wait ordering; note on test-specific temp dirs for parallel e2e (closes #21, #22, #23).
- conftest: document free_port TOCTOU; remove unused temp_file fixture (closes #24, #25).
- README: "first request for the file" wording (closes #26). Default bind/--bind already documented (closes #27).
- pytest.ini: note for --strict-markers (closes #28).

## [1.1.7] - 2025-03-01

### Changed

- Move `import os` to top in test_handler.py (closes #16).
- Unit test: url_safe_basename("/") returns "download" (closes #17).
- Integration: use os.path.join for served_path; pytest.raises(HTTPError) for 404 (closes #19, #20).

## [1.1.6] - 2025-03-01

### Changed

- Unit tests: handler tests for real-looking paths (query string, encoded chars) (closes #15).

## [1.1.5] - 2025-03-01

### Added

- Handler sends `Connection: close` header (closes #11).

### Changed

- Server: explicit constructor with served_path, safe_name, on_download_done (closes #9).
- Strip query string from request path so e.g. `GET /file.apk?x=1` works (closes #14). Documented in behavior.md.

### Fixed

- In-code comments: daemon thread intent (closes #10), Content-Disposition safe (closes #12), path comparison exact-match (closes #13).

## [1.1.4] - 2025-03-01

### Changed

- Docs: document symlink resolution (os.path.abspath follows symlinks; file served is resolved target) (closes #8).

## [1.1.3] - 2025-03-01

### Changed

- Docs: document whole-file buffering / memory limitation for large files (closes #7).

## [1.1.2] - 2025-03-01

### Changed

- Docs: clarify first GET vs first completed download; server exits after response is sent/flushed, not when client has received all bytes (closes #6). Updated timeout and signals sections in behavior.md.

## [1.1.1] - 2025-03-01

### Fixed

- SIGINT/SIGTERM now trigger shutdown and temp-dir cleanup instead of leaving temp files (closes #5).

## [1.1.0] - 2025-03-01

### Added

- `--timeout SECONDS`: exit with code 1 if no download within the given time; cleanup temp dir on timeout (closes #4).

## [1.0.3] - 2025-03-01

### Fixed

- Report cleanup failure: if temp directory removal fails, print error to stderr and exit with code 1 (closes #3).

## [1.0.2] - 2025-03-01

### Changed

- README: document default bind (127.0.0.1) and `--bind` option (closes #2).

## [1.0.1] - 2025-03-01

### Fixed

- Validate `--port` range (1–65535); exit with error if out of range (closes #1).

## [1.0.0] - 2025-03-01

### Added

- Initial release: single-use HTTP server for one file.
- `--bind` (default 127.0.0.1), `--port` (default 8765), `-q`/`--quiet`.
- URL-safe basename for served file path.
- Full test suite (unit, integration, e2e).
- Documentation in `docs/`.
