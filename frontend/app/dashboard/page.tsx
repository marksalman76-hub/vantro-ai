'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { SkeletonCard } from '@/components/Skeleton';

interface CreditsData {
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  tier: string;
}

interface HistoryJob {
  id: string;
  agent_id: string;
  agent_name: string;
  status: string;
  credits_used: number;
  created_at: string | null;
  completed_at: string | null;
}

interface AgentUsage {
  agent_id: string;
  agent_name: string;
  count: number;
}

const CLIENT_STATUS: Record<string, string> = {
  pending:                  'Waiting to start',
  queued:                   'Waiting to start',
  running:                  'In progress',
  processing:               'In progress',
  approved:                 'In progress',
  pending_approval:         'Needs your approval',
  pending_financial_review: 'Needs your approval',
  completed:                'Ready',
  failed:                   'Could not complete',
  cancelled:                'Cancelled',
  rejected:                 'Not approved',
};

const STATUS_STYLES: Record<string, string> = {
  'Waiting to start':    'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  'In progress':         'text-blue-400 bg-blue-500/10 border-blue-500/20',
  'Needs your approval': 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  'Ready':               'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  'Could not complete':  'text-red-400 bg-red-500/10 border-red-500/20',
  'Cancelled':           'text-gray-500 bg-gray-700/20 border-gray-700',
  'Not approved':        'text-red-400 bg-red-500/10 border-red-500/20',
};

function MetricCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 flex flex-col gap-1">
      <p className="text-xs text-gray-500 font-medium">{label}</p>
      <p className={`text-2xl font-bold ${color || 'text-white'}`}>{value}</p>
      {sub && <p className="text-xs text-gray-600">{sub}</p>}
    </div>
  );
}

function AgentBar({ name, count, max }: { name: string; count: number; max: number }) {
  const pct = max > 0 ? Math.round((count / max) * 100) : 0;
  return (
    <div className="flex items-center gap-3">
      <p className="text-xs text-gray-400 w-32 truncate shrink-0">{name}</p>
      <div className="flex-1 bg-gray-800 rounded-full h-1.5">
        <div
          className="h-1.5 rounded-full bg-violet-500"
          style={{ width: `${pct}%`, boxShadow: '0 0 6px rgba(124,58,237,0.5)' }}
        />
      </div>
      <span className="text-xs text-gray-500 w-6 text-right shrink-0">{count}</span>
    </div>
  );
}

function isThisMonth(dateStr: string | null): boolean {
  if (!dateStr) return false;
  const d = new Date(dateStr);
  const now = new Date();
  return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
}

