from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import urljoin

import httpx

from .models import ScanResponse
from .probes import probe_endpoints
from .rules import evaluate_headers
from .scoring import compute_grade
from .security import (
    MAX_BODY_BYTES,
    MAX_REDIRECTS,
    REQUEST_TIMEOUT,
    USER_AGENT,
    ValidatedTarget,
    validate_target,
)


class TooManyRedirectsError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def build_client(transport: httpx.AsyncBaseTransport | None = None) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        follow_redirects=False,
        timeout=httpx.Timeout(REQUEST_TIMEOUT),
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
        transport=transport,
    )


async def _fetch(
    client: httpx.AsyncClient,
    target: ValidatedTarget,
) -> tuple[httpx.Response, list[str]]:
    current = target
    chain: list[str] = []

    for _ in range(MAX_REDIRECTS + 1):
        request = client.build_request("GET", current.url)
        response = await client.send(request, stream=True)
        try:
            async for _chunk in response.aiter_bytes(chunk_size=8192):
                if len(_chunk) > MAX_BODY_BYTES:
                    break
        finally:
            await response.aclose()

        location = response.headers.get("location")
        if response.status_code not in {301, 302, 303, 307, 308} or not location:
            return response, chain

        chain.append(current.url)
        next_url = urljoin(current.url, location)
        current = await validate_target(next_url)

    raise TooManyRedirectsError(f"Target exceeded the {MAX_REDIRECTS} redirect limit")


async def scan(raw_url: str, transport: httpx.AsyncBaseTransport | None = None) -> ScanResponse:
    target = await validate_target(raw_url)

    async with build_client(transport) as client:
        response, chain = await _fetch(client, target)
        final_url = str(response.url)
        endpoints = await probe_endpoints(client, final_url)

    findings = evaluate_headers(response.headers)
    score, grade, flags = compute_grade(findings, endpoints)

    return ScanResponse(
        target=target.url,
        final_url=final_url,
        status_code=response.status_code,
        grade=grade,
        score=score,
        findings=findings,
        endpoints=endpoints,
        redirects=chain,
        flags=flags,
        scanned_at=datetime.now(UTC),
    )
