# Installation

There is no separate install step. The program is a single Python script and runs with the standard library only.

## Requirements

- **Python 3.6+** (tested on 3.13). The script uses only the standard library:
  - `argparse`, `os`, `re`, `shutil`, `sys`, `tempfile`, `threading`
  - `http.server` (HTTPServer, SimpleHTTPRequestHandler)
  - `urllib.parse` (unquote)

No pip packages or system dependencies are required to run `serve.py`.

## Getting the project

Clone the repository (or download the script and use it standalone):

```bash
git clone https://github.com/actuallyrizzn/termux-single-file-serve.git
cd termux-single-file-serve
```

## Running

From the project directory:

```bash
python3 serve.py /path/to/your-file
```

Or from anywhere, if you have the script on your `PATH`:

```bash
python3 /path/to/termux-single-file-serve/serve.py /path/to/your-file
```

You can also make `serve.py` executable and run it directly (shebang is `#!/usr/bin/env python3`):

```bash
chmod +x serve.py
./serve.py /path/to/your-file
```

## Optional: development setup

To run the test suite you need a virtual environment and pytest. See [Development](development.md) for:

- Creating a venv
- Installing `requirements-dev.txt` (pytest)
- Running unit, integration, and e2e tests

This is only required for contributing or running tests, not for normal use.
