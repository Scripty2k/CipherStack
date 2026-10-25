# CipherStack — Local Release

CipherStack is a lightweight security scanner that analyzes HTTP response headers, evaluates exposed sensitive endpoints, and provides instant security scoring with actionable remediation tips.

This folder is a **self-contained local release**. It runs the whole site — API and web UI — on your own computer. Nothing is uploaded anywhere, and no data is stored.

---

## Quick start (Windows)

1. Extract the whole ZIP archive to a folder of your choice.
2. Double-click **`Start CipherStack.bat`**.
3. Wait for the first-run setup to finish (about 30 seconds), then your browser opens at `http://127.0.0.1:8000`.

To stop the app, close the console window or press `Ctrl+C` in it.

> **First run needs internet access** to download the Python dependencies. Every run after that starts in a couple of seconds.

### macOS / Linux

```bash
chmod +x start.sh
./start.sh
```

Then open `http://127.0.0.1:8000`.

---

## Requirements

| Requirement | Notes |
| --- | --- |
| **Python 3.11, 3.12 or 3.13** | Required. Python 3.14 is **not** supported yet — one dependency has no prebuilt installer for it. |
| Internet access | Needed on first run (dependency download) and for scanning targets. |
| Node.js | **Not required.** The frontend is already built and bundled. |

If Python is missing, install it from <https://www.python.org/downloads/> and tick **“Add python.exe to PATH”** during setup.

The launcher creates a private `.venv` folder next to itself, so your system Python is never modified. Delete `.venv` at any time to force a clean reinstall.

---

## What the launcher does

1. Finds a supported Python interpreter. It tries `py -3.13`, `py -3.12`, `py -3.11`, then `python`, then `python3`, and finally `uv`. A candidate only counts if it can **actually create a virtual environment**, so a `py` launcher that merely reports a version (for example a uv shim, or the Microsoft Store stub) is skipped automatically.
2. Creates `.venv` and installs [`backend/requirements.txt`](backend/requirements.txt) into it. If the interpreter produced a venv without `pip` (which `uv venv` does), pip is bootstrapped with `ensurepip` first.
3. Starts [`backend/run.py`](backend/run.py), which serves the API **and** the prebuilt UI from [`frontend/dist`](frontend/dist) on a single port.
4. Opens your default browser.

If port `8000` is already taken, the launcher automatically picks the next free port and prints the URL it used.

---

## Using the app

Enter a hostname such as `github.com` and press **Scan**. You get:

- a letter grade from **A+** to **F** and a weighted score out of 100,
- a per-header verdict (`Pass`, `Warning`, `Missing`) with a remediation tip,
- the results of probes against `/.git/HEAD`, `/robots.txt`, `/.env` and `/sitemap.xml`.

Only **public** hosts can be scanned. Private, loopback, link-local and reserved addresses are blocked on purpose (SSRF protection).

---

## Folder layout

```
CipherStack/
├── Start CipherStack.bat            # Windows launcher (opens a browser)
├── Start CipherStack (no browser).bat
├── start.sh                         # macOS / Linux launcher
├── backend/
│   ├── run.py                       # launcher entry point
│   ├── requirements.txt
│   └── app/                         # FastAPI app, scanner, rules, scoring
└── frontend/
    ├── dist/                        # prebuilt UI served by the backend
    └── src/                         # UI source (only needed to rebuild)
```

---

## Troubleshooting

**“No usable Python 3.11 - 3.13 interpreter was found.”**
Install Python 3.11–3.13 from <https://www.python.org/downloads/> and tick **“Add python.exe to PATH”**. Verify with `py -3.12 -m venv testvenv` — if that command fails, the `py` launcher cannot build virtual environments and is skipped by design.

If you use **uv**, run `uv python install 3.12` and the launcher will pick it up automatically.

**The launcher says “Trying Python 3.13 via the py launcher” and then moves on.**
That is expected on machines where `py` is a shim (uv, or the Microsoft Store alias) that reports a version but cannot create a venv. The launcher tests each candidate by actually building `.venv` and skips the ones that fail.

**“Installing dependencies failed.”**
Check your internet connection or proxy settings, then delete the `.venv` folder and run the launcher again.

**The browser does not open.**
Use `Start CipherStack (no browser).bat` and open the printed URL manually.

**“Could not reach the CipherStack API.”**
The backend process stopped. Check the console window for the error and restart the launcher.

**Port already in use.**
Nothing to do — the launcher picks the next free port and prints it.

---

## Rebuilding the frontend (optional)

Only needed if you change the UI. Requires Node.js 18+.

```bash
cd frontend
npm install
npm run build
```

The build output lands in `frontend/dist` and is picked up automatically on the next start.

---

## API

The API is available at the same origin as the UI:

- `POST /api/scan` — body `{ "url": "example.com" }`
- `GET /api/health` — `{ "status": "ok" }`
- Interactive docs: `http://127.0.0.1:8000/docs`

---

## License

See the `LICENSE` file in the project repository.
