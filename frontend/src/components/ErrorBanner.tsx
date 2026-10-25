interface ErrorBannerProps {
    code: string;
    message: string;
}

export function ErrorBanner({ code, message }: ErrorBannerProps) {
    return (
        <div
            role="alert"
            className="animate-fade-up rounded-xl border border-rose-400/30 bg-rose-400/10 px-4 py-3.5"
        >
            <p className="text-sm font-semibold text-rose-300">Scan failed</p>
            <p className="mt-1 text-sm text-rose-200/80">{message}</p>
            <p className="mt-2 font-mono text-xs text-rose-300/60">{code}</p>
        </div>
    );
}
