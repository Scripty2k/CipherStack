from __future__ import annotations

import pytest

from app.models import Verdict
from app.rules import (
    evaluate_csp,
    evaluate_headers,
    evaluate_hsts,
    evaluate_permissions_policy,
    evaluate_referrer_policy,
    evaluate_x_content_type_options,
    evaluate_x_frame_options,
)

SECURE_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'nonce-abc123'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), geolocation=()",
}


def test_all_secure_headers_pass() -> None:
    findings = evaluate_headers(SECURE_HEADERS)
    assert len(findings) == 6
    assert all(finding.verdict is Verdict.PASS for finding in findings)


def test_missing_headers_are_reported() -> None:
    findings = evaluate_headers({})
    assert all(finding.verdict is Verdict.MISSING for finding in findings)
    assert all(finding.value is None for finding in findings)
    assert all(finding.tip for finding in findings)


def test_header_lookup_is_case_insensitive() -> None:
    headers = {key.lower(): value for key, value in SECURE_HEADERS.items()}
    findings = evaluate_headers(headers)
    assert all(finding.verdict is Verdict.PASS for finding in findings)


@pytest.mark.parametrize(
    "policy",
    [
        "default-src 'self'; script-src 'unsafe-inline'",
        "default-src 'self'; script-src 'unsafe-eval'",
    ],
)
def test_csp_with_unsafe_directives_warns(policy: str) -> None:
    finding = evaluate_csp({"Content-Security-Policy": policy})
    assert finding.verdict is Verdict.WARNING


def test_csp_unsafe_inline_with_nonce_passes() -> None:
    policy = "default-src 'self'; script-src 'unsafe-inline' 'nonce-abc123'"
    assert evaluate_csp({"Content-Security-Policy": policy}).verdict is Verdict.PASS


@pytest.mark.parametrize(
    "value",
    [
        "max-age=300; includeSubDomains",
        "max-age=31536000",
        "includeSubDomains",
    ],
)
def test_weak_hsts_warns(value: str) -> None:
    assert evaluate_hsts({"Strict-Transport-Security": value}).verdict is Verdict.WARNING


def test_hsts_strong_passes() -> None:
    value = "max-age=63072000; includeSubDomains; preload"
    assert evaluate_hsts({"Strict-Transport-Security": value}).verdict is Verdict.PASS


@pytest.mark.parametrize("value", ["DENY", "SAMEORIGIN", "sameorigin"])
def test_frame_options_valid_values_pass(value: str) -> None:
    assert evaluate_x_frame_options({"X-Frame-Options": value}).verdict is Verdict.PASS


def test_frame_options_allow_from_warns() -> None:
    value = "ALLOW-FROM https://example.com"
    assert evaluate_x_frame_options({"X-Frame-Options": value}).verdict is Verdict.WARNING


def test_content_type_options_only_nosniff_passes() -> None:
    assert evaluate_x_content_type_options({"X-Content-Type-Options": "nosniff"}).verdict is Verdict.PASS
    assert evaluate_x_content_type_options({"X-Content-Type-Options": "sniff"}).verdict is Verdict.WARNING


@pytest.mark.parametrize("value", ["no-referrer", "same-origin", "strict-origin"])
def test_strong_referrer_policies_pass(value: str) -> None:
    assert evaluate_referrer_policy({"Referrer-Policy": value}).verdict is Verdict.PASS


@pytest.mark.parametrize("value", ["unsafe-url", "origin", "no-referrer-when-downgrade"])
def test_weak_referrer_policies_warn(value: str) -> None:
    assert evaluate_referrer_policy({"Referrer-Policy": value}).verdict is Verdict.WARNING


def test_permissions_policy_empty_value_warns() -> None:
    assert evaluate_permissions_policy({"Permissions-Policy": "  "}).verdict is Verdict.WARNING


def test_weights_sum_to_one_hundred() -> None:
    assert sum(finding.weight for finding in evaluate_headers({})) == 100
