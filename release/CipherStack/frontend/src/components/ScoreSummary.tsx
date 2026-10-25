import type { ScanResult, Verdict } from '../types';
import { GradeBadge } from './GradeBadge';

interface ScoreSummaryProps {
    result: ScanResult;
}

const VERDICT_LABELS: Record<Verdict, string> = {
    pass: 'Passing',
    warning: 'Warnings',
    missing: 'Missing',
};

const VERDICT_STYLES: Record<Verdict, string> = {
    pass: 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300',
    warning: 'border-amber-400/30 bg-amber-400/10 text-amber-300',
    missing: 'border-rose-400/30 bg-rose-400/10 text-rose-300',
};

function countByVerdict(result: ScanResult, verdict: Verdict): number {
    return result.findings.filter((finding) => finding.verdict === verdict).length;
}

export function ScoreSummary({ result }: ScoreSummaryProps) {
    const verdicts: Verdict[] = ['pass', 'warning', 'missing'];

    return (
        <section className="panel animate-fade-up p-6" aria-label="Scan summary">
            <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
                <GradeBadge grade={result.grade} />
                <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                        <span className="text-3xl font-semibold tabular-nums">{result.score.toFixed(1)}</span>
                        <span className="text-sm text-muted">out of 100</span>
                    </div>
                    <p className="mt-1 truncate font-mono text-sm text-muted" title={result.final_url}>
                        {result.final_url}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                        {verdicts.map((verdict) => (
                            <span key={verdict} className={`pill ${VERDICT_STYLES[verdict]}`}>
                                {VERDICT_LABELS[verdict]}
                                <span className="tabular-nums opacity-80">{countByVerdict(result, verdict)}</span>
                            </span>
                        ))}
                        <span className="pill border-line bg-elevated text-muted">
                            HTTP <span className="tabular-nums">{result.status_code}</span>
                        </span>
                        {result.redirects.length > 0 && (
                            <span className="pill border-line bg-elevated text-muted">
                                Redirects <span className="tabular-nums">{result.redirects.length}</span>
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {result.flags.length > 0 && (
                <ul className="mt-5 space-y-2 border-t border-line pt-5">
                    {result.flags.map((flag) => (
                        <li key={flag} className="flex gap-2 text-sm text-rose-300">
                            <span aria-hidden="true">!</span>
                            <span>{flag}</span>
                        </li>
                    ))}
                </ul>
            )}
        </section>
    );
}
