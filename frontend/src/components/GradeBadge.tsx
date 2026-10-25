import type { Grade } from '../types';

const GRADE_STYLES: Record<Grade, string> = {
    'A+': 'border-emerald-400/40 bg-emerald-400/10 text-emerald-300',
    A: 'border-emerald-400/40 bg-emerald-400/10 text-emerald-300',
    B: 'border-lime-400/40 bg-lime-400/10 text-lime-300',
    C: 'border-amber-400/40 bg-amber-400/10 text-amber-300',
    D: 'border-orange-400/40 bg-orange-400/10 text-orange-300',
    F: 'border-rose-400/40 bg-rose-400/10 text-rose-300',
};

interface GradeBadgeProps {
    grade: Grade;
    size?: 'md' | 'lg';
}

export function GradeBadge({ grade, size = 'lg' }: GradeBadgeProps) {
    const sizing = size === 'lg' ? 'h-24 w-24 text-4xl' : 'h-12 w-12 text-lg';

    return (
        <div
            className={`flex shrink-0 items-center justify-center rounded-2xl border font-bold tabular-nums ${sizing} ${GRADE_STYLES[grade]}`}
            aria-label={`Security grade ${grade}`}
        >
            {grade}
        </div>
    );
}
