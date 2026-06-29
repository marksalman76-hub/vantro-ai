'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { SkeletonCard } from '@/components/Skeleton';

// Redesign components
import MetricCard from '@/components/dashboard/MetricCard';
import ActionCard from '@/components/dashboard/ActionCard';
import StatusBadge from '@/components/dashboard/StatusBadge';
import DashboardHeader from '@/components/dashboard/DashboardHeader';
import StatusStrip from '@/components/dashboard/StatusStrip';
import AlertsSection from '@/components/dashboard/AlertsSection';
import QuickLaunchSection from '@/components/dashboard/QuickLaunchSection';
import RecentJobsTable, { HistoryJob } from '@/components/dashboard/RecentJobsTable';
import ThemeToggle from '@/components/dashboard/ThemeToggle';

interface AdminCredits {
  total_credits?: number;
  used_credits?: number;
  remaining_credits?: number;
  tier?: string;
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

export default function AdminDashboard() {
  const router = useRouter();
  const [credits, setCredits] = useState<AdminCredits | null>(null);
  const [jobs, setJobs] = useState<HistoryJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  interface RawJob {
    id: string;
    agent_id?: string;
    agent_name?: string;
    status: string;
    credits_used?: number;
    created_at: string | null;
    completed_at: string | null;
  }

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) { router.push('/admin-login'); return; }

    const headers = { Authorization: `Bearer ${token}` };

    try {
      const d = JSON.parse(localStorage.getItem('dismissed_announcements') || '[]');
      setDismissed(new Set(d));
    } catch { /* ignore */ }

    Promise.all([
      fetch('/api/admin/stats', { headers }).then(r => r.ok ? r.json() : null),
      fetch('/api/admin/jobs', { headers }).then(r => r.ok ? r.json() : null),
      fetch('/api/platform/announcements', { headers }).then(r => r.ok ? r.json() : []),
    ]).then(([c, j, ann]) => {
      if (c) setCredits(c as AdminCredits);
      if (j?.jobs) {
        const mapped: HistoryJob[] = (j.jobs as RawJob[]).map(job => ({
          id: job.id,
          agent_id: job.agent_id || 'unknown',
          agent_name: job.agent_name || 'Unknown Agent',
          status: job.status,
          credits_used: job.credits_used || 0,
          created_at: job.created_at,
          completed_at: job.completed_at,
        }));
        setJobs(mapped);
      }
      if (Array.isArray(ann)) setAnnouncements(ann);
    }).finally(() => setLoading(false));
  }, [router]);

  const onDismiss = (id: string) => {
    const next = new Set(dismissed).add(id);
    setDismissed(next);
    localStorage.setItem('dismissed_announcements', JSON.stringify(Array.from(next)));
  };

  const onSignOut = () => {
    localStorage.removeItem('admin_token');
    router.push('/admin-login');
  };

  const completedThisMonth = jobs.filter(
    j => j.status === 'completed' && isThisMonth(j.completed_at || j.created_at)
  ).length;

  const agentCounts: Record<string, AgentUsage> = {};
  for (const job of jobs) {
    if (job.agent_id) {
      if (!agentCounts[job.agent_id]) {
        agentCounts[job.agent_id] = { agent_id: job.agent_id, agent_name: job.agent_name || 'Unknown', count: 0 };
      }
      agentCounts[job.agent_id].count++;
    }
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
      <DashboardHeader
        credits={credits ? {
          total_credits: credits.total_credits ?? 0,
          used_credits: credits.used_credits ?? 0,
          remaining_credits: credits.remaining_credits ?? 0,
        } : null}
        pendingApprovals={pendingApprovals}
        failedJobs={failedJobs}
        onSignOut={onSignOut}
      />

      <div className="p-8 max-w-5xl" style={{ paddingTop: '6rem' }}>
        <StatusStrip
          credits={credits ? {
            total_credits: credits.total_credits ?? 0,
            used_credits: credits.used_credits ?? 0,
            remaining_credits: credits.remaining_credits ?? 0,
            tier: credits.tier ?? 'enterprise',
          } : null}
          completedThisMonth={completedThisMonth}
          pendingApprovals={pendingApprovals}
          topAgents={topAgents}
        />

        <div className="mb-6">
          <AlertsSection
            announcements={announcements}
            pendingApprovals={pendingApprovals}
            failedJobs={failedJobs}
            dismissed={dismissed}
            onDismiss={onDismiss}
          />
        </div>

        <QuickLaunchSection />

        <RecentJobsTable jobs={jobs} />
      </div>

      <ThemeToggle />
    </>
  );
}
