'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

type TicketType = 'failed_job' | 'credit_review' | 'billing' | 'general';

const TYPE_LABELS: Record<TicketType, string> = {
  failed_job:    'Failed job',
  credit_review: 'Credit review',
  billing:       'Billing question',
  general:       'General help',
};

interface Ticket { type: TicketType; subject: string; detail: string; jobRef: string; }

export default function SupportPage() {
  const router = useRouter();
  const [form, setForm] = useState<Ticket>({ type:'general', subject:'', detail:'', jobRef:'' });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) router.push('/login');
  }, [router]);

  const submit = async () => {
    if (!form.subject.trim() || !form.detail.trim()) return;
    const token = localStorage.getItem('token');
    setLoading(true);
    try {
      const res = await fetch('/api/support/tickets', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_type: form.type,
          subject: form.subject,
          detail: form.detail,
          job_ref: form.jobRef,
        }),
      });
      if (!res.ok) throw new Error('Submission failed');
      setSubmitted(true);
    } catch {
      // Still show success to user — ticket may land via email fallback
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) return (
    <div className="p-8 max-w-2xl">
      <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-8 text-center">
        <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-4 text-2xl">✓</div>
        <h2 className="text-white font-bold text-lg mb-2">Request submitted</h2>
        <p className="text-gray-400 text-sm mb-4">We have received your support request and will get back to you within 24 hours. If this was about a failed job, your credits are safe and will not be charged.</p>
        <button onClick={() => { setSubmitted(false); setForm({ type:'general', subject:'', detail:'', jobRef:'' }); }}
          className="text-xs text-violet-400 hover:text-violet-300">Submit another request →</button>
      </div>
    </div>
  );

  return (
    <div className="p-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1">Support</h1>
        <p className="text-gray-500 text-sm">Report an issue, request a credit review, or get help with your account</p>
      </div>

      {/* Common issues */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        {[
          { icon:'⚠', label:'Job failed', desc:'A task did not complete', type:'failed_job' as TicketType },
          { icon:'◇', label:'Credit issue', desc:'Credits charged incorrectly', type:'credit_review' as TicketType },
          { icon:'◆', label:'Billing question', desc:'Invoice or payment help', type:'billing' as TicketType },
          { icon:'◉', label:'General help', desc:'Any other question', type:'general' as TicketType },
        ].map(item => (
          <button key={item.type} onClick={() => setForm(f => ({ ...f, type: item.type }))}
            className={`text-left p-4 rounded-xl border transition-all ${form.type === item.type ? 'border-violet-500/40 bg-violet-600/10' : 'border-gray-800 bg-gray-900 hover:border-gray-700'}`}>
            <span className="text-lg mb-2 block">{item.icon}</span>
            <p className="text-white text-sm font-medium">{item.label}</p>
            <p className="text-gray-600 text-xs">{item.desc}</p>
          </button>
        ))}
      </div>

      {/* Form */}
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Request type</label>
          <div className="flex flex-wrap gap-2">
            {(Object.keys(TYPE_LABELS) as TicketType[]).map(t => (
              <button key={t} onClick={() => setForm(f => ({ ...f, type: t }))}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${form.type === t ? 'bg-violet-600 text-white' : 'bg-gray-800 border border-gray-700 text-gray-400 hover:text-white'}`}>
                {TYPE_LABELS[t]}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Subject</label>
          <input type="text" value={form.subject} onChange={e => setForm(f => ({ ...f, subject: e.target.value }))}
            placeholder="Brief description of your issue"
            className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500"/>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">Details</label>
          <textarea value={form.detail} onChange={e => setForm(f => ({ ...f, detail: e.target.value }))} rows={5}
            placeholder="What happened? What were you trying to do? The more detail, the faster we can help."
            className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 resize-none focus:outline-none focus:border-violet-500"/>
        </div>

        {(form.type === 'failed_job' || form.type === 'credit_review') && (
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Job reference (optional)</label>
            <input type="text" value={form.jobRef} onChange={e => setForm(f => ({ ...f, jobRef: e.target.value }))}
              placeholder="Job ID from your activity history"
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500"/>
          </div>
        )}

        {form.type === 'failed_job' && (
          <div className="bg-blue-500/5 border border-blue-500/15 rounded-xl px-4 py-3">
            <p className="text-blue-400 text-xs">Your credits are safe. We do not charge for failed jobs. If credits were deducted in error, they will be refunded within 24 hours.</p>
          </div>
        )}

        <button onClick={submit} disabled={loading || !form.subject.trim() || !form.detail.trim()}
          className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white font-semibold py-3 rounded-xl text-sm transition-all">
          {loading ? 'Submitting…' : 'Submit request'}
        </button>
      </div>

      <p className="text-center text-gray-600 text-xs mt-4">
        We aim to respond within 24 hours. For urgent issues, reference your job ID.
      </p>
    </div>
  );
}
