# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