export default function DashboardPage() {
  const router = useRouter();
  const [credits, setCredits] = useState<CreditsData | null>(null);
  const [jobs, setJobs] = useState<HistoryJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    const headers = { Authorization: `Bearer ${token}` };

    Promise.all([
      fetch('/api/workspace/credits', { headers }).then(r => r.ok ? r.json() : null),
      fetch('/api/agents/jobs?skip=0&limit=200', { headers }).then(r => r.ok ? r.json() : null),
    ]).then(([c, j]) => {
      if (c) setCredits(c);
      if (j?.jobs) setJobs(j.jobs);
    }).finally(() => setLoading(false));
  }, [router]);

  const completedThisMonth = jobs.filter(
    j => j.status === 'completed' && isThisMonth(j.completed_at || j.created_at)
  ).length;

  // Top 3 agents by usage
  const agentCounts: Record<string, AgentUsage> = {};
  for (const job of jobs) {
    if (!agentCounts[job.agent_id]) {
      agentCounts[job.agent_id] = { agent_id: job.agent_id, agent_name: job.agent_name, count: 0 };
    }
    agentCounts[job.agent_id].count++;
  }
  const topAgents = Object.values(agentCounts)
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);
  const maxCount = topAgents[0]?.count || 1;

  const creditsRemaining = credits
    ? (credits.remaining_credits ?? credits.total_credits - credits.used_credits)
    : null;

  if (loading) {
    return (
      <div className="p-8 max-w-5xl">
        <div className="mb-8">
          <div className="animate-pulse bg-gray-800 rounded h-7 w-36 mb-2" />
          <div className="animate-pulse bg-gray-800 rounded h-4 w-56" />
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  const pendingApprovals = jobs.filter(j =>
    j.status === 'pending_approval' || j.status === 'pending_financial_review'
  ).length;
  const failedJobs = jobs.filter(j => j.status === 'failed').length;

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold mb-1">Dashboard</h1>
          <p className="text-gray-500 text-sm">Your AI agent workspace at a glance</p>
        </div>
        {credits?.tier && (
          <span className="shrink-0 text-xs font-semibold px-3 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 capitalize mt-1">
            {credits.tier} plan
          </span>
        )}
      </div>

      {/* Pending approvals / failed notice */}
      {(pendingApprovals > 0 || failedJobs > 0) && (
        <div className="flex gap-3 mb-6 flex-wrap">
          {pendingApprovals > 0 && (
            <Link
              href="/dashboard/approvals"
              className="flex-1 min-w-[180px] bg-orange-500/10 border border-orange-500/20 hover:border-orange-500/40 rounded-2xl px-4 py-3 flex items-center justify-between transition-colors"
            >
              <div>
                <p className="text-orange-300 text-xs font-semibold">Needs your approval</p>
                <p className="text-orange-200/60 text-[10px] mt-0.5">Review before we continue</p>
              </div>
              <span className="text-2xl font-bold text-orange-400">{pendingApprovals}</span>
            </Link>
          )}
          {failedJobs > 0 && (
            <Link
              href="/dashboard/jobs?filter=failed"
              className="flex-1 min-w-[180px] bg-red-500/10 border border-red-500/15 hover:border-red-500/30 rounded-2xl px-4 py-3 flex items-center justify-between transition-colors"
            >
              <div>
                <p className="text-red-300 text-xs font-semibold">Could not complete</p>
                <p className="text-red-200/60 text-[10px] mt-0.5">Retry or contact support</p>
              </div>
              <span className="text-2xl font-bold text-red-400">{failedJobs}</span>
            </Link>
          )}
        </div>
      )}


      {/* Metrics row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          label="Credits remaining"
          value={creditsRemaining !== null ? creditsRemaining.toLocaleString() : '—'}
          sub={credits ? `of ${credits.total_credits.toLocaleString()} total` : undefined}
          color={
            creditsRemaining !== null && credits && credits.total_credits > 0
              ? (creditsRemaining / credits.total_credits) < 0.2
                ? 'text-red-400'
                : (creditsRemaining / credits.total_credits) < 0.5
                ? 'text-amber-400'
                : 'text-emerald-400'
              : 'text-white'
          }
        />
        <MetricCard
          label="Jobs completed this month"
          value={completedThisMonth}
          sub="completed status"
          color="text-violet-400"
        />
        <MetricCard
          label="Next billing date"
          value="—"
          sub="Manage in Billing"
        />
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 flex flex-col gap-2">
          <p className="text-xs text-gray-500 font-medium">Top agents used</p>
          {topAgents.length === 0 ? (
            <p className="text-xs text-gray-600 mt-2">No jobs run yet</p>
          ) : (
            <div className="flex flex-col gap-2 mt-1">
              {topAgents.map(a => (
                <AgentBar key={a.agent_id} name={a.agent_name} count={a.count} max={maxCount} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {[
          { href: '/dashboard/agents',  icon: '◆', label: 'Run an agent',       desc: 'Launch a task with any active agent'   },
          { href: '/dashboard/library', icon: '▣', label: 'Output library',      desc: 'Browse and copy past agent outputs'    },
          { href: '/dashboard/reports', icon: '◈', label: 'Weekly report',       desc: 'Performance summary and insights'      },
          { href: '/dashboard/brand',   icon: '◎', label: 'Brand profile',       desc: 'Feed your brand context to agents'     },
          { href: '/dashboard/billing', icon: '◇', label: 'Billing & credits',   desc: 'Top up credits or manage your plan'    },
          { href: '/dashboard/settings',icon: '◌', label: 'Settings',            desc: 'Integrations, notifications, security' },
        ].map(item => (
          <Link
            key={item.href}
            href={item.href}
            className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-2xl p-5 transition-all group"
          >
            <div className="flex items-center gap-3 mb-2">
              <span className="text-lg text-violet-400 group-hover:text-violet-300 transition-colors">{item.icon}</span>
              <p className="font-medium text-sm text-white">{item.label}</p>
            </div>
            <p className="text-xs text-gray-600">{item.desc}</p>
          </Link>
        ))}
      </div>

      {/* Recent jobs */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
          <h2 className="font-semibold text-white text-sm">Recent jobs</h2>
          <Link href="/dashboard/jobs" className="text-xs text-violet-400 hover:text-violet-300 font-medium">
            View all →
          </Link>
        </div>
        {jobs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-sm mb-3">No jobs yet</p>
            <Link href="/dashboard/agents" className="text-xs text-violet-400 hover:text-violet-300 font-medium">
              Run your first agent →
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-800/60">
            {jobs.slice(0, 10).map(job => (
              <div key={job.id} className="flex items-center gap-4 px-6 py-3 hover:bg-gray-800/30 transition-colors">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-medium truncate">{job.agent_name}</p>
                  <p className="text-xs text-gray-600">
                    {job.created_at ? new Date(job.created_at).toLocaleString() : '—'}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${
                      STATUS_STYLES[CLIENT_STATUS[job.status]] || 'text-gray-400 bg-gray-800 border-gray-700'
                    }`}
                  >
                    {CLIENT_STATUS[job.status] || 'In progress'}
                  </span>
                  {job.credits_used > 0 && (
                    <span className="text-[10px] text-gray-600">{job.credits_used}cr</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
