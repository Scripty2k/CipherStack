import { EndpointList } from './components/EndpointList';
import { ErrorBanner } from './components/ErrorBanner';
import { HeaderAccordion } from './components/HeaderAccordion';
import { ScoreSummary } from './components/ScoreSummary';
import { UrlScanForm } from './components/UrlScanForm';
import { useScan } from './hooks/useScan';

export default function App() {
    const { status, result, error, scan } = useScan();
    const loading = status === 'loading';

    return (
        <div className="mx-auto flex min-h-screen w-full max-w-3xl flex-col px-5 py-12 sm:py-16">
            <header className="mb-8">
                <div className="flex items-center gap-2.5">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-accent/30 bg-accent/10 font-mono text-sm font-bold text-accent">
                        CS
                    </span>
                    <h1 className="text-lg font-semibold tracking-tight">CipherStack</h1>
                </div>
                <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted">
                    Audit HTTP security headers and exposed endpoints for any public URL. Every scan returns a
                    weighted score, a letter grade, and concrete remediation steps.
                </p>
            </header>

            <main className="flex flex-col gap-5">
                <UrlScanForm loading={loading} onScan={scan} />

                {status === 'error' && error && <ErrorBanner code={error.code} message={error.message} />}

                {status === 'idle' && (
                    <div className="panel px-5 py-10 text-center">
                        <p className="text-sm text-muted">
                            Enter a hostname such as <span className="font-mono text-ink/80">github.com</span> to begin.
                        </p>
                    </div>
                )}

                {status === 'success' && result && (
                    <>
                        <ScoreSummary result={result} />
                        <HeaderAccordion findings={result.findings} />
                        <EndpointList endpoints={result.endpoints} />
                    </>
                )}
            </main>

            <footer className="mt-auto pt-10 text-xs text-muted/70">
                Scans are read-only and never stored. Private and loopback addresses are blocked.
            </footer>
        </div>
    );
}
