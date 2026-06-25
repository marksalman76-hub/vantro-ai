import { useState } from 'react';
import { X, Loader2 } from 'lucide-react';

interface Props { onClose: () => void; }

const TEAM_SIZES = ['1–10', '11–50', '51–200', '201–500', '500+'];

const field: React.CSSProperties = {
  width: '100%',
  background: 'rgba(255,255,255,0.06)',
  border: '1px solid rgba(255,255,255,0.10)',
  borderRadius: 10,
  padding: '10px 14px',
  fontSize: 13,
  color: 'oklch(0.97 0 0)',
  fontFamily: 'Inter, sans-serif',
  outline: 'none',
  boxSizing: 'border-box',
};

const label: React.CSSProperties = {
  fontFamily: 'Inter, sans-serif',
  fontSize: 12,
  fontWeight: 500,
  color: 'oklch(0.55 0 0)',
  marginBottom: 5,
  display: 'block',
};

export function SalesModal({ onClose }: Props) {
  const [form, setForm] = useState({ name: '', company: '', email: '', phone: '', teamSize: '11–50', message: '' });
  const [status, setStatus] = useState<'idle' | 'loading' | 'done' | 'error'>('idle');

  function set(k: string, v: string) { setForm(f => ({ ...f, [k]: v })); }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setStatus('loading');
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      setStatus(res.ok ? 'done' : 'error');
    } catch {
      setStatus('error');
    }
  }

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        background: 'rgba(0,0,0,0.75)',
        backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 16,
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          width: '100%', maxWidth: 520,
          background: 'oklch(0.18 0 0)',
          border: '1px solid rgba(255,255,255,0.10)',
          borderRadius: 20,
          boxShadow: '0 32px 100px rgba(0,0,0,0.7)',
          overflow: 'hidden',
          maxHeight: '90vh',
          display: 'flex', flexDirection: 'column',
        }}
      >
        {/* Header */}
        <div style={{
          padding: '22px 26px 18px',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
          display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <div>
            <p style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.30)', marginBottom: 5 }}>
              Enterprise
            </p>
            <h2 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 20, fontWeight: 700, color: 'oklch(0.97 0 0)', marginBottom: 3 }}>
              Talk to sales
            </h2>
            <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.38)', lineHeight: 1.5 }}>
              Tell us about your team and we'll be in touch within 24 hours.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.10)', borderRadius: '50%', width: 34, height: 34, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'rgba(255,255,255,0.50)', cursor: 'pointer', flexShrink: 0 }}
          >
            <X size={15} />
          </button>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 26px 26px' }}>
          {status === 'done' ? (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <div style={{ fontSize: 40, marginBottom: 16 }}>✓</div>
              <h3 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 18, fontWeight: 700, color: 'oklch(0.97 0 0)', marginBottom: 8 }}>Message sent</h3>
              <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.45)', lineHeight: 1.6 }}>
                We'll reach out to <strong style={{ color: 'oklch(0.80 0 0)' }}>{form.email}</strong> within 24 hours.
              </p>
            </div>
          ) : (
            <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={label}>Full name *</label>
                  <input required style={field} value={form.name} onChange={e => set('name', e.target.value)} placeholder="Jane Smith" />
                </div>
                <div>
                  <label style={label}>Company *</label>
                  <input required style={field} value={form.company} onChange={e => set('company', e.target.value)} placeholder="Acme Corp" />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={label}>Work email *</label>
                  <input required type="email" style={field} value={form.email} onChange={e => set('email', e.target.value)} placeholder="jane@acme.com" />
                </div>
                <div>
                  <label style={label}>Phone</label>
                  <input type="tel" style={field} value={form.phone} onChange={e => set('phone', e.target.value)} placeholder="+1 555 000 0000" />
                </div>
              </div>

              <div>
                <label style={label}>Team size *</label>
                <select
                  required
                  value={form.teamSize}
                  onChange={e => set('teamSize', e.target.value)}
                  style={{ ...field, appearance: 'none', WebkitAppearance: 'none', cursor: 'pointer' }}
                >
                  {TEAM_SIZES.map(s => (
                    <option key={s} value={s} style={{ background: 'oklch(0.18 0 0)' }}>{s} employees</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={label}>What are you looking to automate? *</label>
                <textarea
                  required
                  rows={4}
                  value={form.message}
                  onChange={e => set('message', e.target.value)}
                  placeholder="Tell us about your current workflows and what you'd like to hand off to AI agents…"
                  style={{ ...field, resize: 'vertical', lineHeight: 1.55 }}
                />
              </div>

              {status === 'error' && (
                <p style={{ fontSize: 12, color: 'oklch(0.65 0.18 25)', fontFamily: 'Inter, sans-serif' }}>
                  Something went wrong. Email us at <a href="mailto:hello@vantro.ai" style={{ color: 'inherit' }}>hello@vantro.ai</a>
                </p>
              )}

              <button
                type="submit"
                disabled={status === 'loading'}
                style={{
                  background: 'linear-gradient(180deg, #ffffff 0%, #d4d4d4 100%)',
                  color: 'oklch(0.12 0 0)',
                  border: 'none',
                  borderRadius: 100,
                  padding: '13px 26px',
                  fontFamily: 'Space Grotesk, sans-serif',
                  fontWeight: 700,
                  fontSize: 14,
                  cursor: status === 'loading' ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  opacity: status === 'loading' ? 0.7 : 1,
                  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.55), 0 4px 18px rgba(0,0,0,0.45)',
                  transition: 'opacity 0.15s',
                  marginTop: 4,
                }}
              >
                {status === 'loading' && <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />}
                {status === 'loading' ? 'Sending…' : 'Send message'}
              </button>
            </form>
          )}
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
