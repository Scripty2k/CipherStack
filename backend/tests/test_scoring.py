from __future__ import annotations

import pytest

from app.models import EndpointFinding, Grade, HeaderFinding, Severity, Verdict
from app.scoring import compute_grade, compute_score, grade_for_score


def _finding(verdict: Verdict, weight: int = 10) -> HeaderFinding:
    return HeaderFinding(header="X-Test", verdict=verdict, value=None, tip="tip", weight=weight)


def _endpoint(path: str, exposed: bool, severity: Severity) -> EndpointFinding:
    return EndpointFinding(
        path=path,
        status_code=200 if exposed else 404,
        exposed=exposed,
        severity=severity,
        note="",
    )


def test_all_pass_scores_one_hundred() -> None:
    findings = [_finding(Verdict.PASS) for _ in range(6)]
    assert compute_score(findings) == 100.0


def test_warning_earns_half_credit() -> None:
    findings = [_finding(Verdict.PASS), _finding(Verdict.WARNING)]
    assert compute_score(findings) == 75.0


def test_all_missing_scores_zero() -> None:
    assert compute_score([_finding(Verdict.MISSING) for _ in range(3)]) == 0.0


def test_empty_findings_score_zero() -> None:
    assert compute_score([]) == 0.0


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (100.0, Grade.A_PLUS),
        (95.0, Grade.A_PLUS),
        (94.9, Grade.A),
        (85.0, Grade.A),
        (84.9, Grade.B),
        (75.0, Grade.B),
        (74.9, Grade.C),
        (60.0, Grade.C),
        (59.9, Grade.D),
        (45.0, Grade.D),
        (44.9, Grade.F),
        (0.0, Grade.F),
    ],
)
def test_grade_bands(score: float, expected: Grade) -> None:
    assert grade_for_score(score) is expected


def test_exposed_git_caps_grade_at_f() -> None:
    findings = [_finding(Verdict.PASS) for _ in range(6)]
    endpoints = [_endpoint("/.git/HEAD", True, Severity.CRITICAL)]
    score, grade, flags = compute_grade(findings, endpoints)
    assert score == 100.0
    assert grade is Grade.F
    assert len(flags) == 1


def test_exposed_env_caps_grade_at_d() -> None:
    findings = [_finding(Verdict.PASS) for _ in range(6)]
    endpoints = [_endpoint("/.env", True, Severity.HIGH)]
    _, grade, flags = compute_grade(findings, endpoints)
    assert grade is Grade.D
    assert len(flags) == 1


def test_informational_endpoints_do_not_affect_grade() -> None:
    findings = [_finding(Verdict.PASS) for _ in range(6)]
    endpoints = [
        _endpoint("/robots.txt", True, Severity.INFO),
        _endpoint("/sitemap.xml", True, Severity.INFO),
    ]
    _, grade, flags = compute_grade(findings, endpoints)
    assert grade is Grade.A_PLUS
    assert flags == []


def test_cap_does_not_upgrade_a_worse_grade() -> None:
    findings = [_finding(Verdict.MISSING) for _ in range(6)]
    endpoints = [_endpoint("/.env", True, Severity.HIGH)]
    _, grade, flags = compute_grade(findings, endpoints)
    assert grade is Grade.F
    assert flags == []
