'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import GlassCard from '@/components/ui/glass-card';
import GlassButton from '@/components/ui/glass-button';
import Background3D from '@/components/ui/3d-background';

const AVATARS = [
  { id: 'avatar_alex',  name: 'Alex',  style: 'Professional male, business attire' },
  { id: 'avatar_sofia', name: 'Sofia', style: 'Professional female, modern style'  },
  { id: 'avatar_james', name: 'James', style: 'Casual male, friendly presenter'    },
  { id: 'avatar_maria', name: 'Maria', style: 'Casual female, energetic presenter' },
  { id: 'avatar_kai',   name: 'Kai',   style: 'Gender-neutral, minimalist style'   },
  { id: 'avatar_nova',  name: 'Nova',  style: 'Futuristic, tech-focused presenter' },
];

const VOICES = [
  { id: 'voice_natural',      name: 'Natural',      desc: 'Warm, conversational tone'  },
  { id: 'voice_professional', name: 'Professional', desc: 'Clear, authoritative tone'  },
  { id: 'voice_energetic',    name: 'Energetic',    desc: 'Upbeat, enthusiastic tone'  },
  { id: 'voice_calm',         name: 'Calm',         desc: 'Soothing, relaxed delivery' },
];

const LANGUAGES = ['English', 'Spanish', 'French', 'German', 'Portuguese', 'Italian', 'Japanese', 'Chinese'];
const TONES = ['professional', 'casual', 'enthusiastic', 'formal', 'educational'];

interface JobResult { id: string; status: string; message: string }

