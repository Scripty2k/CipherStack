import type { Config } from 'tailwindcss';

const config: Config = {
    content: ['./index.html', './src/**/*.{ts,tsx}'],
    theme: {
        extend: {
            colors: {
                canvas: '#0a0b0f',
                surface: '#12141a',
                elevated: '#171a22',
                line: '#1f2330',
                ink: '#e6e8ee',
                muted: '#8b90a0',
                accent: '#4f8cff',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
                mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
            },
            boxShadow: {
                panel: '0 1px 0 0 rgba(255,255,255,0.04) inset, 0 20px 40px -24px rgba(0,0,0,0.9)',
            },
            keyframes: {
                'fade-up': {
                    from: { opacity: '0', transform: 'translateY(8px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
            },
            animation: {
                'fade-up': 'fade-up 240ms ease-out both',
            },
        },
    },
    plugins: [],
};

export default config;
