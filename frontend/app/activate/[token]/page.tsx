'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

interface Agent {
  id: string;
  name: string;
}

interface ActivationResult {
  activated: boolean;
  plan: string;
  agents: Agent[];
  message: string;
}

export default function ActivatePage() {
  const params = useParams();
  const token = params?.token as string | undefined;
  const router = useRouter();

  const [state, setState] = useState<'loading' | 'success' | 'error'>('loading');
  const [result, setResult] = useState<ActivationResult | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!token) return;

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai';

    fetch(`${API_URL}/api/billing/activate/${encodeURIComponent(token)}`)
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          setErrorMsg(data.detail || 'Activation failed');
          setState('error');
          return;
        }
        setResult(data);
        setState('success');
      })
      .catch(() => {
        setErrorMsg('Could not connect. Please try again.');
        setState('error');
      });
  }, [token]);

  if (state === 'loading') {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Activating your workspace...</p>
        </div>
      </div>
    );
  }

  if (state === 'error') {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center px-6">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-900/40 rounded-full mx-auto mb-6 flex items-center justify-center border border-red-800/50">
            <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-3">Activation failed</h1>
          <p className="text-gray-400 mb-8">{errorMsg}</p>
          <p className="text-sm text-gray-500 mb-6">
            If this link has expired or was already used, contact{' '}
            <a href="mailto:hello@vantro.ai" className="text-violet-400 hover:text-violet-300 underline">
              hello@vantro.ai
            </a>
          </p>
          <Link
            href="/dashboard"
            className="inline-block bg-white/10 hover:bg-white/15 text-white font-medium px-6 py-3 rounded-xl transition-all"
          >
            Go to dashboard
          </Link>
        </div>
      </div>
    );
  }

  const planLabel = (result?.plan ?? '').charAt(0).toUpperCase() + (result?.plan ?? '').slice(1);

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center px-6">
      <div className="max-w-lg w-full">
        {/* Success icon */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-600/20 rounded-full mx-auto mb-5 flex items-center justify-center border border-green-500/30">
            <svg className="w-10 h-10 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold mb-2">Workspace activated!</h1>
          <p className="text-gray-400">{result?.message}</p>
        </div>

        {/* Agents list */}
        {result?.agents && result.agents.length > 0 && (
          <div className="bg-[#13131f] border border-white/8 rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-2 h-2 rounded-full bg-violet-500" />
              <p className="text-sm font-semibold text-gray-300 uppercase tracking-wide">
                {planLabel} plan — your agents
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {result.agents.map((agent) => (
                <div
                  key={agent.id}
                  className="flex items-center gap-2.5 bg-white/4 rounded-lg px-3 py-2.5"
                >
                  <div className="w-6 h-6 rounded-md bg-violet-600/30 flex items-center justify-center flex-shrink-0">
                    <svg className="w-3.5 h-3.5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <span className="text-sm text-gray-200">{agent.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CTA */}
        <div className="text-center space-y-3">
          <Link
            href="/dashboard"
            className="inline-block w-full bg-violet-600 hover:bg-violet-500 text-white font-semibold py-3.5 rounded-xl transition-all text-center"
          >
            Go to dashboard
          </Link>
          <p className="text-xs text-gray-500">
            Monthly billing is active. Manage subscription in billing settings.
          </p>
        </div>
      </div>
    </div>
  );
}
