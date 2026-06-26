'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useGSAP } from '@gsap/react'

gsap.registerPlugin(ScrollTrigger)

const NAV_LINKS = [
  { label: 'Features', href: '#features' },
  { label: 'Agents', href: '#agents' },
  { label: 'Integrations', href: '#integrations' },
  { label: 'Pricing', href: '#pricing' },
]

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [activeLink, setActiveLink] = useState('')
  const [hoveredLink, setHoveredLink] = useState<string | null>(null)
  const [ctaPressed, setCtaPressed] = useState(false)

  const navRef = useRef<HTMLElement>(null)

  // Scroll listener for background state — threshold 20px
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Close mobile menu on resize to desktop
  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth >= 768) setMobileOpen(false)
    }
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  // GSAP mount animation + ScrollTrigger glow
  useGSAP(() => {
    if (!navRef.current) return

    // Mount animation: slide down from above
    gsap.from(navRef.current, {
      y: -80,
      opacity: 0,
      duration: 0.7,
      ease: 'power3.out',
    })

    // Stagger nav links
    gsap.from('.nav-link', {
      y: -20,
      opacity: 0,
      stagger: 0.08,
      delay: 0.3,
      duration: 0.5,
      ease: 'power2.out',
    })

    // ScrollTrigger: add glow text-shadow after 300px
    ScrollTrigger.create({
      start: 300,
      onEnter: () => {
        gsap.to('.nav-link', {
          textShadow: '0 0 20px rgba(0,217,255,0.15)',
          duration: 0.5,
          ease: 'power2.out',
        })
      },
      onLeaveBack: () => {
        gsap.to('.nav-link', {
          textShadow: 'none',
          duration: 0.4,
          ease: 'power2.out',
        })
      },
    })
  }, [])

  const scrolledStyles: React.CSSProperties = {
    background: 'rgba(10,13,17,0.88)',
    backdropFilter: 'blur(20px) saturate(180%)',
    WebkitBackdropFilter: 'blur(20px) saturate(180%)',
    borderBottom: '1px solid rgba(0,217,255,0.15)',
    boxShadow: '0 0 40px rgba(0,0,0,0.4), 0 1px 0 rgba(0,217,255,0.08)',
  }

  const notScrolledStyles: React.CSSProperties = {
    background: 'rgba(15,20,25,0.3)',
    backdropFilter: 'blur(8px)',
    WebkitBackdropFilter: 'blur(8px)',
    borderBottom: '1px solid transparent',
    boxShadow: 'none',
  }

  return (
    <>
      <nav
        ref={navRef}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          height: 72,
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          transition: 'background 0.3s ease, backdrop-filter 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease',
          ...(scrolled ? scrolledStyles : notScrolledStyles),
        }}
      >
        <div
          style={{
            maxWidth: 1280,
            margin: '0 auto',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            gap: 0,
          }}
        >
          {/* ── Logo ── */}
          <a
            href="/"
            style={{
              textDecoration: 'none',
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'center',
              gap: 2,
              flexShrink: 0,
            }}
          >
            <span style={{ color: '#FF6B35', fontWeight: 700, fontSize: 26, lineHeight: 1 }}>V</span>
            <span style={{ color: '#ffffff', fontWeight: 700, fontSize: 26, lineHeight: 1 }}>antro</span>
          </a>

          {/* ── Desktop Nav Links ── */}
          <div
            className="desktop-nav"
            style={{
              display: 'flex',
              flexDirection: 'row',
              gap: 4,
              marginLeft: 'auto',
              alignItems: 'center',
            }}
          >
            {NAV_LINKS.map((link) => {
              const isActive = activeLink === link.href
              const isHovered = hoveredLink === link.href
              return (
                <motion.a
                  key={link.label}
                  href={link.href}
                  className="nav-link"
                  onClick={() => setActiveLink(link.href)}
                  onMouseEnter={() => setHoveredLink(link.href)}
                  onMouseLeave={() => setHoveredLink(null)}
                  whileHover={{
                    color: '#ffffff',
                    backgroundColor: 'rgba(255,255,255,0.06)',
                  }}
                  style={{
                    padding: '8px 16px',
                    borderRadius: 10,
                    fontSize: 14,
                    fontWeight: 500,
                    color: isActive ? '#fff' : 'rgba(255,255,255,0.65)',
                    textDecoration: 'none',
                    position: 'relative',
                    display: 'inline-flex',
                    alignItems: 'center',
                    transition: 'color 150ms ease, background-color 150ms ease',
                    cursor: 'pointer',
                  }}
                >
                  {link.label}
                  {/* Underline slide-in on hover (when not already the active link) */}
                  {!isActive && (
                    <span
                      style={{
                        position: 'absolute',
                        bottom: 4,
                        left: '16px',
                        height: 1.5,
                        borderRadius: 2,
                        background: 'rgba(0,217,255,0.7)',
                        width: isHovered ? 'calc(100% - 32px)' : '0%',
                        transition: 'width 200ms ease-out',
                      }}
                    />
                  )}
                  {isActive && (
                    <motion.span
                      layoutId="nav-active-line"
                      style={{
                        position: 'absolute',
                        bottom: 2,
                        left: '20%',
                        right: '20%',
                        height: 2,
                        borderRadius: 2,
                        background: '#FF6B35',
                        boxShadow: '0 0 8px #FF6B3588',
                      }}
                    />
                  )}
                </motion.a>
              )
            })}
          </div>

          {/* ── Right Side: Login + CTA + Hamburger ── */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'row',
              gap: 12,
              alignItems: 'center',
              marginLeft: 24,
            }}
          >
            {/* Login link — hidden on mobile */}
            <motion.a
              href="/login"
              className="desktop-only"
              whileHover={{
                color: '#ffffff',
                backgroundColor: 'rgba(255,255,255,0.06)',
              }}
              style={{
                fontSize: 14,
                fontWeight: 500,
                color: 'rgba(255,255,255,0.6)',
                padding: '8px 12px',
                borderRadius: 10,
                textDecoration: 'none',
                transition: 'color 150ms ease, background 150ms ease',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
              }}
            >
              Login
            </motion.a>

            {/* Deploy Now CTA — hidden on mobile */}
            <motion.a
              href="#pricing"
              className="desktop-only"
              whileHover={{
                scale: 1.04,
                boxShadow: '0 0 36px rgba(255,107,53,0.65)',
              }}
              whileTap={{ scale: 0.97 }}
              onMouseDown={() => setCtaPressed(true)}
              onMouseUp={() => setCtaPressed(false)}
              onMouseLeave={() => setCtaPressed(false)}
              style={{
                background: 'linear-gradient(135deg, #FF6B35 0%, #E8521A 100%)',
                color: '#fff',
                fontWeight: 700,
                fontSize: 14,
                padding: '10px 24px',
                borderRadius: 10,
                boxShadow: ctaPressed
                  ? '0 0 16px rgba(255,107,53,0.3)'
                  : '0 0 24px rgba(255,107,53,0.45)',
                textDecoration: 'none',
                transition: 'transform 150ms ease-out, box-shadow 150ms ease-out',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                display: 'inline-block',
              }}
            >
              Deploy Now
            </motion.a>

            {/* Mobile Hamburger */}
            <button
              className="hamburger-btn"
              onClick={() => setMobileOpen((prev) => !prev)}
              aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileOpen}
              style={{
                width: 44,
                height: 44,
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: 10,
                display: 'none', // shown via media query in <style>
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: 8,
                flexShrink: 0,
              }}
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                style={{ overflow: 'visible' }}
              >
                <AnimatePresence mode="wait" initial={false}>
                  {mobileOpen ? (
                    <motion.g
                      key="x"
                      initial={{ opacity: 0, rotate: -45 }}
                      animate={{ opacity: 1, rotate: 0 }}
                      exit={{ opacity: 0, rotate: 45 }}
                      transition={{ duration: 0.2, ease: 'easeInOut' }}
                    >
                      <line
                        x1="4"
                        y1="4"
                        x2="20"
                        y2="20"
                        stroke="white"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                      <line
                        x1="20"
                        y1="4"
                        x2="4"
                        y2="20"
                        stroke="white"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </motion.g>
                  ) : (
                    <motion.g
                      key="hamburger"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <line
                        x1="3"
                        y1="7"
                        x2="21"
                        y2="7"
                        stroke="white"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                      <line
                        x1="3"
                        y1="12"
                        x2="21"
                        y2="12"
                        stroke="white"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                      <line
                        x1="3"
                        y1="17"
                        x2="21"
                        y2="17"
                        stroke="white"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </motion.g>
                  )}
                </AnimatePresence>
              </svg>
            </button>
          </div>
        </div>
      </nav>

      {/* ── Mobile Drawer ── */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            key="mobile-drawer"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.25, ease: [0.23, 1, 0.32, 1] }}
            style={{
              position: 'fixed',
              top: 72,
              left: 0,
              right: 0,
              zIndex: 999,
              background: 'rgba(10,13,17,0.97)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              padding: 24,
              display: 'flex',
              flexDirection: 'column',
              gap: 8,
              borderBottom: '1px solid rgba(255,255,255,0.1)',
            }}
          >
            {NAV_LINKS.map((link, i) => (
              <motion.a
                key={link.label}
                href={link.href}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06, duration: 0.25, ease: 'easeOut' }}
                onClick={() => {
                  setActiveLink(link.href)
                  setMobileOpen(false)
                }}
                style={{
                  display: 'block',
                  padding: '14px 16px',
                  borderRadius: 12,
                  color: activeLink === link.href ? '#fff' : 'rgba(255,255,255,0.7)',
                  background:
                    activeLink === link.href ? 'rgba(255,107,53,0.12)' : 'transparent',
                  textDecoration: 'none',
                  fontSize: 16,
                  fontWeight: 500,
                  transition: 'background 150ms ease, color 150ms ease',
                  cursor: 'pointer',
                }}
              >
                {link.label}
              </motion.a>
            ))}

            {/* Divider */}
            <div
              style={{
                height: 1,
                background: 'rgba(255,255,255,0.08)',
                margin: '8px 0',
              }}
            />

            {/* Mobile Login */}
            <a
              href="/login"
              onClick={() => setMobileOpen(false)}
              style={{
                display: 'block',
                padding: '14px 16px',
                borderRadius: 12,
                color: 'rgba(255,255,255,0.7)',
                textDecoration: 'none',
                fontSize: 16,
                fontWeight: 500,
                transition: 'background 150ms ease, color 150ms ease',
                cursor: 'pointer',
              }}
            >
              Login
            </a>

            {/* Mobile Deploy Now CTA */}
            <motion.a
              href="#pricing"
              whileTap={{ scale: 0.98 }}
              onClick={() => setMobileOpen(false)}
              style={{
                display: 'block',
                padding: '14px 16px',
                borderRadius: 12,
                background: 'linear-gradient(135deg, #FF6B35 0%, #E8521A 100%)',
                color: '#fff',
                textDecoration: 'none',
                fontSize: 16,
                fontWeight: 700,
                textAlign: 'center',
                boxShadow: '0 0 24px rgba(255,107,53,0.4)',
                cursor: 'pointer',
                marginTop: 4,
              }}
            >
              Deploy Now
            </motion.a>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Responsive styles ── */}
      <style>{`
        @media (max-width: 767px) {
          .hamburger-btn {
            display: flex !important;
          }
          .desktop-nav {
            display: none !important;
          }
          .desktop-only {
            display: none !important;
          }
        }
        @media (min-width: 768px) {
          .hamburger-btn {
            display: none !important;
          }
          .desktop-nav {
            display: flex !important;
          }
          .desktop-only {
            display: inline-block !important;
          }
        }
      `}</style>
    </>
  )
}
