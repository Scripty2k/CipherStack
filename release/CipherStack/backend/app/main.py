"""Release variant of the CipherStack API.

This module is identical to ``backend/app/main.py`` in the development tree,
with one addition: it also serves the prebuilt single-page frontend from
``frontend/dist`` so the whole product runs on a single port with no Node.js
and no CORS configuration required.

``release/build-release.bat`` copies this file over the generated
``backend/app/main.py`` after copying the rest of the backend sources.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .models import ErrorDetail, ErrorResponse, ScanRequest, ScanResponse
from .scanner import TooManyRedirectsError, build_client, scan
from .security import BlockedTargetError, ResolutionError

DEFAULT_CORS_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")

# backend/app/main.py -> backend/app -> backend -> <release root>
RELEASE_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = RELEASE_ROOT / "frontend" / "dist"
STATIC_INDEX = STATIC_DIR / "index.html"


def _cors_origins() -> list[str]:
    raw = os.getenv("CIPHERSTACK_CORS_ORIGINS", "")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or list(DEFAULT_CORS_ORIGINS)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http_client = build_client()
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(
    title="CipherStack API",
    version="1.0.0",
    description="HTTP security header and misconfiguration auditor.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    payload = ErrorResponse(detail=ErrorDetail(code=code, message=message))
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@app.exception_handler(BlockedTargetError)
async def handle_blocked_target(_: Request, exc: BlockedTargetError) -> JSONResponse:
    return _error(400, "blocked_target", exc.message)


@app.exception_handler(ResolutionError)
async def handle_resolution_error(_: Request, exc: ResolutionError) -> JSONResponse:
    return _error(502, "resolution_failed", exc.message)


@app.exception_handler(TooManyRedirectsError)
async def handle_redirect_loop(_: Request, exc: TooManyRedirectsError) -> JSONResponse:
    return _error(400, "too_many_redirects", exc.message)


@app.exception_handler(httpx.TimeoutException)
async def handle_timeout(_: Request, __: httpx.TimeoutException) -> JSONResponse:
    return _error(504, "timeout", "The target did not respond within the time limit.")


@app.exception_handler(httpx.ConnectError)
async def handle_connect_error(_: Request, __: httpx.ConnectError) -> JSONResponse:
    return _error(502, "connection_failed", "Could not establish a connection to the target.")


@app.exception_handler(httpx.HTTPError)
async def handle_http_error(_: Request, exc: httpx.HTTPError) -> JSONResponse:
    return _error(502, "request_failed", f"Request to the target failed: {exc.__class__.__name__}.")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/scan", response_model=ScanResponse)
async def create_scan(payload: ScanRequest) -> ScanResponse:
    return await scan(payload.url)


# ---------------------------------------------------------------------------
# Static single-page app hosting
# ---------------------------------------------------------------------------
# The routes below are registered last so that /api/* and /docs always win.
# If the frontend was never built, the API still works and the root path
# returns a helpful message instead of a bare 404.

if STATIC_INDEX.is_file():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        """Serve a real file when it exists, otherwise fall back to index.html."""
        if full_path:
            candidate = (STATIC_DIR / full_path).resolve()
            if candidate.is_file() and STATIC_DIR in candidate.parents:
                return FileResponse(candidate)
        return FileResponse(STATIC_INDEX)

else:

    @app.get("/", include_in_schema=False)
    async def missing_frontend() -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "detail": {
                    "code": "frontend_missing",
                    "message": (
                        "The frontend build was not found at frontend/dist. "
                        "Run 'npm install && npm run build' inside the frontend "
                        "folder, then restart the launcher."
                    ),
                }
            },
        )
