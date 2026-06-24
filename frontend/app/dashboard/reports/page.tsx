'use client';
import { useState, useEffect, useCallback } from 'react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface Success {
  job_id: string;
  label: string;
  credits_used: number;
}

interface Failure {
  job_id: string;
  category: string;
  raw_hint: string;
}

interface RedFlag {
  severity: 'critical' | 'warning' | 'info';
  flag: string;
  detail: string;
  action: string;
}

interface ScalingOpportunity {
  signal: string;
  detail: string;
  opportunity: string;
}

interface TacticChange {
  tactic: string;
  reason: string;
  example: string;
}

interface AgentSection {
  agent_id: string;
  agent_name: string;
  category: string;
  status: 'active' | 'idle';
  jobs_completed: number;
  jobs_failed: number;
  jobs_pending: number;
  jobs_cancelled: number;
  credits_used: number;
  quality_score: string;
  quality_label: string;
  completion_rate_pct: number | null;
  total_jobs: number;
  successes: Success[];
  failures: Failure[];
  red_flags: RedFlag[];
  scaling_opportunities: ScalingOpportunity[];
  tactic_changes: TacticChange[];
  recommendations: string[];
  blockers: string[];
}

interface WeeklyReport {
  id: string;
  reporting_period_start: string;
  reporting_period_end: string;
  executive_summary: string;
  sections: AgentSection[];
  status: string;
  delivery_status: string;
  email_sent_at: string | null;
  created_at: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const QUALITY_BORDER: Record<string, string> = {
  excellent:        'border-emerald-500',
  good:             'border-indigo-500',
  fair:             'border-amber-500',
  needs_improvement:'border-red-500',
  no_activity:      'border-gray-700',
};

const QUALITY_TEXT: Record<string, string> = {
  excellent:        'text-emerald-400',
  good:             'text-indigo-400',
  fair:             'text-amber-400',
  needs_improvement:'text-red-400',
  no_activity:      'text-gray-500',
};

const SEVERITY_STYLES: Record<string, { border: string; bg: string; label: string; icon: string }> = {
  critical: { border: 'border-red-600',    bg: 'bg-red-950/60',    label: 'text-red-400',    icon: '⚠' },
  warning:  { border: 'border-amber-600',  bg: 'bg-amber-950/50',  label: 'text-amber-400',  icon: '⚡' },
  info:     { border: 'border-blue-600',   bg: 'bg-blue-950/40',   label: 'text-blue-400',   icon: 'ℹ' },
};

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function SectionBlock({ title, color, children }: { title: string; color: string; children: React.ReactNode }) {
  return (
    <div className={`rounded-lg border p-4 mb-3 ${color}`}>
      <p className="text-xs font-bold uppercase tracking-wider mb-3 opacity-80">{title}</p>
      {children}
    </div>
  );
}

function RedFlagBlock({ flags }: { flags: RedFlag[] }) {
  if (!flags.length) return null;
  return (
    <div className="mb-3 space-y-2">
      {flags.map((rf, i) => {
        const s = SEVERITY_STYLES[rf.severity] || SEVERITY_STYLES.info;
        return (
          <div key={i} className={`rounded-lg border ${s.border} ${s.bg} p-3`}>
            <div className="flex items-start gap-2">
              <span className={`text-sm ${s.label} shrink-0 mt-0.5`}>{s.icon}</span>
              <div className="flex-1 min-w-0">
                <p className={`text-xs font-bold ${s.label} mb-1`}>{rf.flag}</p>
                <p className="text-xs text-gray-300 mb-1.5">{rf.detail}</p>
                <p className="text-xs text-white font-medium">Action: {rf.action}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ScalingBlock({ opps }: { opps: ScalingOpportunity[] }) {
  if (!opps.length) return null;
  return (
    <div className="mb-3 space-y-2">
      {opps.map((op, i) => (
        <div key={i} className="rounded-lg border border-violet-600 bg-violet-950/40 p-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-violet-400 text-sm">↑</span>
            <p className="text-xs font-bold text-violet-300">{op.signal}</p>
            {(op as any).requires_approval && (
              <span className="text-xs text-amber-400 bg-amber-950/50 border border-amber-700 px-1.5 py-0.5 rounded-full font-semibold">
                Needs your approval
              </span>
            )}
          </div>
          <p className="text-xs text-gray-400 mb-2">{op.detail}</p>
          <p className="text-xs text-violet-200 font-medium">{op.opportunity}</p>
          {(op as any).disclaimer && (
            <p className="text-xs text-gray-600 mt-2 italic">{(op as any).disclaimer}</p>
          )}
        </div>
      ))}
    </div>
  );
}

function TacticBlock({ changes }: { changes: TacticChange[] }) {
  if (!changes.length) return null;
  return (
    <div className="mb-3 space-y-2">
      {changes.map((tc, i) => (
        <div key={i} className="rounded-lg border border-amber-700 bg-amber-950/40 p-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-amber-400 text-sm">→</span>
            <p className="text-xs font-bold text-amber-300">{tc.tactic}</p>
          </div>
          <p className="text-xs text-gray-300 mb-2">{tc.reason}</p>
          {tc.example && (
            <div className="bg-gray-900/60 rounded px-2 py-1.5">
              <p className="text-xs text-gray-500 mb-0.5">Example</p>
              <p className="text-xs text-gray-300 italic">{tc.example}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function AgentCard({
  section,
  onConvert,
}: {
  section: AgentSection;
  onConvert: (rec: string, agentId: string) => void;
}) {
  const [open, setOpen] = useState(false);

  if (section.total_jobs === 0) return null;

  const borderClass = QUALITY_BORDER[section.quality_score] || 'border-gray-700';
  const textClass   = QUALITY_TEXT[section.quality_score]  || 'text-gray-500';
  const hasCritical = section.red_flags?.some(f => f.severity === 'critical');
  const hasScale    = section.scaling_opportunities?.length > 0;

  return (
    <div className={`rounded-xl border-l-4 ${borderClass} bg-gray-900 border border-gray-800 p-5 mb-4`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-white text-sm">{section.agent_name}</span>
            <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded-full">{section.category}</span>
            {hasCritical && (
              <span className="text-xs text-red-400 bg-red-950/60 border border-red-700 px-2 py-0.5 rounded-full font-semibold">
                ⚠ Action needed
              </span>
            )}
            {hasScale && (
              <span className="text-xs text-violet-400 bg-violet-950/40 border border-violet-700 px-2 py-0.5 rounded-full font-semibold">
                ↑ Momentum
              </span>
            )}
          </div>
          <span className={`text-xs font-medium mt-1 block ${textClass}`}>{section.quality_label}</span>
        </div>
        <button
          onClick={() => setOpen(o => !o)}
          className="text-gray-500 hover:text-white transition-colors text-xs shrink-0 pt-0.5"
        >
          {open ? '▲ Close' : '▼ Full report'}
        </button>
      </div>

      {/* Stats row */}
      <div className="flex flex-wrap gap-4 text-xs text-gray-400 pb-3 mb-3 border-b border-gray-800">
        <span className="text-emerald-400">✓ {section.jobs_completed} completed</span>
        <span className={section.jobs_failed > 0 ? 'text-red-400' : 'text-gray-500'}>
          ✗ {section.jobs_failed} failed
        </span>
        {section.jobs_pending > 0 && <span className="text-amber-400">⏳ {section.jobs_pending} pending</span>}
        <span>{section.credits_used} credits used</span>
        {section.completion_rate_pct !== null && (
          <span className={textClass}>{section.completion_rate_pct}% success rate</span>
        )}
      </div>

      {/* Always-visible: red flags + scaling teaser */}
      {hasCritical && (
        <RedFlagBlock flags={section.red_flags.filter(f => f.severity === 'critical')} />
      )}
      {!open && hasScale && (
        <div className="text-xs text-violet-400 bg-violet-950/20 border border-violet-800 rounded-lg px-3 py-2 mb-3">
          ↑ <span className="font-semibold">{section.scaling_opportunities[0].signal}</span> — {section.scaling_opportunities[0].opportunity}
        </div>
      )}

      {/* Expanded detail */}
      {open && (
        <div className="space-y-3 mt-1">

          {/* Successes */}
          {section.successes.length > 0 && (
            <SectionBlock title={`What was delivered (${section.successes.length} task${section.successes.length !== 1 ? 's' : ''})`} color="border-emerald-800 bg-emerald-950/30">
              <ul className="space-y-1.5">
                {section.successes.map((sv, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs">
                    <span className="text-emerald-400 shrink-0 mt-0.5">✓</span>
                    <span className="text-gray-300 flex-1">{sv.label}</span>
                    <span className="text-gray-500 shrink-0">{sv.credits_used}cr</span>
                  </li>
                ))}
              </ul>
            </SectionBlock>
          )}

          {/* Failures */}
          {section.failures.length > 0 && (
            <SectionBlock title={`What went wrong (${section.failures.length})`} color="border-red-800 bg-red-950/30">
              <ul className="space-y-2">
                {section.failures.map((fv, i) => (
                  <li key={i} className="text-xs">
                    <p className="text-red-300 font-medium mb-0.5">✗ {fv.category}</p>
                    {fv.raw_hint && fv.raw_hint !== 'No details recorded' && (
                      <p className="text-gray-600 pl-3">{fv.raw_hint}</p>
                    )}
                  </li>
                ))}
              </ul>
            </SectionBlock>
          )}

          {/* Red flags (all) */}
          {section.red_flags.length > 0 && (
            <>
              <p className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                Red flags ({section.red_flags.length})
              </p>
              <RedFlagBlock flags={section.red_flags} />
            </>
          )}

          {/* Scaling opportunities */}
          {section.scaling_opportunities.length > 0 && (
            <>
              <p className="text-xs font-bold uppercase tracking-wider text-violet-500 mb-2">
                Scaling opportunities
              </p>
              <ScalingBlock opps={section.scaling_opportunities} />
            </>
          )}

          {/* Tactic changes */}
          {section.tactic_changes.length > 0 && (
            <>
              <p className="text-xs font-bold uppercase tracking-wider text-amber-500 mb-2">
                Recommended tactic changes
              </p>
              <TacticBlock changes={section.tactic_changes} />
            </>
          )}

          {/* Recommendations */}
          {section.recommendations.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                Owner recommendations
              </p>
              {section.recommendations.map((r, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-violet-400 text-xs mt-0.5 shrink-0">•</span>
                  <div className="flex-1 min-w-0">
                    <span className="text-xs text-gray-300">{r}</span>
                    <button
                      onClick={() => onConvert(r, section.agent_id)}
                      className="ml-2 text-xs text-violet-400 hover:text-violet-300 underline"
                    >
                      Create task
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function FeedbackPanel({ reportId, onDone }: { reportId: string; onDone: () => void }) {
  const RATINGS = [
    { value: 'useful',                 label: 'Useful' },
    { value: 'do_more_like_this',      label: 'Do more like this' },
    { value: 'not_useful',             label: 'Not useful' },
    { value: 'too_detailed',           label: 'Too detailed' },
    { value: 'not_detailed_enough',    label: 'Not detailed enough' },
    { value: 'wrong_recommendation',   label: 'Wrong recommendation' },
  ];
  const [rating, setRating] = useState('');
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  async function submit() {
    if (!rating) return;
    setSubmitting(true);
    try {
      await fetch(`/api/reports/weekly/${reportId}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ rating, comment: comment || null }),
      });
      setDone(true);
      onDone();
    } catch {}
    setSubmitting(false);
  }

  if (done) return (
    <p className="text-center text-emerald-400 text-sm py-2">Thank you for your feedback!</p>
  );

  return (
    <div>
      <p className="text-sm font-semibold text-white mb-3">How was this report?</p>
      <div className="flex flex-wrap gap-2 mb-3">
        {RATINGS.map(r => (
          <button
            key={r.value}
            onClick={() => setRating(r.value)}
            className={`px-3 py-1.5 rounded-full text-xs border transition-all ${
              rating === r.value
                ? 'bg-violet-600 border-violet-500 text-white'
                : 'border-gray-700 text-gray-400 hover:border-gray-500'
            }`}
          >
            {r.label}
          </button>
        ))}
      </div>
      <textarea
        value={comment}
        onChange={e => setComment(e.target.value)}
        placeholder="Any other thoughts? (optional)"
        rows={2}
        maxLength={500}
        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 resize-none mb-3"
      />
      <button
        onClick={submit}
        disabled={!rating || submitting}
        className="bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
      >
        {submitting ? 'Submitting…' : 'Send feedback'}
      </button>
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function ReportsPage() {
  const [reports, setReports]         = useState<WeeklyReport[]>([]);
  const [total, setTotal]             = useState(0);
  const [skip, setSkip]               = useState(0);
  const [loading, setLoading]         = useState(true);
  const [generating, setGenerating]   = useState(false);
  const [selected, setSelected]       = useState<WeeklyReport | null>(null);
  const [feedbackDone, setFeedbackDone] = useState(false);
  const [convertResult, setConvertResult] = useState<any | null>(null);
  const PAGE = 8;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/reports/weekly?skip=${skip}&limit=${PAGE}`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setReports(data.reports || []);
        setTotal(data.total || 0);
        if (!selected && data.reports?.length) setSelected(data.reports[0]);
      }
    } catch {}
    setLoading(false);
  }, [skip]); // eslint-disable-line

  useEffect(() => { load(); }, [load]);

  async function generate() {
    setGenerating(true);
    try {
      const res = await fetch('/api/reports/weekly/generate', { method: 'POST', credentials: 'include' });
      if (res.ok) {
        setSkip(0);
        setSelected(null);
        await load();
      }
    } catch {}
    setGenerating(false);
  }

  async function convert(rec: string, agentId: string) {
    if (!selected) return;
    const res = await fetch(`/api/reports/weekly/${selected.id}/convert-recommendation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ recommendation_text: rec, agent_id: agentId }),
    });
    if (res.ok) setConvertResult(await res.json());
  }

  const activeSections  = selected?.sections?.filter(s => s.total_jobs > 0) || [];
  const idleSections    = selected?.sections?.filter(s => s.total_jobs === 0) || [];
  const totalCompleted  = activeSections.reduce((n, s) => n + s.jobs_completed, 0);
  const totalFailed     = activeSections.reduce((n, s) => n + s.jobs_failed, 0);
  const totalCredits    = activeSections.reduce((n, s) => n + s.credits_used, 0);
  const criticalFlags   = activeSections.flatMap(s => (s.red_flags || []).filter(f => f.severity === 'critical'));
  const scalingCount    = activeSections.filter(s => s.scaling_opportunities?.length).length;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6 md:p-8">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Weekly AI Workforce Reports</h1>
            <p className="text-gray-500 text-sm mt-1">Successes, failures, red flags and scaling opportunities — every week</p>
          </div>
          <button
            onClick={generate}
            disabled={generating}
            className="bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
          >
            {generating ? 'Generating…' : 'Generate now'}
          </button>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1,2,3].map(i => <div key={i} className="h-20 bg-gray-800 rounded-xl animate-pulse" />)}
          </div>
        ) : reports.length === 0 ? (
          <div className="text-center py-24">
            <div className="text-5xl mb-4">📊</div>
            <p className="text-gray-300 text-lg mb-2 font-semibold">No reports yet</p>
            <p className="text-gray-600 text-sm mb-6 max-w-sm mx-auto">
              Your first report will be generated automatically every Monday at 9am,
              or generate one now to see this week's performance.
            </p>
            <button
              onClick={generate}
              disabled={generating}
              className="bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition-colors"
            >
              {generating ? 'Generating…' : 'Generate your first report'}
            </button>
          </div>
        ) : (
          <div className="flex gap-6">

            {/* History sidebar */}
            <div className="w-52 shrink-0">
              <p className="text-xs text-gray-600 font-semibold uppercase tracking-wider mb-3">History ({total})</p>
              <div className="space-y-1.5">
                {reports.map(r => (
                  <button
                    key={r.id}
                    onClick={() => { setSelected(r); setFeedbackDone(false); setConvertResult(null); }}
                    className={`w-full text-left px-3 py-2.5 rounded-lg border text-xs transition-all ${
                      selected?.id === r.id
                        ? 'border-violet-500 bg-violet-600/10 text-white'
                        : 'border-gray-800 hover:border-gray-700 text-gray-500'
                    }`}
                  >
                    <p className="font-semibold text-white text-xs mb-0.5">{fmtDate(r.reporting_period_end)}</p>
                    <p className="text-gray-600">{r.delivery_status === 'sent' ? '✉ Emailed' : '● Generated'}</p>
                  </button>
                ))}
              </div>
              {total > skip + PAGE && (
                <button
                  onClick={() => setSkip(s => s + PAGE)}
                  className="text-xs text-gray-600 hover:text-gray-400 w-full text-center mt-2 py-1"
                >
                  Load older
                </button>
              )}
            </div>

            {/* Report body */}
            {selected && (
              <div className="flex-1 min-w-0">

                {/* Critical flags banner — always at top */}
                {criticalFlags.length > 0 && (
                  <div className="rounded-xl border border-red-700 bg-red-950/40 p-4 mb-5">
                    <p className="text-sm font-bold text-red-400 mb-2">
                      ⚠ {criticalFlags.length} critical issue{criticalFlags.length !== 1 ? 's' : ''} requiring your attention
                    </p>
                    <ul className="space-y-1">
                      {criticalFlags.map((f, i) => (
                        <li key={i} className="text-xs text-red-200">
                          <span className="font-semibold">{f.flag}</span> — {f.action}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Scaling banner */}
                {scalingCount > 0 && criticalFlags.length === 0 && (
                  <div className="rounded-xl border border-violet-700 bg-violet-950/30 p-4 mb-5">
                    <p className="text-sm font-bold text-violet-300">
                      ↑ {scalingCount} agent{scalingCount !== 1 ? 's are' : ' is'} building momentum — see scaling opportunities below
                    </p>
                  </div>
                )}

                {/* Summary card */}
                <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 mb-5">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="text-xs text-gray-600">
                        {fmtDate(selected.reporting_period_start)} — {fmtDate(selected.reporting_period_end)}
                      </p>
                      <h2 className="text-base font-bold text-white mt-0.5">Executive summary</h2>
                    </div>
                    {selected.email_sent_at && (
                      <span className="text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800 px-2 py-1 rounded-full">
                        ✉ Emailed {fmtDate(selected.email_sent_at)}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-300 leading-relaxed">{selected.executive_summary}</p>

                  <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-800">
                    <div>
                      <p className="text-xl font-bold text-emerald-400">{totalCompleted}</p>
                      <p className="text-xs text-gray-600 mt-0.5">tasks completed</p>
                    </div>
                    <div>
                      <p className={`text-xl font-bold ${totalFailed > 0 ? 'text-red-400' : 'text-gray-600'}`}>{totalFailed}</p>
                      <p className="text-xs text-gray-600 mt-0.5">failed</p>
                    </div>
                    <div>
                      <p className="text-xl font-bold text-violet-400">{totalCredits}</p>
                      <p className="text-xs text-gray-600 mt-0.5">credits used</p>
                    </div>
                    <div>
                      <p className="text-xl font-bold text-white">{activeSections.length}</p>
                      <p className="text-xs text-gray-600 mt-0.5">active agents</p>
                    </div>
                  </div>
                </div>

                {/* Convert result */}
                {convertResult && (
                  <div className="bg-violet-950/30 border border-violet-700 rounded-xl p-4 mb-5">
                    <p className="text-sm font-semibold text-white mb-1">Suggested action</p>
                    <p className="text-xs text-gray-400 mb-0.5">
                      Run <span className="text-violet-300 font-medium">{convertResult.suggested_agent_name}</span> with:
                    </p>
                    <p className="text-xs text-gray-500 italic bg-gray-900 rounded p-2 mb-3">{convertResult.suggested_prompt}</p>
                    <div className="flex gap-3">
                      <a
                        href={`/dashboard/create?task=${encodeURIComponent(convertResult.suggested_prompt || '')}`}
                        className="text-xs bg-violet-600 hover:bg-violet-500 text-white px-3 py-1.5 rounded-lg font-semibold transition-colors"
                      >
                        Create task →
                      </a>
                      <button onClick={() => setConvertResult(null)} className="text-xs text-gray-600 hover:text-white">
                        Dismiss
                      </button>
                    </div>
                  </div>
                )}

                {/* Agent cards */}
                <div className="mb-6">
                  <p className="text-xs text-gray-600 font-semibold uppercase tracking-wider mb-3">
                    Agent performance — {activeSections.length} active
                  </p>
                  {activeSections.length === 0 ? (
                    <div className="text-center py-12 text-gray-700 text-sm">No active agents this week</div>
                  ) : (
                    activeSections.map(s => (
                      <AgentCard key={s.agent_id} section={s} onConvert={convert} />
                    ))
                  )}

                  {idleSections.length > 0 && (
                    <details className="mt-2">
                      <summary className="text-xs text-gray-700 cursor-pointer hover:text-gray-500">
                        {idleSections.length} idle agent{idleSections.length !== 1 ? 's' : ''} — no activity this week
                      </summary>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {idleSections.map(s => (
                          <span key={s.agent_id} className="text-xs text-gray-700 bg-gray-900 px-2 py-1 rounded-full border border-gray-800">
                            {s.agent_name}
                          </span>
                        ))}
                      </div>
                    </details>
                  )}
                </div>

                {/* Feedback */}
                {!feedbackDone && (
                  <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
                    <FeedbackPanel reportId={selected.id} onDone={() => setFeedbackDone(true)} />
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
