'use client';

import { ArrowLeft } from 'lucide-react';

const SECTIONS = [
  {
    title: 'What Are Cookies',
    body: `Cookies are small text files placed on your device when you visit a website. They allow the site to remember your preferences, keep you logged in, and understand how you interact with the service.\n\nVantro uses cookies and similar technologies (such as local storage and session storage) to operate the platform, ensure security, and improve your experience.`,
  },
  {
    title: 'Types of Cookies We Use',
    body: `Strictly Necessary Cookies: Required for the platform to function. These include session authentication tokens, CSRF protection tokens, and cookies that remember your cookie consent choice. You cannot opt out of these.\n\nFunctional Cookies: Remember your preferences such as theme settings, dashboard layout, and workspace selections. Disabling these may affect platform usability.\n\nAnalytics Cookies: Help us understand how users interact with Vantro so we can improve the product. These are aggregated and do not identify you personally. We use privacy-preserving analytics that do not share data with advertising networks.\n\nWe do not use advertising or tracking cookies. We do not share cookie data with third-party ad platforms.`,
  },
  {
    title: 'Cookie Duration',
    body: `Session Cookies: Deleted when you close your browser. Used for authentication and security.\n\nPersistent Cookies: Remain on your device for a set period. Our persistent cookies expire between 7 days (remember-me tokens) and 12 months (preference and analytics cookies).\n\nYou can view and delete cookies at any time via your browser settings.`,
  },
  {
    title: 'Managing Cookies',
    body: `You can control cookies through your browser settings. Most browsers allow you to view, block, or delete cookies. Note that blocking strictly necessary cookies will prevent you from logging in to Vantro.\n\nFor instructions on managing cookies in your browser, visit your browser's help documentation. Common browsers: Chrome, Firefox, Safari, Edge.\n\nTo opt out of analytics tracking, you can disable analytics cookies via the cookie preferences panel accessible from the footer of this page.`,
  },
  {
    title: 'Third-Party Cookies',
    body: `Vantro embeds content from a limited number of third-party services, which may set their own cookies. These include:\n\n• Stripe (payment processing) — sets cookies required for secure payment flows. See Stripe's cookie policy at stripe.com/legal/cookies-policy.\n\nWe do not embed social media widgets, advertising networks, or other third-party trackers on the platform.`,
  },
  {
    title: 'Updates to This Policy',
    body: `We may update this Cookie Policy as the platform evolves or as regulatory requirements change. We will notify you of material changes via email or an in-app notice.\n\nThis policy was last reviewed on June 25, 2026.`,
  },
];

export function CookiesPage() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'oklch(0.12 0 0)', fontFamily: 'Inter, sans-serif', color: 'oklch(0.97 0 0)' }}>
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
        <p style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, letterSpacing: '0.15em', textTransform: 'uppercase', color: 'oklch(0.60 0 0)', marginBottom: 16 }}>
          Legal
        </p>
        <h1 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 'clamp(2rem, 4vw, 3rem)', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 12, lineHeight: 1.1 }}>
          Cookie Policy
        </h1>
        <p style={{ color: 'oklch(0.60 0 0)', fontSize: 14, marginBottom: 64 }}>
          Last updated: June 25, 2026
        </p>

        <p style={{ color: 'oklch(0.75 0 0)', fontSize: 16, lineHeight: 1.75, marginBottom: 56 }}>
          This Cookie Policy explains how Vantro uses cookies and similar technologies when you visit vantro.ai or use the Vantro platform. It should be read alongside our Privacy Policy.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 48 }}>
          {SECTIONS.map(section => (
            <div key={section.title}>
              <h2 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 18, fontWeight: 600, marginBottom: 16, color: 'oklch(0.97 0 0)' }}>
                {section.title}
              </h2>
              {section.body.split('\n\n').map((para, i) => (
                <p key={i} style={{ color: 'oklch(0.72 0 0)', fontSize: 15, lineHeight: 1.75, marginBottom: 12 }}>
                  {para}
                </p>
              ))}
            </div>
          ))}
        </div>

        <div style={{ marginTop: 64, padding: 24, borderRadius: 12, border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.03)' }}>
          <p style={{ color: 'oklch(0.72 0 0)', fontSize: 14, lineHeight: 1.7, margin: 0 }}>
            Questions about cookies or data practices? Contact us at{' '}
            <a href="mailto:privacy@vantro.ai" style={{ color: 'oklch(0.97 0 0)', textDecoration: 'underline' }}>
              privacy@vantro.ai
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
