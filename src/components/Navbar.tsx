import { useState, useEffect, useRef } from 'react'
import { Menu, X } from 'lucide-react'

const NAV_LINKS = [
  { label: 'Features', href: '#features' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Agents', href: '#agents' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
]

export function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const overlayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Close mobile menu on route changes or outside clicks
  useEffect(() => {
    if (!mobileOpen) return
    const handle = (e: MouseEvent) => {
      if (overlayRef.current && !overlayRef.current.contains(e.target as Node)) {
        setMobileOpen(false)
      }
    }
    document.addEventListener('mousedown', handle)
    return () => document.removeEventListener('mousedown', handle)
  }, [mobileOpen])

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [mobileOpen])

  return (
    <>
      <nav
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 100,
          transition: 'background 0.3s ease, border-color 0.3s ease, backdrop-filter 0.3s ease',
          background: scrolled
            ? 'oklch(0.14 0 0 / 0.85)'
            : 'transparent',
          backdropFilter: scrolled ? 'blur(16px) saturate(1.4)' : 'none',
          WebkitBackdropFilter: scrolled ? 'blur(16px) saturate(1.4)' : 'none',
          borderBottom: scrolled
            ? '1px solid oklch(0.97 0 0 / 0.07)'
            : '1px solid transparent',
        }}
      >
        <div
          style={{
            maxWidth: '80rem',
            margin: '0 auto',
            padding: '0 1.5rem',
            height: scrolled ? '3.25rem' : '4rem',
            transition: 'height 0.3s ease',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          {/* Logo */}
          <a
            href="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              textDecoration: 'none',
              flexShrink: 0,
            }}
          >
            <img
              src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/uLNNHswnlaLuEQJY.png"
              alt="Vantro logo"
              style={{ height: '2rem', width: 'auto' }}
            />
            <span
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700,
                fontSize: '1.1rem',
                color: 'oklch(0.97 0 0)',
                letterSpacing: '-0.01em',
              }}
            >
              VANTRO
            </span>
            <span
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 400,
                fontSize: '1.1rem',
                color: 'oklch(0.70 0 0)',
              }}
            >
              .ai
            </span>
          </a>

          {/* Center nav - desktop only */}
          <ul
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '2rem',
              listStyle: 'none',
              margin: 0,
              padding: 0,
            }}
            className="hidden md:flex"
          >
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: '0.875rem',
                    color: 'oklch(0.70 0 0)',
                    textDecoration: 'none',
                    transition: 'color 0.2s ease',
                  }}
                  onMouseEnter={(e) =>
                    ((e.target as HTMLAnchorElement).style.color = 'oklch(0.97 0 0)')
                  }
                  onMouseLeave={(e) =>
                    ((e.target as HTMLAnchorElement).style.color = 'oklch(0.70 0 0)')
                  }
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>

          {/* Right actions - desktop */}
          <div
            style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}
            className="hidden md:flex"
          >
            <a
              href="https://app.vantro.ai/login"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.875rem',
                color: 'oklch(0.70 0 0)',
                padding: '0.5rem 0.75rem',
                borderRadius: '0.5rem',
                transition: 'color 0.2s ease',
                textDecoration: 'none',
              }}
              onMouseEnter={(e) =>
                ((e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.97 0 0)')
              }
              onMouseLeave={(e) =>
                ((e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.70 0 0)')
              }
            >
              Sign in
            </a>
            <a
              href="https://app.vantro.ai/signup"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                background: 'linear-gradient(180deg, #ffffff 0%, #d8d8d8 100%)',
                color: 'oklch(0.14 0 0)',
                border: 'none',
                cursor: 'pointer',
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.875rem',
                fontWeight: 600,
                padding: '0.5rem 1.25rem',
                borderRadius: '9999px',
                boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.60), 0 2px 8px rgba(0,0,0,0.35)',
                transition: 'opacity 0.2s ease, transform 0.15s ease',
                textDecoration: 'none',
                display: 'inline-block',
              }}
              onMouseEnter={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.opacity = '0.88'
                ;(e.currentTarget as HTMLAnchorElement).style.transform = 'scale(1.02)'
              }}
              onMouseLeave={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.opacity = '1'
                ;(e.currentTarget as HTMLAnchorElement).style.transform = 'scale(1)'
              }}
            >
              Activate agents
            </a>
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'oklch(0.97 0 0)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '0.5rem',
            }}
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </nav>

      {/* Mobile overlay sheet */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 99,
          background: 'oklch(0.10 0 0 / 0.6)',
          opacity: mobileOpen ? 1 : 0,
          pointerEvents: mobileOpen ? 'auto' : 'none',
          transition: 'opacity 0.3s ease',
        }}
      >
        <div
          ref={overlayRef}
          style={{
            position: 'absolute',
            top: '4rem',
            left: 0,
            right: 0,
            background: 'oklch(0.20 0 0 / 0.96)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            borderBottom: '1px solid oklch(0.97 0 0 / 0.08)',
            padding: '1.5rem',
            transform: mobileOpen ? 'translateY(0)' : 'translateY(-1rem)',
            opacity: mobileOpen ? 1 : 0,
            transition: 'transform 0.3s ease, opacity 0.3s ease',
          }}
        >
          <ul
            style={{
              listStyle: 'none',
              margin: 0,
              padding: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: '0.25rem',
            }}
          >
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  style={{
                    display: 'block',
                    fontFamily: "'Inter', sans-serif",
                    fontSize: '1rem',
                    color: 'oklch(0.70 0 0)',
                    textDecoration: 'none',
                    padding: '0.75rem 0',
                    borderBottom: '1px solid oklch(0.97 0 0 / 0.05)',
                    transition: 'color 0.2s ease',
                  }}
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '0.75rem',
              marginTop: '1.25rem',
            }}
          >
            <a
              href="https://app.vantro.ai/login"
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => setMobileOpen(false)}
              style={{
                background: 'none',
                border: '1px solid oklch(0.97 0 0 / 0.15)',
                cursor: 'pointer',
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.9375rem',
                color: 'oklch(0.97 0 0)',
                padding: '0.75rem',
                borderRadius: '0.75rem',
                textAlign: 'center',
                textDecoration: 'none',
              }}
            >
              Sign in
            </a>
            <a
              href="https://app.vantro.ai/signup"
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => setMobileOpen(false)}
              style={{
                background: 'oklch(0.97 0 0)',
                color: 'oklch(0.14 0 0)',
                border: 'none',
                cursor: 'pointer',
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.9375rem',
                fontWeight: 600,
                padding: '0.75rem',
                borderRadius: '9999px',
                textAlign: 'center',
                textDecoration: 'none',
                display: 'inline-block',
              }}
            >
              Activate agents
            </a>
          </div>
        </div>
      </div>
    </>
  )
}
