# Publishing CipherStack as a GitHub release

The `release/CipherStack` folder is a ready-to-ship, self-contained build. Users extract the ZIP, double-click `Start CipherStack.bat`, and the site runs locally.

## 1. Rebuild (only if you changed the source)

```bat
release\build-release.bat
```

This copies the backend and frontend sources into `release\CipherStack`, builds the frontend into `release\CipherStack\frontend\dist`, and removes `node_modules` so the archive stays small.

## 2. Zip it

Right-click `release\CipherStack` → **Send to** → **Compressed (zipped) folder**, and rename the result to `CipherStack-1.0.0-windows.zip`.

Or from a terminal:

```bat
powershell -NoProfile -Command "Compress-Archive -Path 'release\CipherStack' -DestinationPath 'release\CipherStack-1.0.0-windows.zip' -Force"
```

> Zip the **`CipherStack` folder itself**, not its contents, so users get a single top-level folder after extracting.

## 3. Create the GitHub release

1. Push your changes and tag the commit:

   ```bat
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. On GitHub, open **Releases** → **Draft a new release**.
3. Choose the tag `v1.0.0`, title it `CipherStack 1.0.0`.
4. Attach `release\CipherStack-1.0.0-windows.zip` under **Attach binaries**.
5. Paste the short description below, then **Publish release**.

### Suggested release notes

```markdown
## CipherStack 1.0.0 — local release

Run the full CipherStack site on your own machine. No Node.js, no Docker, no server.

### Quick start
1. Download `CipherStack-1.0.0-windows.zip` and extract it.
2. Double-click `Start CipherStack.bat`.
3. Your browser opens at http://127.0.0.1:8000.

The first run creates a private Python virtual environment and installs the
dependencies (about 30 seconds, needs internet). Later runs start instantly.

### Requirements
- Windows 10/11
- Python 3.11, 3.12 or 3.13 (3.14 is not supported yet)

### What it does
- Grades six security headers from A+ to F with weighted scoring.
- Probes `/.git/HEAD`, `/robots.txt`, `/.env` and `/sitemap.xml`.
- Blocks private, loopback and reserved targets (SSRF protection).
- Stateless: nothing is stored.
```

## 4. Optional: macOS / Linux archive

The same folder works on macOS and Linux via `start.sh`. If you want a separate asset, zip it on a Unix machine so the executable bit on `start.sh` is preserved:

```bash
cd release && zip -r CipherStack-1.0.0-unix.zip CipherStack
```

## Notes

- `release/CipherStack/.gitignore` keeps `.venv`, `node_modules` and logs out of version control, but **`frontend/dist` is intentionally shipped** — it is the prebuilt UI.
- If you add a new Python module under `backend/app`, `build-release.bat` picks it up automatically (`*.py` glob).
- If you add a new frontend source file, it is copied by the recursive `xcopy` of `frontend/src`.
- `release/templates/` holds the two release-only files that are **not** part of the dev tree:
  - `run.py` — the launcher entry point (port picking, browser opening, uvicorn boot).
  - `main.py` — the dev `backend/app/main.py` plus static SPA hosting from `frontend/dist`.

  `build-release.bat` copies both into the generated release. If you change the API in `backend/app/main.py`, mirror the change in `release/templates/main.py`, otherwise the release keeps serving the old API.
- `build-release.bat` only wipes `release/CipherStack/backend` and `release/CipherStack/frontend`. The launchers, `README.md`, `.gitignore` and `start.sh` at the release root are hand-written and survive a rebuild.
- The release was verified end-to-end: `/` serves the SPA, `/assets/*` serves the hashed bundles, `/api/health` returns `{"status":"ok"}`, `/api/scan` returns a graded report, deep routes fall back to `index.html`, `/docs` works, and private targets are rejected with HTTP 400.
