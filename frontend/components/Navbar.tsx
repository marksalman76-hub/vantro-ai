'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'

const NAV_LINKS = [
  { label: 'agents',       href: '#agents',       section: 'agents'       },
  { label: 'how it works', href: '#how-it-works',  section: 'how-it-works' },
  { label: 'integrations', href: '#integrations',  section: 'integrations' },
  { label: 'pricing',      href: '/pricing',       section: null            },
]

function VantroMark() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" className="text-white">
      <path d="M12 2L14.09 8.26L20.28 9.27L16.14 13.3L17.18 19.5L12 16.77L6.82 19.5L7.86 13.3L3.72 9.27L9.91 8.26L12 2Z" />
    </svg>
  )
}

export default function Navbar() {
  const [scrolled,    setScrolled]    = useState(false)
  const [mobileOpen,  setMobileOpen]  = useState(false)
  const [activeSection, setActiveSection] = useState<string | null>(null)
  const observerRef = useRef<IntersectionObserver | null>(null)

  // Scroll detection
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Active section via IntersectionObserver
  useEffect(() => {
    const sections = NAV_LINKS.map(l => l.section).filter(Boolean) as string[]
    const els = sections.map(id => document.getElementById(id)).filter(Boolean) as HTMLElement[]
    if (!els.length) return

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter(e => e.isIntersecting)
        if (visible.length) setActiveSection(visible[0].target.id)
      },
      { rootMargin: '-30% 0px -60% 0px', threshold: 0 }
    )
    els.forEach(el => observerRef.current!.observe(el))
    return () => observerRef.current?.disconnect()
  }, [])

  const pillBg    = 'rgba(7, 13, 31, 0.82)'
  const pillBgSc  = 'rgba(7, 13, 31, 0.95)'
  const borderSc  = 'rgba(124, 58, 237, 0.22)'
  const borderDef = 'rgba(255, 255, 255, 0.07)'

  return (
    <>
      {/* Floating pill wrapper */}
      <div className="fixed top-4 inset-x-0 z-50 flex justify-center px-4 pointer-events-none">
        <motion.header
          initial={false}
          animate={{
            background:   scrolled ? pillBgSc : pillBg,
            borderColor:  scrolled ? borderSc  : borderDef,
            boxShadow:    scrolled
              ? '0 0 0 1px rgba(124,58,237,0.12), 0 8px 48px rgba(0,0,0,0.5), 0 0 80px rgba(124,58,237,0.06)'
              : '0 0 0 1px rgba(255,255,255,0.04), 0 4px 24px rgba(0,0,0,0.3)',
            paddingTop:    scrolled ? '8px'  : '10px',
            paddingBottom: scrolled ? '8px'  : '10px',
          }}
          transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
          className="pointer-events-auto w-full max-w-4xl rounded-2xl border"
          style={{
            backdropFilter:       'blur(24px) saturate(1.6)',
            WebkitBackdropFilter: 'blur(24px) saturate(1.6)',
          }}
        >
          <div className="flex items-center justify-between px-5">

            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group shrink-0">
              <motion.div
                whileHover={{ rotate: 15, scale: 1.1 }}
                transition={{ type: 'spring', stiffness: 400, damping: 15 }}
              >
                <VantroMark />
              </motion.div>
              <span className="font-semibold text-[15px] tracking-tight text-white">
                Vantro
              </span>
            </Link>

            {/* Desktop nav links */}
            <nav className="hidden md:flex items-center gap-1" aria-label="Primary navigation">
              {NAV_LINKS.map((link) => {
                const isActive = link.section && activeSection === link.section
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="relative px-3.5 py-1.5 text-[13px] lowercase tracking-wide transition-colors duration-200 group"
                    style={{ color: isActive ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.42)' }}
                    onMouseEnter={e => { if (!isActive) (e.currentTarget as HTMLElement).style.color = 'rgba(255,255,255,0.85)' }}
                    onMouseLeave={e => { if (!isActive) (e.currentTarget as HTMLElement).style.color = 'rgba(255,255,255,0.42)' }}
                  >
                    {link.label}
                    {/* Active dot */}
                    {isActive && (
                      <motion.span
                        layoutId="nav-active-dot"
                        className="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-violet-400"
                        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      />
                    )}
                    {/* Hover bg */}
                    <span className="absolute inset-0 rounded-lg bg-white/0 group-hover:bg-white/[0.05] transition-colors duration-200 -z-10" />
                  </Link>
                )
              })}
            </nav>

            {/* Right CTAs */}
            <div className="hidden md:flex items-center gap-2 shrink-0">
              <Link
                href="/login"
                className="px-3.5 py-1.5 text-[13px] text-white/40 hover:text-white/80 transition-colors duration-200 rounded-lg hover:bg-white/[0.05]"
              >
                log in
              </Link>

              {/* CTA pill with shimmer */}
              <Link
                href="/signup"
                className="relative overflow-hidden inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-[12px] font-semibold bg-white text-[#080d1e] hover:bg-white/92 transition-colors duration-200 group"
              >
                {/* Shimmer sweep */}
                <motion.span
                  className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                  initial={{ x: '-120%' }}
                  animate={{ x: '220%' }}
                  transition={{ duration: 2.4, ease: 'easeInOut', repeat: Infinity, repeatDelay: 3.5 }}
                />
                get started
                <span className="relative" aria-hidden="true">→</span>
              </Link>
            </div>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(v => !v)}
              aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileOpen}
              className="md:hidden flex flex-col justify-center gap-[5px] p-2 -mr-1"
            >
              {([
                mobileOpen ? { rotate: 45,  y: 7 }      : { rotate: 0, y: 0 },
                mobileOpen ? { opacity: 0,  scaleX: 0 } : { opacity: 1, scaleX: 1 },
                mobileOpen ? { rotate: -45, y: -7 }     : { rotate: 0, y: 0 },
              ] as const).map((anim, i) => (
                <motion.span
                  key={i}
                  animate={anim}
                  transition={{ duration: 0.2 }}
                  className="block w-5 h-px origin-center bg-white"
                />
              ))}
            </button>
          </div>

          {/* Mobile drawer — lives inside pill */}
          <AnimatePresence>
            {mobileOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
                className="overflow-hidden md:hidden"
              >
                <div className="border-t border-white/[0.07] mt-2 mx-2 pt-4 pb-5 px-3 flex flex-col gap-1">
                  {NAV_LINKS.map((link, i) => (
                    <motion.div
                      key={link.href}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                    >
                      <Link
                        href={link.href}
                        onClick={() => setMobileOpen(false)}
                        className="block px-3 py-2 text-[15px] lowercase text-white/55 hover:text-white rounded-xl hover:bg-white/[0.05] transition-all"
                      >
                        {link.label}
                      </Link>
                    </motion.div>
                  ))}
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="pt-3 mt-2 border-t border-white/[0.07] flex flex-col gap-2.5"
                  >
                    <Link href="/login" className="px-3 text-[14px] text-white/45 hover:text-white">
                      log in
                    </Link>
                    <Link
                      href="/signup"
                      className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full text-[14px] font-semibold w-fit bg-white text-[#080d1e]"
                    >
                      get started →
                    </Link>
                  </motion.div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.header>
      </div>

      {/* Spacer so page content clears the pill height */}
      <div className="h-20" aria-hidden="true" />
    </>
  )
}
