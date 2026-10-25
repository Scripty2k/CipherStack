from __future__ import annotations

from collections.abc import Sequence

from .models import EndpointFinding, Grade, HeaderFinding, Severity, Verdict

_GRADE_BANDS: tuple[tuple[float, Grade], ...] = (
    (95.0, Grade.A_PLUS),
    (85.0, Grade.A),
    (75.0, Grade.B),
    (60.0, Grade.C),
    (45.0, Grade.D),
)

_GRADE_ORDER: tuple[Grade, ...] = (
    Grade.A_PLUS,
    Grade.A,
    Grade.B,
    Grade.C,
    Grade.D,
    Grade.F,
)

_VERDICT_CREDIT = {
    Verdict.PASS: 1.0,
    Verdict.WARNING: 0.5,
    Verdict.MISSING: 0.0,
}

_ENDPOINT_CAPS: dict[str, tuple[Grade, str]] = {
    "/.git/HEAD": (
        Grade.F,
        "Exposed /.git/HEAD allows source code disclosure and caps the grade at F.",
    ),
    "/.env": (
        Grade.D,
        "Exposed /.env may leak secrets and caps the grade at D.",
    ),
}


def compute_score(findings: Sequence[HeaderFinding]) -> float:
    total = sum(finding.weight for finding in findings)
    if total == 0:
        return 0.0
    earned = sum(finding.weight * _VERDICT_CREDIT[finding.verdict] for finding in findings)
    return round(earned / total * 100, 1)


def grade_for_score(score: float) -> Grade:
    for threshold, grade in _GRADE_BANDS:
        if score >= threshold:
            return grade
    return Grade.F


def _worse_of(left: Grade, right: Grade) -> Grade:
    return left if _GRADE_ORDER.index(left) >= _GRADE_ORDER.index(right) else right


def compute_grade(
    findings: Sequence[HeaderFinding],
    endpoints: Sequence[EndpointFinding],
) -> tuple[float, Grade, list[str]]:
    score = compute_score(findings)
    grade = grade_for_score(score)
    flags: list[str] = []

    for endpoint in endpoints:
        if not endpoint.exposed or endpoint.severity not in {Severity.CRITICAL, Severity.HIGH}:
            continue
        cap = _ENDPOINT_CAPS.get(endpoint.path)
        if cap is None:
            continue
        cap_grade, message = cap
        if _GRADE_ORDER.index(cap_grade) > _GRADE_ORDER.index(grade):
            grade = _worse_of(grade, cap_grade)
            flags.append(message)

    return score, grade, flags
