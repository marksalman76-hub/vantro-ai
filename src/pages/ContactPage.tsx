'use client';

import { ArrowLeft } from 'lucide-react';

interface ContactCardProps {
  label: string;
  email: string;
  description: string;
}

function ContactCard({ label, email, description }: ContactCardProps) {
  return (
    <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: 20 }}>
      <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'oklch(0.60 0 0)', marginBottom: 8 }}>
        {label}
      </div>
      <a
        href={`mailto:${email}`}
        style={{ display: 'block', fontSize: 15, fontWeight: 500, color: 'oklch(0.97 0 0)', textDecoration: 'none', marginBottom: 6 }}
        onMouseEnter={e => { (e.currentTarget as HTMLAnchorElement).style.textDecoration = 'underline' }}
        onMouseLeave={e => { (e.currentTarget as HTMLAnchorElement).style.textDecoration = 'none' }}
      >
        {email}
      </a>
      <p style={{ fontSize: 13, lineHeight: 1.6, color: 'oklch(0.60 0 0)', margin: 0 }}>
        {description}
      </p>
    </div>
  );
}

export function ContactPage() {
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
          Contact
        </div>

        <h1 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 40, fontWeight: 700, color: 'oklch(0.97 0 0)', margin: '0 0 24px', lineHeight: 1.15 }}>
          Get in Touch
        </h1>

        <p style={{ fontSize: 16, lineHeight: 1.7, color: 'oklch(0.72 0 0)', marginBottom: 48 }}>
          Have a question, partnership inquiry, or want to see Vantro in action? We&apos;d love to hear from you.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <ContactCard
            label="General Inquiries"
            email="hello@vantro.ai"
            description="Questions about Vantro, the platform, or how to get started."
          />
          <ContactCard
            label="Sales"
            email="sales@vantro.ai"
            description="Pricing, enterprise plans, and custom deployments."
          />
          <ContactCard
            label="Support"
            email="support@vantro.ai"
            description="Help with your account or technical issues."
          />
        </div>
      </div>
    </div>
  );
}
