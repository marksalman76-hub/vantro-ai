'use client';

import { ArrowLeft } from 'lucide-react';

export function AboutPage() {
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
          Company
        </div>

        <h1 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 40, fontWeight: 700, color: 'oklch(0.97 0 0)', margin: '0 0 12px', lineHeight: 1.15 }}>
          About Vantro
        </h1>

        <p style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 13, color: 'oklch(0.60 0 0)', marginBottom: 40 }}>
          Last updated: June 25, 2026
        </p>

        <p style={{ fontSize: 16, lineHeight: 1.7, color: 'oklch(0.72 0 0)', marginBottom: 56 }}>
          Vantro was founded on a simple belief: every company deserves an AI workforce that works as hard as they do. We build autonomous AI agents that handle the work, so your team can focus on what matters.
        </p>

        <section style={{ marginBottom: 48 }}>
          <h2 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 22, fontWeight: 600, color: 'oklch(0.97 0 0)', margin: '0 0 16px' }}>
            Our Mission
          </h2>
          <p style={{ fontSize: 15, lineHeight: 1.7, color: 'oklch(0.72 0 0)', margin: 0 }}>
            We&apos;re building the infrastructure for the autonomous business. Our agents don&apos;t just automate tasks — they reason, adapt, and collaborate to run entire business functions end-to-end.
          </p>
        </section>

        <section style={{ marginBottom: 56 }}>
          <h2 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 22, fontWeight: 600, color: 'oklch(0.97 0 0)', margin: '0 0 16px' }}>
            The Team
          </h2>
          <p style={{ fontSize: 15, lineHeight: 1.7, color: 'oklch(0.72 0 0)', margin: 0 }}>
            Vantro is built by a team of engineers, researchers, and operators who have worked at leading AI labs and enterprise software companies. We&apos;re backed by top-tier investors and committed to building AI that businesses can actually trust.
          </p>
        </section>

        <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: 24 }}>
          <p style={{ fontSize: 14, color: 'oklch(0.72 0 0)', margin: 0 }}>
            Want to learn more? Reach us at{' '}
            <a
              href="mailto:hello@vantro.ai"
              style={{ color: 'oklch(0.97 0 0)', textDecoration: 'none' }}
              onMouseEnter={e => { (e.currentTarget as HTMLAnchorElement).style.textDecoration = 'underline' }}
              onMouseLeave={e => { (e.currentTarget as HTMLAnchorElement).style.textDecoration = 'none' }}
            >
              hello@vantro.ai
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
