import type { EndpointFinding, Severity } from '../types';

interface EndpointListProps {
    endpoints: EndpointFinding[];
}

const SEVERITY_STYLES: Record<Severity, string> = {
    critical: 'border-rose-400/30 bg-rose-400/10 text-rose-300',
    high: 'border-orange-400/30 bg-orange-400/10 text-orange-300',
    info: 'border-sky-400/30 bg-sky-400/10 text-sky-300',
    none: 'border-line bg-elevated text-muted',
};

const SEVERITY_LABELS: Record<Severity, string> = {
    critical: 'Critical',
    high: 'High',
    info: 'Info',
    none: 'Clear',
};

export function EndpointList({ endpoints }: EndpointListProps) {
    return (
        <section className="panel animate-fade-up overflow-hidden" aria-label="Endpoint probes">
            <header className="border-b border-line px-5 py-4">
                <h2 className="text-sm font-semibold">Exposed endpoints</h2>
                <p className="mt-0.5 text-xs text-muted">Sensitive paths probed on the final origin.</p>
            </header>
            <ul>
                {endpoints.map((endpoint) => (
                    <li
                        key={endpoint.path}
                        className="flex flex-col gap-2 border-b border-line px-5 py-3.5 last:border-b-0 sm:flex-row sm:items-center sm:gap-3"
                    >
                        <span className="min-w-0 flex-1 truncate font-mono text-sm">{endpoint.path}</span>
                        <span className="font-mono text-xs tabular-nums text-muted">
                            {endpoint.status_code ?? 'ERR'}
                        </span>
                        <span className={`pill shrink-0 ${SEVERITY_STYLES[endpoint.severity]}`}>
                            {SEVERITY_LABELS[endpoint.severity]}
                        </span>
                        <p className="w-full text-xs text-muted sm:w-64 sm:text-right">{endpoint.note}</p>
                    </li>
                ))}
            </ul>
        </section>
    );
}
