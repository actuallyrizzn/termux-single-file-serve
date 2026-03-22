# Development

## Project layout

```
termux-single-file-serve/
├── serve.py           # Main script (entry point and logic)
├── LICENSE            # AGPL-3.0 for code
├── LICENSE-DOCS       # CC BY-SA 4.0 for non-code content
├── README.md
├── requirements.txt   # No runtime deps (stdlib only)
├── requirements-dev.txt  # pytest for tests
├── pytest.ini         # Test paths and markers
├── docs/              # Documentation (this folder)
└── tests/
    ├── conftest.py    # Pytest fixtures (e.g. free_port)
    ├── unit/          # Unit tests (url_safe_basename, handler)
    ├── integration/  # HTTP server + real request tests
    └── e2e/           # Full flow: subprocess serve.py, GET, cleanup
```

## Virtual environment and tests

Create a venv and install dev dependencies:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Run all tests:

```bash
.venv/bin/pytest tests/ -v
```

Run by category (pytest markers):

```bash
.venv/bin/pytest -m unit -v
.venv/bin/pytest -m integration -v
.venv/bin/pytest -m e2e -v
```

Run by directory:

```bash
.venv/bin/pytest tests/unit/ -v
.venv/bin/pytest tests/integration/ -v
.venv/bin/pytest tests/e2e/ -v
```

## Test markers

Defined in `pytest.ini`:

- **`unit`** — Fast tests, no real I/O (mocked handler, url_safe_basename).
- **`integration`** — Real HTTP server in a thread, real GET request, check response and shutdown.
- **`e2e`** — Run `serve.py` as a subprocess, perform GET, assert process exit and cleanup.

## Code style

The project uses only the standard library; no formatter or linter is configured. Use normal Python style (PEP 8–like). The script is intentionally minimal.

## Adding features

If you add options or change behavior:

1. Update `serve.py` and any affected tests.
2. Update [Usage](usage.md) and [Configuration](configuration.md) (and [Behavior](behavior.md) if semantics change).
3. Run the full test suite.

## Audit and issues

Past audit findings are tracked as GitHub issues. See the [repo issues](https://github.com/actuallyrizzn/termux-single-file-serve/issues) and the short [AUDIT](AUDIT.md) pointer in this folder.
