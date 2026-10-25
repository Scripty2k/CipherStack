from __future__ import annotations

import asyncio
import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlsplit

ALLOWED_SCHEMES = frozenset({"http", "https"})
MAX_REDIRECTS = 3
REQUEST_TIMEOUT = 10.0
MAX_BODY_BYTES = 262_144
USER_AGENT = "CipherStack/1.0 (+https://github.com/BeatStats/CipherStack)"

_BLOCKED_NETWORKS = tuple(
    ipaddress.ip_network(network)
    for network in (
        "0.0.0.0/8",
        "10.0.0.0/8",
        "100.64.0.0/10",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "172.16.0.0/12",
        "192.0.0.0/24",
        "192.0.2.0/24",
        "192.168.0.0/16",
        "198.18.0.0/15",
        "198.51.100.0/24",
        "203.0.113.0/24",
        "224.0.0.0/4",
        "240.0.0.0/4",
        "::/128",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
        "ff00::/8",
    )
)


class BlockedTargetError(ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ResolutionError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass(frozen=True, slots=True)
class ValidatedTarget:
    url: str
    scheme: str
    host: str
    port: int
    addresses: tuple[str, ...]


def _is_blocked_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    ):
        return True
    return any(address in network for network in _BLOCKED_NETWORKS if network.version == address.version)


def _parse_literal_ip(host: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        return None


def _normalize_host(host: str) -> str:
    return host.strip("[]").lower()


async def _resolve(host: str, port: int) -> tuple[str, ...]:
    loop = asyncio.get_running_loop()
    try:
        infos = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ResolutionError(f"Could not resolve host '{host}'") from exc

    addresses = {info[4][0] for info in infos}
    if not addresses:
        raise ResolutionError(f"Host '{host}' resolved to no addresses")
    return tuple(sorted(addresses))


def _ensure_public(addresses: tuple[str, ...], host: str) -> None:
    for raw in addresses:
        address = ipaddress.ip_address(raw)
        if _is_blocked_address(address):
            raise BlockedTargetError(
                f"Host '{host}' resolves to a non-public address ({raw}) and cannot be scanned"
            )


def normalize_url(raw: str) -> str:
    candidate = raw.strip()
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    return candidate


async def validate_target(raw: str) -> ValidatedTarget:
    url = normalize_url(raw)
    parts = urlsplit(url)

    scheme = parts.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise BlockedTargetError(f"Scheme '{scheme or 'none'}' is not allowed; use http or https")

    host = _normalize_host(parts.hostname or "")
    if not host:
        raise BlockedTargetError("URL must include a hostname")

    try:
        port = parts.port or (443 if scheme == "https" else 80)
    except ValueError as exc:
        raise BlockedTargetError("URL contains an invalid port") from exc

    literal = _parse_literal_ip(host)
    if literal is not None:
        _ensure_public((str(literal),), host)
        return ValidatedTarget(url=url, scheme=scheme, host=host, port=port, addresses=(str(literal),))

    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        raise BlockedTargetError(f"Host '{host}' is not a public target")

    addresses = await _resolve(host, port)
    _ensure_public(addresses, host)
    return ValidatedTarget(url=url, scheme=scheme, host=host, port=port, addresses=addresses)
