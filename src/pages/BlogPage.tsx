'use client';

import { useState } from 'react';
import { ArrowLeft } from 'lucide-react';

export function BlogPage() {
  const [email, setEmail] = useState('');

  function handleSubscribe() {
    alert("Thanks! We'll be in touch.");
  }

  return (
    <div style={{ backgroundColor: 'oklch(0.12 0 0)', minHeight: '100vh', fontFamily: 'Inter, sans-serif', color: 'oklch(0.72 0 0)' }}>
      <div style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', padding: '20px 48px', display: 'flex', alignItems: 'center' }}>
        <a
          href="/"
          style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'oklch(0.70 0 0)', textDecoration: 'none', fontSize: 14, transition: 'color 0.15s' }}
          onMouseEnter={e => { (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.97 0 0)' }}
          onMouseLeave={e => { (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.70 0 0)' }}
        >
          <ArrowLeft size={16} />
          <span style={{ marginLeft: 4 }}>Back to Vantro.ai</span>
        </a>
      </div>

      <div style={{ maxWidth: 720, margin: '0 auto', padding: '72px 48px 120px' }}>
        <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'oklch(0.60 0 0)', marginBottom: 24 }}>
          Blog
        </div>

        <h1 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 40, fontWeight: 700, color: 'oklch(0.97 0 0)', margin: '0 0 24px', lineHeight: 1.15 }}>
          From the Team
        </h1>

        <p style={{ fontSize: 16, lineHeight: 1.7, color: 'oklch(0.72 0 0)', marginBottom: 56 }}>
          Thoughts on AI, autonomous systems, and the future of work.
        </p>

        <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: 32 }}>
          <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 20, color: 'oklch(0.60 0 0)', marginBottom: 16 }}>
            ✦
          </div>

          <h2 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 20, fontWeight: 600, color: 'oklch(0.97 0 0)', margin: '0 0 10px' }}>
            Posts coming soon
          </h2>

          <p style={{ fontSize: 14, lineHeight: 1.6, color: 'oklch(0.72 0 0)', margin: '0 0 24px' }}>
            We&apos;re working on our first articles. Subscribe to be notified when we publish.
          </p>

          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="Your email"
              style={{
                flex: '1 1 200px',
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.12)',
                borderRadius: 8,
                padding: '10px 14px',
                fontSize: 14,
                color: 'oklch(0.97 0 0)',
                outline: 'none',
                fontFamily: 'Inter, sans-serif',
              }}
            />
            <button
              onClick={handleSubscribe}
              style={{
                background: 'oklch(0.97 0 0)',
                color: 'oklch(0.12 0 0)',
                border: 'none',
                borderRadius: 999,
                padding: '10px 22px',
                fontSize: 14,
                fontWeight: 600,
                cursor: 'pointer',
                fontFamily: 'Inter, sans-serif',
                whiteSpace: 'nowrap',
              }}
            >
              Subscribe
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
