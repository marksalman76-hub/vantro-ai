'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface ApprovalJob { id: string; agent_name: string; status: string; hitl_level: string; credits_used: number; created_at: string | null; output: string | null; error_message: string | null; }

export default function ApprovalsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<ApprovalJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }
    fetch('/api/agents/jobs', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.jobs) setJobs(d.jobs.filter((j: ApprovalJob) => j.status === 'pending_approval' || j.status === 'rejected')); })
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <div className="flex items-center justify-center h-screen"><div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"/></div>;

  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-2xl font-bold">Approvals</h1>
          {jobs.filter(j => j.status === 'pending_approval').length > 0 && (
            <span className="bg-orange-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
              {jobs.filter(j => j.status === 'pending_approval').length}
            </span>
          )}
        </div>
        <p className="text-gray-500 text-sm">Jobs that require your review or are awaiting admin approval</p>
      </div>

      {jobs.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-12 text-center">
          <p className="text-emerald-400 text-sm font-medium mb-2">No pending approvals</p>
          <p className="text-gray-600 text-xs">All your jobs are processing or completed. Check your <Link href="/dashboard/assets" className="text-violet-400">outputs</Link> for ready results.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map(job => (
            <div key={job.id} className={`bg-gray-900 border rounded-2xl p-5 ${job.status === 'pending_approval' ? 'border-orange-500/20' : 'border-gray-800'}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                      job.status === 'pending_approval' ? 'text-orange-400 bg-orange-500/10 border-orange-500/20' : 'text-red-400 bg-red-500/10 border-red-500/20'
                    }`}>
                      {job.status === 'pending_approval' ? 'Awaiting admin approval' : 'Declined'}
                    </span>
                    <span className="text-[10px] text-gray-600 bg-gray-800 px-2 py-0.5 rounded-full">{job.hitl_level}</span>
                  </div>
                  <p className="text-white text-sm font-medium mb-1">{job.agent_name}</p>
                  <p className="text-xs text-gray-500">{job.created_at ? new Date(job.created_at).toLocaleString() : '—'}</p>
                </div>
              </div>
              {job.status === 'pending_approval' && (
                <div className="mt-4 bg-orange-500/5 border border-orange-500/15 rounded-xl px-4 py-3">
                  <p className="text-orange-400 text-xs font-medium mb-0.5">Your request is being reviewed</p>
                  <p className="text-gray-500 text-xs">This agent executes an action that requires admin approval. You will be notified when it completes. Your credits are reserved and will only be charged if approved.</p>
                </div>
              )}
              {job.status === 'rejected' && (
                <div className="mt-4 bg-red-500/5 border border-red-500/15 rounded-xl px-4 py-3">
                  <p className="text-red-400 text-xs font-medium mb-0.5">This request was not approved</p>
                  <p className="text-gray-500 text-xs mb-2">{job.error_message || 'Your credits were not charged. Please contact support if you have questions.'}</p>
                  <Link href="/dashboard/support" className="text-xs text-violet-400 hover:text-violet-300">Contact support →</Link>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
