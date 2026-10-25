from __future__ import annotations

import pytest

from app.security import BlockedTargetError, normalize_url, validate_target


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com",
        "gopher://example.com",
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
    ],
)
async def test_disallowed_schemes_are_rejected(url: str) -> None:
    with pytest.raises(BlockedTargetError):
        await validate_target(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost",
        "http://localhost:8000/admin",
        "http://app.localhost",
        "http://127.0.0.1",
        "http://127.0.0.1:8080",
        "http://10.0.0.1",
        "http://192.168.1.1",
        "http://172.16.0.5",
        "http://169.254.169.254/latest/meta-data/",
        "http://0.0.0.0",
        "http://[::1]",
        "http://[fe80::1]",
        "http://[fc00::1]",
    ],
)
async def test_private_and_reserved_addresses_are_rejected(url: str) -> None:
    with pytest.raises(BlockedTargetError):
        await validate_target(url)


async def test_public_literal_ip_is_allowed() -> None:
    target = await validate_target("https://93.184.216.34")
    assert target.host == "93.184.216.34"
    assert target.port == 443
    assert target.addresses == ("93.184.216.34",)


async def test_public_hostname_is_resolved_and_allowed() -> None:
    target = await validate_target("https://example.com")
    assert target.scheme == "https"
    assert target.host == "example.com"
    assert target.addresses


async def test_missing_hostname_is_rejected() -> None:
    with pytest.raises(BlockedTargetError):
        await validate_target("https://")


async def test_invalid_port_is_rejected() -> None:
    with pytest.raises(BlockedTargetError):
        await validate_target("https://example.com:notaport")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("example.com", "https://example.com"),
        ("  example.com  ", "https://example.com"),
        ("http://example.com", "http://example.com"),
        ("https://example.com/path?q=1", "https://example.com/path?q=1"),
    ],
)
def test_normalize_url(raw: str, expected: str) -> None:
    assert normalize_url(raw) == expected


async def test_default_port_follows_scheme() -> None:
    http_target = await validate_target("http://example.com")
    assert http_target.port == 80
