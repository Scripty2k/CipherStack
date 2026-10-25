from __future__ import annotations

import re
from collections.abc import Mapping

from .models import HeaderFinding, Verdict

HSTS_MIN_MAX_AGE = 15_552_000

_STRONG_REFERRER_POLICIES = frozenset(
    {"no-referrer", "strict-origin-when-cross-origin", "same-origin", "strict-origin"}
)
_WEAK_REFERRER_POLICIES = frozenset(
    {"unsafe-url", "origin", "origin-when-cross-origin", "no-referrer-when-downgrade"}
)
_FRAME_OPTIONS_PASS = frozenset({"deny", "sameorigin"})

_CSP_NONCE_OR_HASH = re.compile(r"'(?:nonce|sha256|sha384|sha512)-", re.IGNORECASE)
_HSTS_MAX_AGE = re.compile(r"max-age\s*=\s*(\d+)", re.IGNORECASE)


def _lookup(headers: Mapping[str, str], name: str) -> str | None:
    lowered = name.lower()
    for key, value in headers.items():
        if key.lower() == lowered:
            return value.strip()
    return None


def _finding(header: str, verdict: Verdict, value: str | None, tip: str, weight: int) -> HeaderFinding:
    return HeaderFinding(header=header, verdict=verdict, value=value, tip=tip, weight=weight)


def evaluate_csp(headers: Mapping[str, str]) -> HeaderFinding:
    header = "Content-Security-Policy"
    weight = 25
    value = _lookup(headers, header)
    tip = "Define a Content-Security-Policy that restricts script sources to trusted origins."

    if value is None:
        return _finding(header, Verdict.MISSING, None, tip, weight)

    lowered = value.lower()
    has_unsafe = "unsafe-inline" in lowered or "unsafe-eval" in lowered
    if has_unsafe and not _CSP_NONCE_OR_HASH.search(value):
        return _finding(
            header,
            Verdict.WARNING,
            value,
            "Replace 'unsafe-inline' and 'unsafe-eval' with nonces or hashes to block injected scripts.",
            weight,
        )
    return _finding(header, Verdict.PASS, value, tip, weight)


def evaluate_hsts(headers: Mapping[str, str]) -> HeaderFinding:
    header = "Strict-Transport-Security"
    weight = 20
    value = _lookup(headers, header)
    tip = "Send Strict-Transport-Security with max-age of at least 15552000 and includeSubDomains."

    if value is None:
        return _finding(header, Verdict.MISSING, None, tip, weight)

    match = _HSTS_MAX_AGE.search(value)
    max_age = int(match.group(1)) if match else 0
    has_subdomains = "includesubdomains" in value.lower()

    if max_age < HSTS_MIN_MAX_AGE or not has_subdomains:
        return _finding(
            header,
            Verdict.WARNING,
            value,
            "Raise max-age to at least 15552000 seconds and add includeSubDomains to cover every subdomain.",
            weight,
        )
    return _finding(header, Verdict.PASS, value, tip, weight)


def evaluate_x_frame_options(headers: Mapping[str, str]) -> HeaderFinding:
    header = "X-Frame-Options"
    weight = 15
    value = _lookup(headers, header)
    tip = "Set X-Frame-Options to DENY or SAMEORIGIN to prevent clickjacking."

    if value is None:
        return _finding(header, Verdict.MISSING, None, tip, weight)

    normalized = value.split(",")[0].strip().lower()
    if normalized in _FRAME_OPTIONS_PASS:
        return _finding(header, Verdict.PASS, value, tip, weight)
    return _finding(
        header,
        Verdict.WARNING,
        value,
        "Use DENY or SAMEORIGIN; ALLOW-FROM is deprecated and ignored by modern browsers.",
        weight,
    )


def evaluate_x_content_type_options(headers: Mapping[str, str]) -> HeaderFinding:
    header = "X-Content-Type-Options"
    weight = 15
    value = _lookup(headers, header)
    tip = "Set X-Content-Type-Options to nosniff to stop MIME-type sniffing."

    if value is None:
        return _finding(header, Verdict.MISSING, None, tip, weight)

    if value.strip().lower() == "nosniff":
        return _finding(header, Verdict.PASS, value, tip, weight)
    return _finding(header, Verdict.WARNING, value, "The only valid value is nosniff.", weight)


def evaluate_referrer_policy(headers: Mapping[str, str]) -> HeaderFinding:
    header = "Referrer-Policy"
    weight = 15
    value = _lookup(headers, header)
    tip = "Set Referrer-Policy to strict-origin-when-cross-origin or no-referrer."

    if value is None:
        return _finding(header, Verdict.MISSING, None, tip, weight)

    tokens = [token.strip().lower() for token in value.split(",") if token.strip()]
    if any(token in _WEAK_REFERRER_POLICIES for token in tokens):
        return _finding(
            header,
            Verdict.WARNING,
            value,
            "Avoid policies that leak full URLs cross-origin; prefer strict-origin-when-cross-origin.",
            weight,
        )
    if any(token in _STRONG_REFERRER_POLICIES for token in tokens):
        return _finding(header, Verdict.PASS, value, tip, weight)
    return _finding(header, Verdict.WARNING, value, tip, weight)


def evaluate_permissions_policy(headers: Mapping[str, str]) -> HeaderFinding:
    header = "Permissions-Policy"
    weight = 10
    value = _lookup(headers, header)
    tip = "Declare a Permissions-Policy that disables powerful features such as camera and geolocation."

    if value is None:
        return _finding(header, Verdict.MISSING, None, tip, weight)

    if not value.strip():
        return _finding(header, Verdict.WARNING, value, tip, weight)
    return _finding(header, Verdict.PASS, value, tip, weight)


_RULES = (
    evaluate_csp,
    evaluate_hsts,
    evaluate_x_frame_options,
    evaluate_x_content_type_options,
    evaluate_referrer_policy,
    evaluate_permissions_policy,
)


def evaluate_headers(headers: Mapping[str, str]) -> list[HeaderFinding]:
    return [rule(headers) for rule in _RULES]
