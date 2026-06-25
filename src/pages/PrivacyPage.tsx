'use client';

import { ArrowLeft } from 'lucide-react';

const SECTIONS = [
  {
    title: 'Information We Collect',
    body: `We collect information you provide directly to us when you create an account, use our services, or contact us for support. This includes your name, email address, billing information, and any other information you choose to provide.\n\nWe also automatically collect certain information when you use Vantro, including log data (IP address, browser type, pages visited), device information, and usage data about how you interact with our AI agents.`,
  },
  {
    title: 'How We Use Your Information',
    body: `We use the information we collect to provide, maintain, and improve our services; process transactions and send related information; send technical notices, updates, and support messages; respond to your comments and questions; and monitor and analyze usage patterns to improve user experience.\n\nWe do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy.`,
  },
  {
    title: 'Data Retention',
    body: `We retain your personal information for as long as your account is active or as needed to provide you with our services. You may request deletion of your personal data at any time by contacting us. We will respond to deletion requests within 30 days.\n\nCertain information may be retained for longer periods as required by law or for legitimate business purposes such as fraud prevention.`,
  },
  {
    title: 'Security',
    body: `We implement industry-standard security measures to protect your information against unauthorized access, alteration, disclosure, or destruction. All data is encrypted in transit using TLS and at rest using AES-256 encryption.\n\nHowever, no method of transmission over the Internet or method of electronic storage is 100% secure. We cannot guarantee absolute security of your data.`,
  },
  {
    title: 'Cookies',
    body: `We use cookies and similar tracking technologies to track activity on our service and hold certain information. Cookies are files with a small amount of data which may include an anonymous unique identifier.\n\nYou can instruct your browser to refuse all cookies or to indicate when a cookie is being sent. However, if you do not accept cookies, some portions of our service may not function properly.`,
  },
  {
    title: 'Third-Party Services',
    body: `Our service may contain links to third-party websites or integrate with third-party services. We are not responsible for the privacy practices of those third parties. We encourage you to read the privacy policies of any third-party services you use in connection with Vantro.\n\nWe use select third-party providers for payment processing, analytics, and infrastructure. These providers are contractually obligated to keep your information confidential.`,
  },
  {
    title: 'Your Rights',
    body: `Depending on your location, you may have certain rights regarding your personal information, including the right to access, correct, or delete your data; the right to object to or restrict processing; and the right to data portability.\n\nTo exercise any of these rights, please contact us at privacy@vantro.ai. We will respond to all requests within 30 days.`,
  },
  {
    title: 'Changes to This Policy',
    body: `We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last updated" date. For material changes, we will provide additional notice via email.\n\nYour continued use of Vantro after any changes constitutes acceptance of the updated policy.`,
  },
];

export function PrivacyPage() {
  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: 'oklch(0.12 0 0)',
        fontFamily: "'Inter', sans-serif",
        color: 'oklch(0.97 0 0)',
      }}
    >
      {/* Top bar */}
      <div
        style={{
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          padding: '20px 48px',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <a
          href="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            color: 'oklch(0.70 0 0)',
            textDecoration: 'none',
            fontSize: 14,
            transition: 'color 0.15s',
          }}
          onMouseEnter={e => { (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.97 0 0)' }}
          onMouseLeave={e => { (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.70 0 0)' }}
        >
          <ArrowLeft size={16} />
          <span style={{ marginLeft: 4 }}>Back to Vantro.ai</span>
        </a>
      </div>

      {/* Content */}
      <div style={{ maxWidth: 720, margin: '0 auto', padding: '72px 48px 120px' }}>
        <p
          style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 11,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            color: 'oklch(0.60 0 0)',
            marginBottom: 16,
          }}
        >
          Legal
        </p>
        <h1
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 'clamp(2rem, 4vw, 3rem)',
            fontWeight: 700,
            letterSpacing: '-0.02em',
            marginBottom: 12,
            lineHeight: 1.1,
          }}
        >
          Privacy Policy
        </h1>
        <p style={{ color: 'oklch(0.60 0 0)', fontSize: 14, marginBottom: 64 }}>
          Last updated: June 25, 2026
        </p>

        <p style={{ color: 'oklch(0.75 0 0)', fontSize: 16, lineHeight: 1.75, marginBottom: 56 }}>
          Vantro ("we", "our", or "us") is committed to protecting your personal information. This
          Privacy Policy explains how we collect, use, and share information about you when you use
          our platform and services.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 48 }}>
          {SECTIONS.map((section) => (
            <div key={section.title}>
              <h2
                style={{
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontSize: 18,
                  fontWeight: 600,
                  marginBottom: 16,
                  color: 'oklch(0.97 0 0)',
                }}
              >
                {section.title}
              </h2>
              {section.body.split('\n\n').map((para, i) => (
                <p
                  key={i}
                  style={{
                    color: 'oklch(0.72 0 0)',
                    fontSize: 15,
                    lineHeight: 1.75,
                    marginBottom: 12,
                  }}
                >
                  {para}
                </p>
              ))}
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: 64,
            padding: 24,
            borderRadius: 12,
            border: '1px solid rgba(255,255,255,0.08)',
            background: 'rgba(255,255,255,0.03)',
          }}
        >
          <p style={{ color: 'oklch(0.72 0 0)', fontSize: 14, lineHeight: 1.7, margin: 0 }}>
            Questions about this policy? Contact us at{' '}
            <a
              href="mailto:privacy@vantro.ai"
              style={{ color: 'oklch(0.97 0 0)', textDecoration: 'underline' }}
            >
              privacy@vantro.ai
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
