import type { ApiErrorBody, ApiErrorDetail, ScanResult } from '../types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');

export class ScanApiError extends Error {
    readonly code: string;

    constructor(code: string, message: string) {
        super(message);
        this.name = 'ScanApiError';
        this.code = code;
    }
}

function isDetailArray(value: unknown): value is ApiErrorDetail[] {
    return Array.isArray(value);
}

function extractDetail(body: unknown): ApiErrorDetail | null {
    if (typeof body !== 'object' || body === null || !('detail' in body)) {
        return null;
    }

    const { detail } = body as ApiErrorBody;

    if (isDetailArray(detail)) {
        const first = detail[0];
        if (!first) {
            return null;
        }
        return { code: 'validation_error', message: first.message };
    }

    if (typeof detail === 'object' && detail !== null && 'message' in detail) {
        return detail;
    }

    return null;
}

export async function scanUrl(url: string, signal?: AbortSignal): Promise<ScanResult> {
    let response: Response;

    try {
        response = await fetch(`${API_BASE_URL}/api/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url }),
            signal: signal ?? null,
        });
    } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
            throw error;
        }
        throw new ScanApiError('network_error', 'Could not reach the CipherStack API. Is the backend running?');
    }

    const payload: unknown = await response.json().catch(() => null);

    if (!response.ok) {
        const detail = extractDetail(payload);
        throw new ScanApiError(
            detail?.code ?? 'request_failed',
            detail?.message ?? `The scan failed with HTTP ${response.status}.`,
        );
    }

    return payload as ScanResult;
}
