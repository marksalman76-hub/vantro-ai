'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import { ArrowUpRight, Github, Twitter, Linkedin } from 'lucide-react'
import Hls from 'hls.js'

const HLS_SRC = 'https://stream.mux.com/8wrHPCX2dC3msyYU9ObwqNdm00u3ViXvOSHUMRYSEe5Q.m3u8'

const FOOTER_LINKS = [
  {
    heading: 'Product',
    links: [
      { label: 'How It Works',  href: '#how-it-works' },
      { label: 'Agent Roster',  href: '#agents'       },
      { label: 'Integrations',  href: '#integrations' },
      { label: 'Pricing',       href: '/pricing'      },
      { label: 'Changelog',     href: '#'             },
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
      { label: 'About',     href: '#' },
      { label: 'Blog',      href: '#' },
      { label: 'Careers',   href: '#' },
      { label: 'Contact',   href: '#' },
      { label: 'Press Kit', href: '#' },
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
  { Icon: Github,   href: '#', label: 'GitHub'   },
  { Icon: Twitter,  href: '#', label: 'Twitter'  },
  { Icon: Linkedin, href: '#', label: 'LinkedIn' },
]

export default function CTAFooter() {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    if (Hls.isSupported()) {
      const hls = new Hls()
      hls.loadSource(HLS_SRC)
      hls.attachMedia(video)
      return () => hls.destroy()
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = HLS_SRC
    }
  }, [])

  return (
    <>
      {/* ── Cinematic CTA ─────────────────────────────────────────────── */}
      <section className="relative py-32 px-6 md:px-16 lg:px-24 text-center overflow-hidden bg-black">
        {/* HLS video background */}
        <video
          ref={videoRef}
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover z-0"
        />

        {/* Top fade */}
        <div
          className="absolute top-0 left-0 right-0 z-[1] pointer-events-none"
          style={{ height: '200px', background: 'linear-gradient(to bottom, black, transparent)' }}
        />
        {/* Bottom fade */}
        <div
          className="absolute bottom-0 left-0 right-0 z-[1] pointer-events-none"
          style={{ height: '200px', background: 'linear-gradient(to top, black, transparent)' }}
        />

        {/* Content */}
        <div className="relative z-10">
          <h2 className="font-heading italic text-white tracking-tight leading-[0.85] max-w-3xl mx-auto mb-4"
            style={{ fontSize: 'clamp(3rem, 7vw, 5rem)' }}>
            Your AI workforce starts today.
          </h2>
          <p className="text-white/60 font-body font-light text-sm md:text-base max-w-xl mx-auto mb-8">
            Join 500+ teams running autonomous agents with Vantro. Connect your tools, configure in plain English, and go live the same day.
          </p>

          <div className="flex items-center justify-center gap-6 flex-wrap">
            <Link href="/signup">
              <button className="liquid-glass-strong rounded-full px-6 py-3 text-sm font-medium text-white flex items-center gap-2 hover:bg-white/10 transition-all font-body">
                Start Free 14-Day Trial
                <ArrowUpRight className="h-5 w-5" />
              </button>
            </Link>
            <Link href="/pricing">
              <button className="bg-white text-black rounded-full px-6 py-3 text-sm font-medium flex items-center gap-2 hover:bg-white/90 transition-colors font-body">
                View Pricing
                <ArrowUpRight className="h-4 w-4" />
              </button>
            </Link>
          </div>

          <p className="mt-6 text-xs text-white/30 font-body">
            No credit card required · Cancel anytime · SOC 2 Type II certified
          </p>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────────────── */}
      <footer className="relative bg-black border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-8 lg:gap-12">

            {/* Brand col */}
            <div className="col-span-2">
              <Link href="/" className="inline-flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ background: 'linear-gradient(135deg, #7C3AED, #3B82F6)', boxShadow: '0 0 20px rgba(124,58,237,0.35)' }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="white" aria-hidden="true">
                    <path d="M12 2L14.09 8.26L20.28 9.27L16.14 13.3L17.18 19.5L12 16.77L6.82 19.5L7.86 13.3L3.72 9.27L9.91 8.26L12 2Z" />
                  </svg>
                </div>
                <span className="text-lg font-bold text-white tracking-tight">
                  Vantro<span className="text-violet-400">.ai</span>
                </span>
              </Link>
              <p className="text-sm text-white/40 leading-relaxed mb-6 max-w-xs font-body">
                Autonomous AI agents that handle the repetitive work so your team can focus on what matters.
              </p>
              <div className="flex items-center gap-2">
                {SOCIAL.map(({ Icon, href, label }) => (
                  <a key={label} href={href} aria-label={label}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-white/35 hover:text-white transition-colors"
                    style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}>
                    <Icon className="w-3.5 h-3.5" />
                  </a>
                ))}
              </div>
            </div>

            {/* Link columns */}
            {FOOTER_LINKS.map((col) => (
              <div key={col.heading}>
                <p className="text-xs font-bold text-white/30 uppercase tracking-[0.15em] mb-4 font-body">{col.heading}</p>
                <ul className="space-y-2.5">
                  {col.links.map(({ label, href }) => (
                    <li key={label}>
                      <Link href={href} className="text-sm text-white/45 hover:text-white transition-colors duration-200 font-body">
                        {label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Bottom bar */}
          <div className="mt-14 pt-8 flex flex-col md:flex-row items-center justify-between gap-4 border-t border-white/10">
            <p className="text-white/40 font-body font-light text-xs">
              &copy; 2026 Vantro Inc. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              {['Privacy', 'Terms', 'Contact'].map((link) => (
                <Link
                  key={link}
                  href={link === 'Privacy' ? '/privacy' : link === 'Terms' ? '/terms' : '#'}
                  className="text-white/40 hover:text-white/70 font-body font-light text-xs transition-colors"
                >
                  {link}
                </Link>
              ))}
              <Link href="/status" className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:opacity-80 transition-opacity"
                style={{ background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.15)' }}>
                <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                <span className="text-[11px] text-green-400 font-medium font-body">System status</span>
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </>
  )
}
