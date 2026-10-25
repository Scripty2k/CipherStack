import { useState, type FormEvent } from 'react';

interface UrlScanFormProps {
    loading: boolean;
    onScan: (url: string) => void;
}

export function UrlScanForm({ loading, onScan }: UrlScanFormProps) {
    const [value, setValue] = useState('');

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const trimmed = value.trim();
        if (!trimmed || loading) {
            return;
        }
        onScan(trimmed);
    }

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row" role="search">
            <div className="relative flex-1">
                <label htmlFor="target-url" className="sr-only">
                    Target URL
                </label>
                <input
                    id="target-url"
                    type="text"
                    inputMode="url"
                    autoComplete="url"
                    spellCheck={false}
                    placeholder="example.com"
                    value={value}
                    onChange={(event) => setValue(event.target.value)}
                    disabled={loading}
                    className="w-full rounded-xl border border-line bg-elevated/70 px-4 py-3.5 font-mono text-sm text-ink placeholder:text-muted/60 transition focus:border-accent/60 focus:bg-elevated disabled:opacity-60"
                />
            </div>
            <button
                type="submit"
                disabled={loading || value.trim().length === 0}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-accent px-6 py-3.5 text-sm font-semibold text-canvas transition hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-50"
            >
                {loading ? (
                    <>
                        <span
                            className="h-4 w-4 animate-spin rounded-full border-2 border-canvas/30 border-t-canvas"
                            aria-hidden="true"
                        />
                        Scanning
                    </>
                ) : (
                    'Scan'
                )}
            </button>
        </form>
    );
}
