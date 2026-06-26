'use client'

import { useState, FormEvent } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// ─── Data ─────────────────────────────────────────────────────────────────────

const NAV_COLUMNS = [
  {
    heading: 'Product',
    links: [
      { label: 'Features', href: '#features' },
      { label: '22 Agents', href: '#agents' },
      { label: 'Integrations', href: '#integrations' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'Enterprise', href: '#pricing' },
      { label: 'Roadmap', href: '#' },
    ],
  },
  {
    heading: 'Company',
    links: [
      { label: 'About', href: '#' },
      { label: 'Blog', href: '#' },
      { label: 'Careers', href: '#' },
      { label: 'Press', href: '#' },
      { label: 'Security', href: '#' },
      { label: 'Contact', href: 'mailto:hello@vantro.ai' },
    ],
  },
  {
    heading: 'Resources',
    links: [
      { label: 'Documentation', href: '#' },
      { label: 'API Reference', href: '#' },
      { label: 'Community', href: '#' },
      { label: 'Status', href: '#' },
      { label: 'Changelog', href: '#' },
    ],
  },
  {
    heading: 'Connect',
    links: [
      { label: 'Twitter / X', href: 'https://x.com' },
      { label: 'LinkedIn', href: 'https://linkedin.com' },
      { label: 'GitHub', href: 'https://github.com' },
      { label: 'Email', href: 'mailto:hello@vantro.ai' },
    ],
  },
] as const

// ─── Social Icons ─────────────────────────────────────────────────────────────

function TwitterIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  )
}

function LinkedInIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  )
}

function GitHubIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
    </svg>
  )
}

const SOCIAL_LINKS = [
  { label: 'Twitter / X', href: 'https://x.com', Icon: TwitterIcon },
  { label: 'LinkedIn', href: 'https://linkedin.com', Icon: LinkedInIcon },
  { label: 'GitHub', href: 'https://github.com', Icon: GitHubIcon },
] as const

// ─── Logo ─────────────────────────────────────────────────────────────────────

function Logo() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 2, userSelect: 'none' }}>
      <span style={{ color: '#FF6B35', fontWeight: 700, fontSize: 28 }}>V</span>
      <span style={{ color: '#ffffff', fontWeight: 700, fontSize: 28 }}>antro</span>
    </div>
  )
}

// ─── Social Button ────────────────────────────────────────────────────────────

function SocialButton({
  href,
  label,
  Icon,
}: {
  href: string
  label: string
  Icon: () => JSX.Element
}) {
  const [hovered, setHovered] = useState(false)

  return (
    <a
      href={href}
      aria-label={label}
      target="_blank"
      rel="noopener noreferrer"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: 36,
        height: 36,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: hovered ? 'rgba(0,217,255,0.10)' : 'rgba(255,255,255,0.06)',
        border: `1px solid ${hovered ? 'rgba(0,217,255,0.30)' : 'rgba(255,255,255,0.10)'}`,
        color: hovered ? '#00D9FF' : '#9ca3af',
        transition: 'background 0.2s ease, border-color 0.2s ease, color 0.2s ease',
        textDecoration: 'none',
        flexShrink: 0,
      }}
    >
      <Icon />
    </a>
  )
}

// ─── Newsletter ───────────────────────────────────────────────────────────────

