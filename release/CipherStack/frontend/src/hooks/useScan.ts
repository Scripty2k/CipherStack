import { useCallback, useEffect, useRef, useState } from 'react';

import { ScanApiError, scanUrl } from '../lib/api';
import type { ScanResult, ScanStatus } from '../types';

interface ScanState {
    status: ScanStatus;
    result: ScanResult | null;
    error: { code: string; message: string } | null;
    scan: (url: string) => Promise<void>;
}

export function useScan(): ScanState {
    const [status, setStatus] = useState<ScanStatus>('idle');
    const [result, setResult] = useState<ScanResult | null>(null);
    const [error, setError] = useState<{ code: string; message: string } | null>(null);
    const controllerRef = useRef<AbortController | null>(null);

    useEffect(() => () => controllerRef.current?.abort(), []);

    const scan = useCallback(async (url: string) => {
        controllerRef.current?.abort();
        const controller = new AbortController();
        controllerRef.current = controller;

        setStatus('loading');
        setError(null);

        try {
            const response = await scanUrl(url, controller.signal);
            if (controller.signal.aborted) {
                return;
            }
            setResult(response);
            setStatus('success');
        } catch (caught) {
            if (caught instanceof DOMException && caught.name === 'AbortError') {
                return;
            }
            const code = caught instanceof ScanApiError ? caught.code : 'unexpected_error';
            const message = caught instanceof Error ? caught.message : 'An unexpected error occurred.';
            setError({ code, message });
            setStatus('error');
        }
    }, []);

    return { status, result, error, scan };
}
