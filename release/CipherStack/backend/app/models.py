from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Grade(StrEnum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class Verdict(StrEnum):
    PASS = "pass"
    WARNING = "warning"
    MISSING = "missing"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    INFO = "info"
    NONE = "none"


class ScanRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)

    @field_validator("url")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("URL must not be empty")
        return cleaned


class HeaderFinding(BaseModel):
    header: str
    verdict: Verdict
    value: str | None
    tip: str
    weight: int


class EndpointFinding(BaseModel):
    path: str
    status_code: int | None
    exposed: bool
    severity: Severity
    note: str


class ScanResponse(BaseModel):
    target: str
    final_url: str
    status_code: int
    grade: Grade
    score: float
    findings: list[HeaderFinding]
    endpoints: list[EndpointFinding]
    redirects: list[str]
    flags: list[str]
    scanned_at: datetime


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    detail: ErrorDetail
