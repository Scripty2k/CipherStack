from __future__ import annotations

import asyncio
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx

from .models import EndpointFinding, Severity

PROBE_PATHS: tuple[str, ...] = ("/.git/HEAD", "/robots.txt", "/.env", "/sitemap.xml")

_NOT_FOUND_STATUSES = frozenset({401, 403, 404, 410})


@dataclass(frozen=True, slots=True)
class ProbeSpec:
    path: str
    severity: Severity
    exposed_note: str
    safe_note: str


_PROBE_SPECS: tuple[ProbeSpec, ...] = (
    ProbeSpec(
        path="/.git/HEAD",
        severity=Severity.CRITICAL,
        exposed_note="Git metadata is publicly readable, exposing full source history.",
        safe_note="Git metadata is not publicly accessible.",
    ),
    ProbeSpec(
        path="/robots.txt",
        severity=Severity.INFO,
        exposed_note="robots.txt is present and may reveal internal paths.",
        safe_note="No robots.txt was returned.",
    ),
    ProbeSpec(
        path="/.env",
        severity=Severity.HIGH,
        exposed_note="Environment file is publicly readable and may contain credentials.",
        safe_note="No environment file was returned.",
    ),
    ProbeSpec(
        path="/sitemap.xml",
        severity=Severity.INFO,
        exposed_note="sitemap.xml is present and enumerates site URLs.",
        safe_note="No sitemap.xml was returned.",
    ),
)


def _classify(spec: ProbeSpec, status_code: int | None) -> EndpointFinding:
    if status_code is None:
        return EndpointFinding(
            path=spec.path,
            status_code=None,
            exposed=False,
            severity=Severity.NONE,
            note="Probe failed before a response was received.",
        )

    if status_code in _NOT_FOUND_STATUSES:
        return EndpointFinding(
            path=spec.path,
            status_code=status_code,
            exposed=False,
            severity=Severity.NONE,
            note=spec.safe_note,
        )

    if 200 <= status_code < 300:
        return EndpointFinding(
            path=spec.path,
            status_code=status_code,
            exposed=True,
            severity=spec.severity,
            note=spec.exposed_note,
        )

    return EndpointFinding(
        path=spec.path,
        status_code=status_code,
        exposed=False,
        severity=Severity.NONE,
        note=f"Responded with HTTP {status_code}; no content disclosed.",
    )


async def _probe(client: httpx.AsyncClient, base_url: str, spec: ProbeSpec) -> EndpointFinding:
    target = urljoin(base_url, spec.path.lstrip("/"))
    try:
        response = await client.get(target)
    except httpx.HTTPError:
        return _classify(spec, None)
    return _classify(spec, response.status_code)


async def probe_endpoints(client: httpx.AsyncClient, base_url: str) -> list[EndpointFinding]:
    return list(
        await asyncio.gather(*(_probe(client, base_url, spec) for spec in _PROBE_SPECS))
    )
