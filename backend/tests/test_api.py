from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.models import Grade, Verdict
from app.scanner import scan

SECURE_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'nonce-abc123'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), geolocation=()",
}


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/":
        return httpx.Response(200, headers=SECURE_HEADERS, text="<html></html>")
    if request.url.path == "/.git/HEAD":
        return httpx.Response(200, text="ref: refs/heads/main")
    return httpx.Response(404, text="not found")


def _bare_handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/":
        return httpx.Response(200, text="<html></html>")
    return httpx.Response(404)


def _redirect_handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/":
        return httpx.Response(301, headers={"location": "https://example.com/home"})
    if request.url.path == "/home":
        return httpx.Response(200, headers=SECURE_HEADERS, text="<html></html>")
    return httpx.Response(404)


async def test_scan_reports_secure_target() -> None:
    result = await scan("https://example.com", transport=httpx.MockTransport(_handler))
    assert result.status_code == 200
    assert result.grade is Grade.F
    assert result.score == 100.0
    assert all(finding.verdict is Verdict.PASS for finding in result.findings)
    assert any(endpoint.path == "/.git/HEAD" and endpoint.exposed for endpoint in result.endpoints)
    assert result.flags


async def test_scan_reports_missing_headers() -> None:
    result = await scan("https://example.com", transport=httpx.MockTransport(_bare_handler))
    assert result.score == 0.0
    assert result.grade is Grade.F
    assert all(finding.verdict is Verdict.MISSING for finding in result.findings)


async def test_scan_follows_redirects_and_records_chain() -> None:
    result = await scan("https://example.com", transport=httpx.MockTransport(_redirect_handler))
    assert result.final_url == "https://example.com/home"
    assert result.redirects == ["https://example.com"]


@pytest.fixture
def client() -> TestClient:
    with TestClient(main.app) as test_client:
        yield test_client


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_scan_endpoint_rejects_blocked_target(client: TestClient) -> None:
    response = client.post("/api/scan", json={"url": "http://127.0.0.1"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "blocked_target"


def test_scan_endpoint_rejects_empty_url(client: TestClient) -> None:
    response = client.post("/api/scan", json={"url": "   "})
    assert response.status_code == 422


def test_scan_endpoint_returns_result(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_scan(url: str):
        return await scan(url, transport=httpx.MockTransport(_handler))

    monkeypatch.setattr(main, "scan", fake_scan)
    response = client.post("/api/scan", json={"url": "https://example.com"})
    assert response.status_code == 200
    body = response.json()
    assert body["grade"] == "F"
    assert body["score"] == 100.0
    assert len(body["findings"]) == 6
    assert len(body["endpoints"]) == 4
