'use client';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface JobStep {
  step: string;
  status: 'pending' | 'running' | 'done' | 'error';
  ts?: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const STEP_STYLES: Record<JobStep['status'], {
  dot: string;
  label: string;
  icon: string;
}> = {
  pending: {
    dot:   'bg-gray-700 border-gray-600',
    label: 'text-gray-500',
    icon:  '○',
  },
  running: {
    dot:   'bg-blue-500/20 border-blue-500 animate-pulse',
    label: 'text-blue-400',
    icon:  '◉',
  },
  done: {
    dot:   'bg-emerald-500/20 border-emerald-500',
    label: 'text-gray-300',
    icon:  '✓',
  },
  error: {
    dot:   'bg-red-500/20 border-red-500',
    label: 'text-red-400',
    icon:  '✗',
  },
};

function formatTs(ts: string | undefined): string {
  if (!ts) return '';
  try {
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch {
    return ts;
  }
}

// ─── Component ────────────────────────────────────────────────────────────────

interface JobProgressTimelineProps {
  steps: JobStep[] | null | undefined;
}

export default function JobProgressTimeline({ steps }: JobProgressTimelineProps) {
  // Graceful degradation: nothing to render
  if (!steps || steps.length === 0) return null;

  return (
    <div className="relative pl-4">
      {steps.map((step, i) => {
        const styles = STEP_STYLES[step.status] ?? STEP_STYLES.pending;
        const isLast = i === steps.length - 1;

        return (
          <div key={i} className="relative flex gap-4 pb-4 last:pb-0">
            {/* Vertical connector line */}
            {!isLast && (
              <div
                className="absolute left-[11px] top-7 bottom-0 w-px bg-gray-800"
                aria-hidden="true"
              />
            )}

            {/* Dot */}
            <div
              className={`relative z-10 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-bold mt-0.5 ${styles.dot}`}
            >
              <span
                className={
                  step.status === 'done'   ? 'text-emerald-400' :
                  step.status === 'error'  ? 'text-red-400'     :
                  step.status === 'running'? 'text-blue-400'    :
                                             'text-gray-600'
                }
              >
                {styles.icon}
              </span>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0 pt-0.5">
              <div className="flex items-baseline gap-3">
                <p className={`text-xs font-medium leading-none ${styles.label}`}>
                  {step.step}
                </p>
                {step.ts && (
                  <span className="text-[10px] text-gray-600 shrink-0">
                    {formatTs(step.ts)}
                  </span>
                )}
              </div>
              {step.status === 'running' && (
                <p className="text-[10px] text-blue-400/70 mt-1">In progress…</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