function Newsletter() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [inputFocused, setInputFocused] = useState(false)

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!email.trim()) return
    setSubmitted(true)
    setEmail('')
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <p style={{ color: '#ffffff', fontSize: 14, fontWeight: 600 }}>Stay in the loop</p>
      <AnimatePresence mode="wait">
        {submitted ? (
          <motion.p
            key="thanks"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{ color: '#22c55e', fontSize: 14, fontWeight: 500 }}
          >
            Thanks! You&apos;re subscribed.
          </motion.p>
        ) : (
          <motion.form
            key="form"
            onSubmit={handleSubmit}
            style={{ display: 'flex', alignItems: 'center', gap: 8 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setInputFocused(true)}
              onBlur={() => setInputFocused(false)}
              placeholder="you@company.com"
              required
              style={{
                flex: 1,
                background: 'rgba(255,255,255,0.06)',
                border: `1px solid ${inputFocused ? '#00D9FF' : 'rgba(255,255,255,0.10)'}`,
                borderRadius: 10,
                color: '#ffffff',
                padding: '11px 16px',
                fontSize: 14,
                outline: 'none',
                boxShadow: inputFocused ? '0 0 0 1px #00D9FF44' : 'none',
                transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
              }}
            />
            <button
              type="submit"
              style={{
                flexShrink: 0,
                padding: '11px 18px',
                borderRadius: 10,
                background: '#FF6B35',
                color: '#ffffff',
                fontWeight: 700,
                fontSize: 13,
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 0 16px rgba(255,107,53,0.35)',
                transition: 'box-shadow 0.2s ease, transform 0.15s ease',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                ;(e.currentTarget as HTMLButtonElement).style.boxShadow =
                  '0 0 28px rgba(255,107,53,0.65)'
                ;(e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-1px)'
              }}
              onMouseLeave={(e) => {
                ;(e.currentTarget as HTMLButtonElement).style.boxShadow =
                  '0 0 16px rgba(255,107,53,0.35)'
                ;(e.currentTarget as HTMLButtonElement).style.transform = 'none'
              }}
            >
              Subscribe
            </button>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  )
}

// ─── Nav Link ─────────────────────────────────────────────────────────────────

function NavLink({ href, label }: { href: string; label: string }) {
  const [hovered, setHovered] = useState(false)
  return (
    <li>
      <a
        href={href}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          fontSize: 14,
          color: hovered ? '#d1d5db' : '#6b7280',
          transition: 'color 0.15s ease',
          textDecoration: 'none',
        }}
      >
        {label}
      </a>
    </li>
  )
}

// ─── Bottom Link ──────────────────────────────────────────────────────────────

function BottomLink({ href, label }: { href: string; label: string }) {
  const [hovered, setHovered] = useState(false)
  return (
    <a
      href={href}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        fontSize: 14,
        color: hovered ? '#d1d5db' : '#6b7280',
        transition: 'color 0.15s ease',
        textDecoration: 'none',
      }}
    >
      {label}
    </a>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function SiteFooter() {
  return (
    <footer
      style={{
        background: '#0A0D11',
        borderTop: '1px solid rgba(0,217,255,0.12)',
        paddingTop: 80,
        paddingBottom: 80,
        paddingLeft: 24,
        paddingRight: 24,
        width: '100%',
      }}
    >
      <div style={{ maxWidth: 1280, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 56 }}>

        {/* Top section: logo/tagline/socials + newsletter */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            gap: 40,
            flexWrap: 'wrap',
          }}
        >
          {/* Logo + tagline + socials */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Logo />
            <p style={{ color: '#9ca3af', fontSize: 14 }}>Your autonomous AI workforce.</p>
            {/* Social links */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4 }}>
              {SOCIAL_LINKS.map(({ href, label, Icon }) => (
                <SocialButton key={label} href={href} label={label} Icon={Icon} />
              ))}
            </div>
          </div>

          {/* Newsletter */}
          <div style={{ width: 288 }}>
            <Newsletter />
          </div>
        </div>

        {/* Nav columns grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: 32,
          }}
        >
          {NAV_COLUMNS.map((col) => (
            <div key={col.heading} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <p
                style={{
                  color: '#ffffff',
                  fontSize: 13,
                  fontWeight: 700,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                }}
              >
                {col.heading}
              </p>
              <ul
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 10,
                  listStyle: 'none',
                  padding: 0,
                  margin: 0,
                }}
              >
                {col.links.map((link) => (
                  <NavLink key={link.label} href={link.href} label={link.label} />
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div style={{ height: 1, background: 'rgba(255,255,255,0.07)' }} />

        {/* Bottom row */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 16,
            flexWrap: 'wrap',
          }}
        >
          <p style={{ color: '#4b5563', fontSize: 14 }}>
            © 2026 Vantro AI · All rights reserved
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <BottomLink href="/privacy" label="Privacy Policy" />
            <BottomLink href="/terms" label="Terms of Service" />
          </div>
        </div>

      </div>

      {/* Responsive grid */}
      <style>{`
        @media (max-width: 768px) {
          footer .nav-grid {
            grid-template-columns: repeat(2, 1fr) !important;
          }
          footer .top-row {
            flex-direction: column !important;
          }
        }
      `}</style>
    </footer>
  )
}
