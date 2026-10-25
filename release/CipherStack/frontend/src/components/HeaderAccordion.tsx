import type { HeaderFinding, Verdict } from '../types';

interface HeaderAccordionProps {
    findings: HeaderFinding[];
}

const VERDICT_STYLES: Record<Verdict, string> = {
    pass: 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300',
    warning: 'border-amber-400/30 bg-amber-400/10 text-amber-300',
    missing: 'border-rose-400/30 bg-rose-400/10 text-rose-300',
};

const VERDICT_LABELS: Record<Verdict, string> = {
    pass: 'Pass',
    warning: 'Warning',
    missing: 'Missing',
};

function HeaderRow({ finding }: { finding: HeaderFinding }) {
    const isPassing = finding.verdict === 'pass';

    return (
        <details className="group border-b border-line last:border-b-0">
            <summary className="flex cursor-pointer list-none items-center gap-3 px-5 py-4 transition hover:bg-elevated/50">
                <span
                    className="text-muted transition group-open:rotate-90"
                    aria-hidden="true"
                >
                    ›
                </span>
                <span className="min-w-0 flex-1 truncate font-mono text-sm">{finding.header}</span>
                <span className={`pill shrink-0 ${VERDICT_STYLES[finding.verdict]}`}>
                    {VERDICT_LABELS[finding.verdict]}
                </span>
            </summary>
            <div className="space-y-3 px-5 pb-5 pl-11">
                <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-muted">Current value</p>
                    <pre className="mt-1.5 overflow-x-auto whitespace-pre-wrap break-all rounded-lg border border-line bg-canvas/60 px-3 py-2 font-mono text-xs text-ink/90">
                        {finding.value ?? 'Not set'}
                    </pre>
                </div>
                {!isPassing && (
                    <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-muted">Remediation</p>
                        <p className="mt-1.5 text-sm text-ink/80">{finding.tip}</p>
                    </div>
                )}
            </div>
        </details>
    );
}

export function HeaderAccordion({ findings }: HeaderAccordionProps) {
    return (
        <section className="panel animate-fade-up overflow-hidden" aria-label="Header findings">
            <header className="border-b border-line px-5 py-4">
                <h2 className="text-sm font-semibold">Security headers</h2>
                <p className="mt-0.5 text-xs text-muted">Expand a header to inspect its value and fix guidance.</p>
            </header>
            {findings.map((finding) => (
                <HeaderRow key={finding.header} finding={finding} />
            ))}
        </section>
    );
}
