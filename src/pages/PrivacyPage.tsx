'use client';

import { ArrowLeft } from 'lucide-react';

const SECTIONS = [
  {
    title: '1. Who We Are and Scope',
    body: `Vantro ("Vantro", "we", "our", or "us") operates an AI agent platform that enables businesses to deploy autonomous AI-powered agents for ecommerce operations, sales, marketing, support, and related business functions. This Privacy Policy applies to all users of vantro.ai, app.vantro.ai, api.vantro.ai, and any associated services (collectively, the "Platform").\n\nFor the purposes of applicable data protection law — including the EU General Data Protection Regulation ("GDPR") and the California Consumer Privacy Act ("CCPA") — Vantro acts as a data controller in respect of account and billing information, and as a data processor in respect of business data you submit to the Platform for processing by our AI agents.`,
  },
  {
    title: '2. Information We Collect',
    body: `Account and Identity Data: When you register, we collect your name, work email address, company name, role, and a hashed password. We do not store plain-text passwords.\n\nBilling and Payment Data: Payment card details are collected and stored exclusively by our payment processor, Stripe, Inc. We store only non-sensitive billing metadata (last four digits, card type, billing address, invoice history). We never have access to your full card number or CVV.\n\nWorkspace and Usage Data: We record which AI agents you run, task inputs and outputs, credit consumption, job status transitions, and Human-in-the-Loop (HITL) approval decisions. This data is isolated by workspace and organisation and is never shared across tenants.\n\nTechnical and Log Data: We automatically collect IP address, browser type and version, operating system, referring URLs, pages visited, request timestamps, HTTP status codes, and error traces. These are used for security monitoring, abuse prevention, and service reliability.\n\nCommunications: If you contact us via email or in-app support, we retain those communications to resolve your query and improve support quality.\n\nThird-Party Integration Credentials: If you connect external services (e.g. Shopify, Google Analytics, Meta Ads), the OAuth tokens or API keys you provide are encrypted at rest using AES-128-CBC with HMAC-SHA256 and are never returned in any API response, log, or error message. Decrypted values are used only to execute the specific agent task you initiate.`,
  },
  {
    title: '3. How We Use Your Information',
    body: `Service Delivery: To authenticate you, route AI agent jobs, process credits, execute integrations, and deliver results to your workspace dashboard.\n\nBilling and Transactions: To generate invoices, process subscription payments via Stripe, apply credit allocations, and enforce plan entitlements.\n\nSecurity and Fraud Prevention: To detect unauthorised access, rate-limit requests, screen for prompt-injection attacks, and block suspicious activity patterns.\n\nService Improvement: Aggregated, de-identified usage patterns inform product decisions. We do not use your individual task inputs or outputs to train shared AI models without your explicit opt-in consent.\n\nLegal Compliance: To meet our obligations under applicable law, respond to lawful requests from public authorities, and enforce our Terms of Service.\n\nWe do not sell, rent, or trade your personal information to third parties. We do not use your data for advertising targeting on third-party platforms.`,
  },
  {
    title: '4. Legal Bases for Processing (GDPR)',
    body: `If you are located in the European Economic Area (EEA) or United Kingdom, our legal bases for processing personal data are:\n\nContract Performance: Processing necessary to provide the Platform services you have subscribed to, including account management, job execution, and billing.\n\nLegitimate Interests: Security monitoring, fraud prevention, aggregate analytics, and service reliability — where these interests are not overridden by your rights.\n\nLegal Obligation: Retaining transaction records and audit logs as required by applicable financial, tax, and regulatory law.\n\nConsent: Where we send optional marketing communications or use non-essential cookies, we rely on your explicit consent, which you may withdraw at any time.`,
  },
  {
    title: '5. Data Sharing and Sub-Processors',
    body: `We engage the following categories of sub-processors to operate the Platform. Each is bound by a data processing agreement:\n\n• Cloud Infrastructure: Amazon Web Services (AWS) — compute, managed database, object storage, and monitoring. Data is stored in the us-east-1 region by default.\n• Database: Supabase (PostgreSQL) — managed relational database for structured application data.\n• Payment Processing: Stripe, Inc. — subscription billing, invoice generation, and webhook event delivery.\n• Frontend Hosting: Vercel, Inc. — serving the client-facing application.\n• AI Model Providers: We use third-party large language model APIs to power our agents. Provider identity is not disclosed to end users in accordance with our technology confidentiality policy. Task inputs submitted to agents are processed by these providers and are subject to their data handling terms.\n\nWe do not share your data with any other third parties except (a) with your explicit consent, (b) as required by law, or (c) in connection with a merger, acquisition, or sale of substantially all assets, with advance notice to you.`,
  },
  {
    title: '6. International Data Transfers',
    body: `Vantro is headquartered in the United States. If you access the Platform from outside the United States, your data will be transferred to and processed in the United States.\n\nFor transfers of personal data from the EEA, UK, or Switzerland, we rely on EU Standard Contractual Clauses (SCCs) and/or the UK International Data Transfer Agreement (IDTA) as the appropriate transfer mechanism with our sub-processors.\n\nBy using the Platform, you acknowledge that your information may be transferred to our facilities and to those third parties described in this policy.`,
  },
  {
    title: '7. Data Retention',
    body: `Account Data: Retained for the duration of your active subscription plus 90 days after account closure, to allow reactivation and to resolve outstanding billing queries.\n\nJob and Task Data: Retained for 12 months from the date of execution, after which it is purged from production databases. You may request earlier deletion (see Section 9).\n\nAudit Logs: Security and access logs are retained for 24 months to support incident investigation and regulatory compliance.\n\nBilling Records: Transaction records are retained for 7 years as required by applicable tax and financial regulations.\n\nEncrypted Integration Credentials: Deleted immediately upon disconnection of the integration or closure of the associated workspace.\n\nData marked for deletion is removed from active systems within 30 days of the deletion trigger and from all backups within 90 days.`,
  },
  {
    title: '8. Security',
    body: `We implement the following technical and organisational measures to protect your information:\n\n• Encryption in transit: TLS 1.2 or higher on all endpoints.\n• Encryption at rest: AES-256 for database storage; AES-128-CBC + HMAC-SHA256 for integration credentials.\n• Access controls: Role-based access control (RBAC); admin functions require separate authentication; all database queries are scoped to a workspace identifier preventing cross-tenant data access.\n• Infrastructure hardening: Security headers on all responses; WAF rules blocking path traversal, SQL injection, and known exploit signatures; rate limiting on all authentication and agent execution endpoints.\n• Monitoring: Continuous alerting on anomalous patterns; Human-in-the-Loop review required for any agent action flagged as involving financial, legal, or scaling decisions.\n\nDespite these measures, no system is perfectly secure. We will notify affected users without undue delay in the event of a data breach that poses a high risk to your rights, as required by applicable law.`,
  },
  {
    title: '9. Your Privacy Rights',
    body: `Depending on your location, you have the following rights regarding your personal data:\n\nRight of Access: Request a copy of the personal data we hold about you.\n\nRight to Rectification: Request correction of inaccurate or incomplete data.\n\nRight to Erasure: Request deletion of your personal data, subject to our legal retention obligations.\n\nRight to Restriction: Request that we restrict processing of your data in certain circumstances.\n\nRight to Data Portability: Receive your personal data in a structured, machine-readable format.\n\nRight to Object: Object to processing based on legitimate interests, including profiling.\n\nRight to Withdraw Consent: Where processing is based on consent, withdraw it at any time without affecting the lawfulness of prior processing.\n\nCCPA Rights (California residents): The right to know what personal information is collected and how it is used; the right to delete personal information; the right to opt out of sale (we do not sell personal information); and the right to non-discrimination for exercising these rights.\n\nTo exercise any of these rights, email privacy@vantro.ai with the subject line "Privacy Request". We will acknowledge receipt within 72 hours and respond substantively within 30 days (extendable to 60 days for complex requests, with notice). We may require identity verification before fulfilling a request.`,
  },
  {
    title: '10. Cookies and Tracking',
    body: `We use the following categories of cookies and local storage:\n\nStrictly Necessary: Session tokens, CSRF protection tokens, and authentication state. These are required for the Platform to function and cannot be disabled.\n\nFunctional: User preferences (e.g. dashboard layout, notification settings) that persist across sessions.\n\nAnalytics: Aggregate usage metrics to understand how features are used, processed in a de-identified manner. We do not use third-party advertising cookies.\n\nYou can control cookie preferences via your browser settings. Disabling strictly necessary cookies will prevent login. Our marketing site (vantro.ai) uses minimal analytics cookies only; the platform app (app.vantro.ai) uses only strictly necessary and functional cookies.`,
  },
  {
    title: '11. Children\'s Privacy',
    body: `The Platform is intended solely for business use by individuals who are at least 18 years old. We do not knowingly collect personal information from anyone under 18. If we become aware that we have collected personal information from a minor, we will delete it promptly. If you believe we may have collected information from a minor, please contact privacy@vantro.ai.`,
  },
  {
    title: '12. Changes to This Policy',
    body: `We may update this Privacy Policy periodically. For changes that materially affect your rights or how we use your data, we will provide at least 30 days' advance notice via email to your registered address and via in-app notification.\n\nYour continued use of the Platform after the effective date of a revised policy constitutes acceptance of the updated terms. If you do not agree to a material change, you may close your account before the change takes effect.`,
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
