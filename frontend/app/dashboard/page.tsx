'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { SkeletonCard } from '@/components/Skeleton';

// Primitives
import MetricCard from '@/components/dashboard/MetricCard';
import ActionCard from '@/components/dashboard/ActionCard';
import StatusBadge from '@/components/dashboard/StatusBadge';

// Sections
import DashboardHeader from '@/components/dashboard/DashboardHeader';
import StatusStrip from '@/components/dashboard/StatusStrip';
import AlertsSection from '@/components/dashboard/AlertsSection';
import QuickLaunchSection from '@/components/dashboard/QuickLaunchSection';
import RecentJobsTable from '@/components/dashboard/RecentJobsTable';

// Fixed widget
import ThemeToggle from '@/components/dashboard/ThemeToggle';

// Suppress unused-import lint warnings — these are re-exported for consumers
void MetricCard;
void ActionCard;
void StatusBadge;

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

interface Announcement {
  id: string;
  title: string;
  body: string;
  affects: string | null;
  type: string;
  show_as: string;
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
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    const headers = { Authorization: `Bearer ${token}` };

    // Restore dismissed announcement IDs from localStorage
    try {
      const d = JSON.parse(localStorage.getItem('dismissed_announcements') || '[]');
      setDismissed(new Set(d));
    } catch { /* ignore */ }

    Promise.all([
      fetch('/api/workspace/credits', { headers }).then(r => r.ok ? r.json() : null),
      fetch('/api/agents/jobs?skip=0&limit=200', { headers }).then(r => r.ok ? r.json() : null),
      fetch('/api/platform/announcements', { headers }).then(r => r.ok ? r.json() : []),
    ]).then(([c, j, ann]) => {
      if (c) setCredits(c);
      if (j?.jobs) setJobs(j.jobs);
      if (Array.isArray(ann)) setAnnouncements(ann);
    }).finally(() => setLoading(false));
  }, [router]);

  const onDismiss = (id: string) => {
    const next = new Set(dismissed).add(id);
    setDismissed(next);
    localStorage.setItem('dismissed_announcements', JSON.stringify(Array.from(next)));
  };

  const onSignOut = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  // Derived state
  const completedThisMonth = jobs.filter(
    j => j.status === 'completed' && isThisMonth(j.completed_at || j.created_at)
  ).length;

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

  const pendingApprovals = jobs.filter(j =>
    j.status === 'pending_approval' || j.status === 'pending_financial_review'
  ).length;

  const failedJobs = jobs.filter(j => j.status === 'failed').length;

  if (loading) {
    return (
      <div className="p-8 max-w-5xl" style={{ paddingTop: '6rem' }}>
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

  return (
    <>
      {/* Sticky header — fixed, z-index 100 */}
      <DashboardHeader
        credits={credits}
        pendingApprovals={pendingApprovals}
        failedJobs={failedJobs}
        onSignOut={onSignOut}
      />

      {/* Main content — offset by header height */}
      <div className="p-8 max-w-5xl" style={{ paddingTop: '6rem' }}>

        {/* Collapsible metrics strip */}
        <StatusStrip
          credits={credits}
          completedThisMonth={completedThisMonth}
          pendingApprovals={pendingApprovals}
          topAgents={topAgents}
        />

        {/* Announcements + action cards */}
        <div className="mb-6">
          <AlertsSection
            announcements={announcements}
            pendingApprovals={pendingApprovals}
            failedJobs={failedJobs}
            dismissed={dismissed}
            onDismiss={onDismiss}
          />
        </div>

        {/* Quick-launch grid */}
        <QuickLaunchSection />

        {/* Job history table */}
        <RecentJobsTable jobs={jobs} />
      </div>

      {/* Fixed bottom-left theme toggle */}
      <ThemeToggle />
    </>
  );
}
