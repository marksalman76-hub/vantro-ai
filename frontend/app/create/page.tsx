'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const AVATARS = [
  { id: 'avatar_alex',  name: 'Alex',    style: 'Professional male, business attire' },
  { id: 'avatar_sofia', name: 'Sofia',   style: 'Professional female, modern style'  },
  { id: 'avatar_james', name: 'James',   style: 'Casual male, friendly presenter'    },
  { id: 'avatar_maria', name: 'Maria',   style: 'Casual female, energetic presenter' },
  { id: 'avatar_kai',   name: 'Kai',     style: 'Gender-neutral, minimalist style'   },
  { id: 'avatar_nova',  name: 'Nova',    style: 'Futuristic, tech-focused presenter' },
];

const VOICES = [
  { id: 'voice_natural',     name: 'Natural',     desc: 'Warm, conversational tone' },
  { id: 'voice_professional',name: 'Professional', desc: 'Clear, authoritative tone' },
  { id: 'voice_energetic',   name: 'Energetic',   desc: 'Upbeat, enthusiastic tone'  },
  { id: 'voice_calm',        name: 'Calm',        desc: 'Soothing, relaxed delivery' },
];

const LANGUAGES = ['English', 'Spanish', 'French', 'German', 'Portuguese', 'Italian', 'Japanese', 'Chinese'];
const TONES = ['professional', 'casual', 'enthusiastic', 'formal', 'educational'];

interface JobResult {
  id: string;
  status: string;
  message: string;
}

export default function CreatePage() {
  const router = useRouter();
  const [script, setScript] = useState('');
  const [avatarId, setAvatarId] = useState('avatar_alex');
  const [voiceId, setVoiceId] = useState('voice_natural');
  const [language, setLanguage] = useState('English');
  const [tone, setTone] = useState('professional');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<JobResult | null>(null);

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
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center px-6">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-600 rounded-full mx-auto mb-6 flex items-center justify-center">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-3">Video queued!</h1>
          <p className="text-gray-400 mb-2">{result.message}</p>
          <p className="text-gray-500 text-sm mb-8">Job ID: {result.id}</p>
          <div className="flex flex-col gap-3">
            <Link href="/dashboard" className="bg-purple-600 hover:bg-purple-700 text-white font-semibold px-8 py-3 rounded-xl transition-all">
              View in dashboard
            </Link>
            <button
              onClick={() => { setResult(null); setScript(''); }}
              className="text-gray-400 hover:text-white text-sm"
            >
              Create another video
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2">
          <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
          <span className="font-bold">Vantro<span className="text-violet-400">.ai</span></span>
        </Link>
        <Link href="/dashboard" className="text-gray-400 hover:text-white text-sm">← Back to dashboard</Link>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Create a video</h1>
          <p className="text-gray-400">Write your script, choose an avatar and voice, then hit generate.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Script */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
            <label className="block text-sm font-semibold mb-3">
              Script <span className="text-purple-400">*</span>
            </label>
            <textarea
              value={script}
              onChange={(e) => setScript(e.target.value)}
              placeholder="Write what you want your AI avatar to say. E.g., 'Welcome to our new product launch. Today I want to walk you through...'"
              rows={8}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none text-sm"
            />
            <div className="flex justify-between mt-2">
              <span className={`text-xs ${script.length < 20 && script.length > 0 ? 'text-red-400' : 'text-gray-500'}`}>
                {script.length} characters
              </span>
              <span className="text-xs text-gray-500">Recommended: 50–500 words</span>
            </div>
          </div>

          {/* Avatar selection */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
            <label className="block text-sm font-semibold mb-4">Choose avatar</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {AVATARS.map((av) => (
                <button
                  key={av.id}
                  type="button"
                  onClick={() => setAvatarId(av.id)}
                  className={`p-4 rounded-xl border text-left transition-all ${
                    avatarId === av.id
                      ? 'border-purple-500 bg-purple-950/40'
                      : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                  }`}
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center text-white font-bold text-sm mb-3">
                    {av.name[0]}
                  </div>
                  <p className="font-medium text-sm">{av.name}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{av.style}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Voice + language + tone */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-6">
            <div>
              <label className="block text-sm font-semibold mb-3">Voice style</label>
              <div className="grid grid-cols-2 gap-3">
                {VOICES.map((v) => (
                  <button
                    key={v.id}
                    type="button"
                    onClick={() => setVoiceId(v.id)}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      voiceId === v.id
                        ? 'border-purple-500 bg-purple-950/40'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }`}
                  >
                    <p className="font-medium text-sm">{v.name}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{v.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Language</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:border-purple-500"
                >
                  {LANGUAGES.map((l) => <option key={l}>{l}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Tone</label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:border-purple-500"
                >
                  {TONES.map((t) => <option key={t} className="capitalize">{t}</option>)}
                </select>
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-xl text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !script.trim()}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-xl transition-all text-base"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Submitting...
              </span>
            ) : 'Generate video'}
          </button>
        </form>
      </div>
    </div>
  );
}
