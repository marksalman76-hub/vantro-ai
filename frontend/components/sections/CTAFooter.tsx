'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Github, Twitter, Linkedin, Zap } from 'lucide-react'

const FOOTER_LINKS = [
  {
    heading: 'Product',
    links: [
      { label: 'How It Works',  href: '#how-it-works'  },
      { label: 'Agent Roster',  href: '#agents'        },
      { label: 'Integrations',  href: '#integrations'  },
      { label: 'Pricing',       href: '/pricing'       },
      { label: 'Changelog',     href: '#'              },
    ],
  },
  {
    heading: 'Solutions',
    links: [
      { label: 'Sales Automation',    href: '#agents' },
      { label: 'Customer Support',    href: '#agents' },
      { label: 'Market Research',     href: '#agents' },
      { label: 'Content & Marketing', href: '#agents' },
      { label: 'Operations',          href: '#agents' },
    ],
  },
  {
    heading: 'Company',
    links: [
      { label: 'About',      href: '#' },
      { label: 'Blog',       href: '#' },
      { label: 'Careers',    href: '#' },
      { label: 'Contact',    href: '#' },
      { label: 'Press Kit',  href: '#' },
    ],
  },
  {
    heading: 'Legal',
    links: [
      { label: 'Terms of Service', href: '/terms'   },
      { label: 'Privacy Policy',   href: '/privacy' },
      { label: 'Cookie Policy',    href: '#'        },
      { label: 'Security',         href: '#'        },
    ],
  },
]

const SOCIAL = [
  { icon: Github,   href: '#', label: 'GitHub'   },
  { icon: Twitter,  href: '#', label: 'Twitter'  },
  { icon: Linkedin, href: '#', label: 'LinkedIn' },
]

export default function CTAFooter() {
  return (
    <>
      {/* ─── CTA Section ──────────────────────────────────────────────── */}
      <section
        className="relative overflow-hidden py-24 lg:py-32"
        style={{ background: 'linear-gradient(180deg, #080D1E 0%, #06091A 100%)' }}
      >
        {/* Ambient blobs */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[350px] rounded-full blur-[160px] pointer-events-none"
          style={{ background: 'radial-gradient(ellipse, rgba(124,58,237,0.18) 0%, transparent 70%)' }} />
        <div className="absolute bottom-0 left-1/4 w-[400px] h-[200px] rounded-full blur-[120px] opacity-10 pointer-events-none"
          style={{ background: '#3B82F6' }} />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[200px] rounded-full blur-[120px] opacity-10 pointer-events-none"
          style={{ background: '#EC4899' }} />

        <div className="absolute inset-0 mesh-grid-fine opacity-20 pointer-events-none" />

        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 28 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ type: 'spring', stiffness: 180, damping: 22 }}
          >
            {/* Badge */}
            <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide mb-8"
              style={{ background: 'rgba(124,58,237,0.12)', border: '1px solid rgba(124,58,237,0.28)', color: '#C084FC' }}>
              <Zap className="w-3 h-3" />
              Start in minutes. No MLOps team required.
            </span>

            <h2 className="section-heading mb-6">
              Ready to deploy your{' '}
              <span className="gradient-text">AI workforce?</span>
            </h2>

            <p className="text-lg text-white/55 max-w-xl mx-auto mb-10 leading-relaxed">
              Join 500+ teams already running AI agents with Vantro.
              Connect your tools, configure in plain English, and go live today.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap gap-3 justify-center mb-10">
              <Link href="/signup">
                <motion.span
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.97 }}
                  className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-base font-bold text-white cursor-pointer"
                  style={{
                    background: 'linear-gradient(135deg, #7C3AED, #3B82F6)',
                    boxShadow: '0 8px 40px rgba(124,58,237,0.45)',
                  }}
                >
                  Start Free 14-Day Trial
                  <ArrowRight className="w-4 h-4" />
                </motion.span>
              </Link>
              <Link href="/pricing">
                <motion.span
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.97 }}
                  className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-base font-bold text-white/75 cursor-pointer"
                  style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)' }}
                >
                  View Pricing
                </motion.span>
              </Link>
            </div>

            <p className="text-sm text-white/30">
              No credit card required · Cancel anytime · SOC 2 Type II certified
            </p>
          </motion.div>

          {/* Social proof logos strip */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.25 }}
            className="mt-16 pt-10"
            style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}
          >
            <p className="text-xs text-white/20 uppercase tracking-[0.2em] font-semibold mb-6">
              Trusted by teams at
            </p>
            <div className="flex flex-wrap justify-center gap-x-10 gap-y-3">
              {[
                { name: 'Salesforce', color: '#00A1E0' },
                { name: 'HubSpot',    color: '#FF7A59' },
                { name: 'Slack',      color: '#E01E5A' },
                { name: 'Shopify',    color: '#96BF48' },
                { name: 'Stripe',     color: '#7B73F7' },
                { name: 'Notion',     color: 'rgba(255,255,255,0.4)' },
              ].map(({ name, color }) => (
                <span key={name} className="text-sm font-bold tracking-tight transition-opacity opacity-25 hover:opacity-60" style={{ color }}>
                  {name}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ─── Footer ───────────────────────────────────────────────────── */}
      <footer
        className="relative"
        style={{ background: '#06091A', borderTop: '1px solid rgba(255,255,255,0.05)' }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-8 lg:gap-12">

            {/* Brand col */}
            <div className="col-span-2">
              <Link href="/" className="inline-flex items-center gap-2 mb-4 group">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #7C3AED, #3B82F6)', boxShadow: '0 0 20px rgba(124,58,237,0.35)' }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="white" aria-hidden="true">
                    <path d="M12 2L14.09 8.26L20.28 9.27L16.14 13.3L17.18 19.5L12 16.77L6.82 19.5L7.86 13.3L3.72 9.27L9.91 8.26L12 2Z" />
                  </svg>
                </div>
                <span className="text-lg font-bold text-white tracking-tight">
                  Vantro<span className="text-violet-400">.ai</span>
                </span>
              </Link>
              <p className="text-sm text-white/40 leading-relaxed mb-6 max-w-xs">
                Autonomous AI agents that handle the repetitive work so your team can focus
                on what matters most.
              </p>
              {/* Socials */}
              <div className="flex items-center gap-2">
                {SOCIAL.map(({ icon: Icon, href, label }) => (
                  <motion.a
                    key={label}
                    href={href}
                    aria-label={label}
                    whileHover={{ scale: 1.1, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-white/35 hover:text-white transition-colors"
                    style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </motion.a>
                ))}
              </div>
            </div>

            {/* Link columns */}
            {FOOTER_LINKS.map((col) => (
              <div key={col.heading}>
                <p className="text-xs font-bold text-white/30 uppercase tracking-[0.15em] mb-4">{col.heading}</p>
                <ul className="space-y-2.5">
                  {col.links.map(({ label, href }) => (
                    <li key={label}>
                      <Link
                        href={href}
                        className="text-sm text-white/45 hover:text-white transition-colors duration-200"
                      >
                        {label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Bottom bar */}
          <div
            className="mt-14 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4"
            style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
          >
            <p className="text-xs text-white/25">
              © 2026 Vantro Inc. All rights reserved.
            </p>
            <Link href="/status" className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:opacity-80 transition-opacity"
              style={{ background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.15)' }}>
              <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              <span className="text-[11px] text-green-400 font-medium">System status</span>
            </Link>
          </div>
        </div>
      </footer>
    </>
  )
}
