# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
