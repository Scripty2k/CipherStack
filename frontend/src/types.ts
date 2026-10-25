export type Grade = 'A+' | 'A' | 'B' | 'C' | 'D' | 'F';

export type Verdict = 'pass' | 'warning' | 'missing';

export type Severity = 'critical' | 'high' | 'info' | 'none';

export interface HeaderFinding {
    header: string;
    verdict: Verdict;
    value: string | null;
    tip: string;
    weight: number;
}

export interface EndpointFinding {
    path: string;
    status_code: number | null;
    exposed: boolean;
    severity: Severity;
    note: string;
}

export interface ScanResult {
    target: string;
    final_url: string;
    status_code: number;
    grade: Grade;
    score: number;
    findings: HeaderFinding[];
    endpoints: EndpointFinding[];
    redirects: string[];
    flags: string[];
    scanned_at: string;
}

export interface ApiErrorDetail {
    code: string;
    message: string;
}

export interface ApiErrorBody {
    detail: ApiErrorDetail | ApiErrorDetail[];
}

export type ScanStatus = 'idle' | 'loading' | 'success' | 'error';