export default function CreatePage() {
  const router = useRouter();
  const [script,   setScript]   = useState('');
  const [avatarId, setAvatarId] = useState('avatar_alex');
  const [voiceId,  setVoiceId]  = useState('voice_natural');
  const [language, setLanguage] = useState('English');
  const [tone,     setTone]     = useState('professional');
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState('');
  const [result,   setResult]   = useState<JobResult | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) router.push('/login?redirect=/create');
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!script.trim()) { setError('Please enter a script'); return; }
    if (script.trim().length < 20) { setError('Script must be at least 20 characters'); return; }

    const token = localStorage.getItem('token');
    if (!token) { router.push('/login?redirect=/create'); return; }

    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/media-jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ avatar_id: avatarId, voice_id: voiceId, script: script.trim(), language, tone }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || 'Failed to submit. Please try again.'); return; }
      setResult(data);
    } catch {
      setError('Network error — please try again');
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6" style={{ backgroundColor: 'rgb(11,15,25)' }}>
        <Background3D />
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="max-w-md w-full">
          <GlassCard hover={false} className="text-center">
            <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6"
              style={{ background: 'linear-gradient(135deg,#10B981,#059669)', boxShadow: '0 0 30px rgba(16,185,129,0.4)' }}>
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Video queued!</h1>
            <p className="mb-1" style={{ color: 'rgb(203,213,225)' }}>{result.message}</p>
            <p className="text-xs mb-8" style={{ color: 'rgba(255,255,255,0.3)' }}>Job ID: {result.id}</p>
            <div className="flex flex-col gap-3">
              <Link href="/dashboard">
                <GlassButton variant="solid" size="md" className="w-full justify-center">View in dashboard</GlassButton>
              </Link>
              <GlassButton variant="glass" size="md" onClick={() => { setResult(null); setScript(''); }} className="w-full justify-center">
                Create another video
              </GlassButton>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'rgb(11,15,25)' }}>
      <Background3D />

      {/* Nav */}
      <nav className="px-6 py-4 flex items-center justify-between relative z-10"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.06)', backdropFilter: 'blur(12px)' }}>
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl flex items-center justify-center text-white font-black text-sm"
            style={{ background: 'linear-gradient(135deg,#3B82F6,#8B5CF6)', boxShadow: '0 0 20px rgba(59,130,246,0.4)' }}>V</div>
          <span className="font-bold text-white">Vantro<span className="text-blue-400">.ai</span></span>
        </Link>
        <Link href="/dashboard" className="text-sm transition-colors" style={{ color: 'rgba(255,255,255,0.4)' }}>
          ← Back to dashboard
        </Link>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-10 relative z-10">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Create a video</h1>
          <p style={{ color: 'rgb(203,213,225)' }}>Write your script, choose an avatar and voice, then hit generate.</p>
        </motion.div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Script */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
            <GlassCard hover={false} className="!p-5">
              <label className="block text-sm font-semibold text-white mb-3">
                Script <span className="text-blue-400">*</span>
              </label>
              <textarea
                value={script}
                onChange={e => setScript(e.target.value)}
                placeholder="Write what you want your AI avatar to say. E.g., 'Welcome to our new product launch…'"
                rows={8}
                className="w-full rounded-xl px-4 py-3 text-white text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.10)' }}
              />
              <div className="flex justify-between mt-2">
                <span className={`text-xs ${script.length > 0 && script.length < 20 ? 'text-red-400' : ''}`}
                  style={{ color: script.length > 0 && script.length < 20 ? undefined : 'rgba(255,255,255,0.3)' }}>
                  {script.length} characters
                </span>
                <span className="text-xs" style={{ color: 'rgba(255,255,255,0.3)' }}>50–500 words recommended</span>
              </div>
            </GlassCard>
          </motion.div>

          {/* Avatar */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <GlassCard hover={false} className="!p-5">
              <label className="block text-sm font-semibold text-white mb-4">Choose avatar</label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {AVATARS.map(av => (
                  <button
                    key={av.id}
                    type="button"
                    onClick={() => setAvatarId(av.id)}
                    className={`p-4 rounded-xl text-left transition-all ${
                      avatarId === av.id
                        ? 'border border-blue-500/60 bg-blue-500/10'
                        : 'border border-white/08 hover:border-white/20 hover:bg-white/[0.04]'
                    }`}
                  >
                    <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm mb-3"
                      style={{ background: 'linear-gradient(135deg,#3B82F6,#8B5CF6)' }}>
                      {av.name[0]}
                    </div>
                    <p className="font-medium text-sm text-white">{av.name}</p>
                    <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.4)' }}>{av.style}</p>
                  </button>
                ))}
              </div>
            </GlassCard>
          </motion.div>

          {/* Voice + language + tone */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <GlassCard hover={false} className="!p-5 space-y-6">
              <div>
                <label className="block text-sm font-semibold text-white mb-3">Voice style</label>
                <div className="grid grid-cols-2 gap-3">
                  {VOICES.map(v => (
                    <button
                      key={v.id}
                      type="button"
                      onClick={() => setVoiceId(v.id)}
                      className={`p-3 rounded-xl text-left transition-all ${
                        voiceId === v.id
                          ? 'border border-blue-500/60 bg-blue-500/10'
                          : 'border border-white/08 hover:border-white/20 hover:bg-white/[0.04]'
                      }`}
                    >
                      <p className="font-medium text-sm text-white">{v.name}</p>
                      <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.4)' }}>{v.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-white mb-2">Language</label>
                  <select
                    value={language}
                    onChange={e => setLanguage(e.target.value)}
                    className="w-full rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.10)' }}
                  >
                    {LANGUAGES.map(l => <option key={l} style={{ background: '#0B0F19' }}>{l}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-white mb-2">Tone</label>
                  <select
                    value={tone}
                    onChange={e => setTone(e.target.value)}
                    className="w-full rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 capitalize"
                    style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.10)' }}
                  >
                    {TONES.map(t => <option key={t} className="capitalize" style={{ background: '#0B0F19' }}>{t}</option>)}
                  </select>
                </div>
              </div>
            </GlassCard>
          </motion.div>

          {error && (
            <div className="px-4 py-3 rounded-xl text-sm text-red-300"
              style={{ background: 'rgba(239,68,68,0.10)', border: '1px solid rgba(239,68,68,0.25)' }}>
              {error}
            </div>
          )}

          <GlassButton
            type="submit"
            variant="solid"
            size="lg"
            disabled={loading || !script.trim()}
            className="w-full justify-center"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Submitting…
              </span>
            ) : 'Generate video'}
          </GlassButton>
        </form>
      </div>
    </div>
  );
}
