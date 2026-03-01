# termux-single-file-serve

Single-use HTTP server for Termux: serve one file over localhost, then cleanup and exit after the first successful download.

## Usage

```bash
python serve.py /path/to/file.apk
# or
python3 serve.py /path/to/your-file.apk
```

- Copies the file into a temporary directory with a URL-safe name.
- Starts a minimal HTTP server and prints the download link (e.g. `http://127.0.0.1:8765/filename.apk`).
- After the first successful download, deletes the temporary copy and shuts down the server.

No dependencies: Python 3 stdlib only.

## Why

On a phone (Termux), you can build or have a file and need to grab it in the browser (e.g. to install an APK). This runs once, serves that one file, then cleans up so there’s no leftover temp files or long-lived server.
