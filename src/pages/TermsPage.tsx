'use client';

import { ArrowLeft } from 'lucide-react';

const SECTIONS = [
  {
    title: 'Acceptance of Terms',
    body: `By accessing or using Vantro ("the Service"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, you may not access or use the Service.\n\nThese Terms apply to all visitors, users, and others who access or use the Service. We reserve the right to update these Terms at any time, and will notify you of material changes via email or in-app notification.`,
  },
  {
    title: 'Description of Service',
    body: `Vantro provides an AI agent platform that allows businesses to deploy autonomous AI agents for operations, sales, support, and other business functions. The Service includes access to our agent dashboard, API, integrations, and related features.\n\nWe reserve the right to modify, suspend, or discontinue any part of the Service at any time with reasonable notice to users.`,
  },
  {
    title: 'Account Registration',
    body: `To access certain features of the Service, you must register for an account. You agree to provide accurate, current, and complete information during registration and to update such information as necessary.\n\nYou are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You must notify us immediately of any unauthorized use of your account.`,
  },
  {
    title: 'Acceptable Use',
    body: `You agree not to use the Service to: violate any applicable law or regulation; infringe the intellectual property rights of others; transmit harmful, offensive, or fraudulent content; attempt to gain unauthorized access to our systems; or use the Service to train competing AI models.\n\nVantro reserves the right to suspend or terminate accounts that violate these guidelines without prior notice.`,
  },
  {
    title: 'Payment and Billing',
    body: `Paid plans are billed in advance on a monthly or annual basis. All fees are non-refundable except as required by applicable law or as expressly stated in these Terms.\n\nWe reserve the right to change our pricing with 30 days notice. Continued use of the Service after a price change constitutes acceptance of the new pricing. If you dispute a charge, you must notify us within 30 days of the charge.`,
  },
  {
    title: 'Intellectual Property',
    body: `The Service and its original content, features, and functionality are owned by Vantro and are protected by international copyright, trademark, patent, trade secret, and other intellectual property laws.\n\nYou retain ownership of any data you submit to the Service. By submitting data, you grant Vantro a limited license to use that data solely for the purpose of providing and improving the Service.`,
  },
  {
    title: 'Limitation of Liability',
    body: `To the maximum extent permitted by applicable law, Vantro shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including loss of profits, data, or goodwill, arising from your use of the Service.\n\nOur total liability to you for any claims under these Terms shall not exceed the amount you paid us in the twelve months preceding the claim.`,
  },
  {
    title: 'Termination',
    body: `We may terminate or suspend your account at any time for violation of these Terms, with or without prior notice. Upon termination, your right to use the Service will immediately cease.\n\nYou may terminate your account at any time by contacting us at support@vantro.ai. Upon termination, we will delete your data in accordance with our Privacy Policy, subject to any legal retention requirements.`,
  },
  {
    title: 'Governing Law',
    body: `These Terms shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of law provisions.\n\nAny disputes arising under these Terms shall be resolved through binding arbitration in accordance with the rules of the American Arbitration Association, except that either party may seek injunctive relief in a court of competent jurisdiction.`,
  },
];

export function TermsPage() {
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
          Terms of Service
        </h1>
        <p style={{ color: 'oklch(0.60 0 0)', fontSize: 14, marginBottom: 64 }}>
          Last updated: June 25, 2026
        </p>

        <p style={{ color: 'oklch(0.75 0 0)', fontSize: 16, lineHeight: 1.75, marginBottom: 56 }}>
          Please read these Terms of Service carefully before using Vantro. These Terms govern your
          access to and use of our platform, including any associated services, APIs, and content.
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
            Questions about these Terms? Contact us at{' '}
            <a
              href="mailto:legal@vantro.ai"
              style={{ color: 'oklch(0.97 0 0)', textDecoration: 'underline' }}
            >
              legal@vantro.ai
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
