# termux-single-file-serve — Documentation

Full documentation for the project. Start here or jump to a section below.

## Documentation index

| Document | Description |
|----------|-------------|
| [Overview](overview.md) | What the project is, goals, and when to use it |
| [Installation](installation.md) | Requirements and how to run (no install step) |
| [Usage](usage.md) | Command-line reference, options, and examples |
| [Configuration](configuration.md) | Bind address, port, URL-safe filenames |
| [Behavior](behavior.md) | How single-use serving works: copy, serve, cleanup |
| [Security](security.md) | Localhost vs all interfaces, Termux/Android notes |
| [Development](development.md) | Venv, tests, project layout, contributing |
| [API reference](reference.md) | Module and function reference |
| [Troubleshooting](troubleshooting.md) | Common problems and fixes |
| [License](LICENSE) | Non-code content license (CC BY-SA 4.0); code is AGPL-3.0 (see repo root [LICENSE](../LICENSE)) |

## Quick start

```bash
python3 serve.py /path/to/your-file.apk
```

Then open the printed URL in your browser to download. The server exits after the first request for the file (see [Behavior](behavior.md)). See [Usage](usage.md) for all options.
