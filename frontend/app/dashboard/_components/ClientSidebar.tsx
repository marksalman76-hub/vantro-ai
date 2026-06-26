'use client'

// Ported from src/components/DashboardSidebar.tsx (master branch) — adapted for Next.js App Router
import { usePathname, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useEffect, useRef, useState } from 'react'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'

// ─── SVG icon components ──────────────────────────────────────────────────────

function IconDashboard({ color }: { color: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <rect x="1" y="1" width="6" height="6" rx="1.5" stroke={color} strokeWidth="1.4" />
      <rect x="9" y="1" width="6" height="6" rx="1.5" stroke={color} strokeWidth="1.4" />
      <rect x="1" y="9" width="6" height="6" rx="1.5" stroke={color} strokeWidth="1.4" />
      <rect x="9" y="9" width="6" height="6" rx="1.5" stroke={color} strokeWidth="1.4" />
    </svg>
  )
}

function IconAgents({ color }: { color: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="8" cy="5" r="3" stroke={color} strokeWidth="1.4" />
      <path d="M2 14c0-3.314 2.686-5 6-5s6 1.686 6 5" stroke={color} strokeWidth="1.4" strokeLinecap="round" />
      <circle cx="13" cy="5" r="1.5" stroke={color} strokeWidth="1.2" />
      <path d="M15 10.5c-.6-1-1.5-1.5-2-1.5" stroke={color} strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  )
}

function IconCreative({ color }: { color: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M2 12L6 4l4 6 2-3 2 5" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="13" cy="3" r="1.5" stroke={color} strokeWidth="1.2" />
    </svg>
  )
}

function IconActivity({ color }: { color: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <polyline points="1,8 4,8 5.5,3 7.5,13 9.5,6 11,10 12.5,8 15,8" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function IconLibrary({ color }: { color: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <rect x="1" y="3" width="14" height="10" rx="1.5" stroke={color} strokeWidth="1.4" />
      <line x1="1" y1="6.5" x2="15" y2="6.5" stroke={color} strokeWidth="1.2" />
      <line x1="5" y1="3" x2="5" y2="13" stroke={color} strokeWidth="1.2" />
    </svg>
  )
}

function IconBrand({ color }: { color: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M8 1L10 6H15L11 9.5L12.5 14.5L8 11.5L3.5 14.5L5 9.5L1 6H6L8 1Z" stroke={color} strokeWidth="1.3" strokeLinejoin="round" />
    </svg>
  )
}

function IconSettings({ color }: { color: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="8" cy="8" r="2.5" stroke={color} strokeWidth="1.4" />
      <path d="M8 1v1.5M8 13.5V15M1 8h1.5M13.5 8H15M2.93 2.93l1.06 1.06M12.01 12.01l1.06 1.06M13.07 2.93l-1.06 1.06M3.99 12.01l-1.06 1.06" stroke={color} strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  )
}

// IconSignOut uses currentColor so it inherits the button's CSS color on hover
function IconSignOut() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style={{ flexShrink: 0 }}>
      <path d="M5.5 13H2.5C1.948 13 1.5 12.552 1.5 12V3C1.5 2.448 1.948 2 2.5 2H5.5" stroke="currentColor" strokeWidth="1.35" strokeLinecap="round" />
      <path d="M10 10.5L13.5 7.5L10 4.5" stroke="currentColor" strokeWidth="1.35" strokeLinecap="round" strokeLinejoin="round" />
      <line x1="13.5" y1="7.5" x2="5.5" y2="7.5" stroke="currentColor" strokeWidth="1.35" strokeLinecap="round" />
    </svg>
  )
}

// ─── NavRow ───────────────────────────────────────────────────────────────────
// Isolated component so each nav item gets its own GSAP hover ref.
function NavRow({
  active,
  ORANGE,
  iconColor,
  textColor,
  children,
}: {
  active: boolean
  ORANGE: string
  iconColor: string
  textColor: string
  children: React.ReactNode
}) {
  const rowRef = useRef<HTMLDivElement>(null)

  function handleEnter() {
    if (active) return
    gsap.to(rowRef.current, {
      x: 3,
      color: 'rgba(255,255,255,0.80)',
      background: 'rgba(255,255,255,0.04)',
      duration: 0.16,
      ease: 'power2.out',
    })
  }

  function handleLeave() {
    if (active) return
    gsap.to(rowRef.current, {
      x: 0,
      color: textColor,
      background: 'transparent',
      duration: 0.22,
      ease: 'power3.out',
    })
  }

  // Flash a ring on the active item when it first becomes active
  const didFlash = useRef(false)
  useEffect(() => {
    if (!active || didFlash.current || !rowRef.current) return
    didFlash.current = true
    gsap.fromTo(
      rowRef.current,
      { boxShadow: `0 0 0 3px ${ORANGE}55` },
      { boxShadow: '0 0 0 0px rgba(0,0,0,0)', duration: 0.5, ease: 'power2.out' }
    )
    const t = setTimeout(() => { didFlash.current = false }, 600)
    return () => clearTimeout(t)
  }, [active, ORANGE])

  return (
    <div
      ref={rowRef}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.625rem',
        padding: '0.475rem 0.75rem',
        borderRadius: '0.5rem',
        fontSize: '0.84rem',
        fontWeight: active ? 500 : 400,
        cursor: 'pointer',
        borderLeft: active ? `3px solid ${ORANGE}` : '3px solid transparent',
        background: active ? `${ORANGE}0F` : 'transparent',
        border: active ? `1px solid ${ORANGE}22` : '1px solid transparent',
        borderLeftWidth: 3,
        color: textColor,
        paddingLeft: active ? 'calc(0.75rem - 2px)' : '0.75rem',
        willChange: 'transform',
      }}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      {children}
    </div>
  )
}

// ─── Nav config ───────────────────────────────────────────────────────────────

type NavItem = {
  href: string
  label: string
  Icon: React.FC<{ color: string }>
  exact: boolean
}

const NAV: NavItem[] = [
  { href: '/dashboard',          label: 'Dashboard',       Icon: IconDashboard, exact: true },
  { href: '/dashboard/agents',   label: 'Run agents',      Icon: IconAgents,    exact: false },
  { href: '/dashboard/creative', label: 'Creative Studio', Icon: IconCreative,  exact: false },
  { href: '/dashboard/jobs',     label: 'Activity',        Icon: IconActivity,  exact: false },
  { href: '/dashboard/library',  label: 'Output library',  Icon: IconLibrary,   exact: false },
  { href: '/dashboard/brand',    label: 'Brand profile',   Icon: IconBrand,     exact: false },
  { href: '/dashboard/settings', label: 'Settings',        Icon: IconSettings,  exact: false },
]

// ─── Component ────────────────────────────────────────────────────────────────

export default function ClientSidebar() {
  const pathname  = usePathname()
  const router    = useRouter()
  const [workspace, setWorkspace] = useState('')
  const [email,     setEmail]     = useState('')
  const [initial,   setInitial]   = useState('U')
  const [plan,      setPlan]      = useState('Starter')

  // ── Refs for GSAP scope ─────────────────────────────────────────────────────
  const sidebarRef  = useRef<HTMLElement>(null)
  const signOutRef  = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    const w = localStorage.getItem('workspace_name')
    if (w) setWorkspace(w)

    const e = localStorage.getItem('email')
    if (e) {
      setEmail(e)
      setInitial(e.charAt(0).toUpperCase())
    }

    const savedPlan = localStorage.getItem('plan')
    if (savedPlan) setPlan(savedPlan.charAt(0).toUpperCase() + savedPlan.slice(1))
  }, [])

  // ── 1. Sidebar mount animation ─────────────────────────────────────────────
  // Slides the whole sidebar in from the left, then staggers nav items.
  useGSAP(() => {
    // Sidebar panel slides in from x:-24
    gsap.fromTo(
      sidebarRef.current,
      { x: -24, opacity: 0 },
      { x: 0, opacity: 1, duration: 0.48, ease: 'power3.out', delay: 0.04 }
    )
    // Nav items stagger upward after panel arrives
    const items = sidebarRef.current?.querySelectorAll<HTMLElement>('[data-nav-item]')
    if (items?.length) {
      gsap.fromTo(
        items,
        { x: -12, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.30, stagger: 0.05, ease: 'power2.out', delay: 0.20 }
      )
    }
  }, { scope: sidebarRef })

  function signOut() {
    localStorage.removeItem('token')
    localStorage.removeItem('onboarding_complete')
    router.push('/login')
  }

  function isActive(href: string, exact: boolean) {
    return exact ? pathname === href : pathname?.startsWith(href)
  }

  // ── Styles ──────────────────────────────────────────────────────────────────

  const ORANGE = '#FF6B35'
  const CYAN   = '#00D9FF'

  const sidebarStyle: React.CSSProperties = {
    width: 224,
    minWidth: 224,
    height: '100vh',
    position: 'sticky',
    top: 0,
    display: 'flex',
    flexDirection: 'column',
    background: 'rgba(10,13,20,0.95)',
    borderRight: '1px solid rgba(255,255,255,0.07)',
    backdropFilter: 'blur(20px)',
    flexShrink: 0,
    overflowY: 'auto',
    overflowX: 'hidden',
  }

  return (
    <aside ref={sidebarRef} style={{ ...sidebarStyle, willChange: 'transform' }}>

      {/* ── Logo ─────────────────────────────────────────────────────────── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '1.375rem 1.25rem 1.125rem',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        flexShrink: 0,
      }}>
        <div style={{
          width: 26,
          height: 26,
          borderRadius: 7,
          background: `linear-gradient(135deg,${ORANGE},${CYAN})`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 900,
          fontSize: 12,
          color: '#fff',
          flexShrink: 0,
        }}>V</div>
        <span style={{ fontWeight: 700, fontSize: '0.875rem', letterSpacing: '0.09em', color: '#fff' }}>
          VANTRO<span style={{ color: CYAN, fontWeight: 400 }}>.ai</span>
        </span>
      </div>

      {/* ── Workspace + Plan badge ────────────────────────────────────────── */}
      <div style={{
        padding: '0.75rem 1.25rem 0.875rem',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        flexShrink: 0,
      }}>
        <p style={{
          fontSize: 9.5,
          color: 'rgba(255,255,255,0.22)',
          textTransform: 'uppercase',
          letterSpacing: '0.09em',
          marginBottom: 3,
        }}>Workspace</p>
        <p style={{
          fontSize: 12.5,
          color: 'rgba(255,255,255,0.8)',
          fontWeight: 600,
          marginBottom: 8,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}>{workspace || 'My workspace'}</p>

        {/* Plan badge */}
        <span style={{
          display: 'inline-block',
          fontSize: 9,
          fontWeight: 700,
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: ORANGE,
          background: `${ORANGE}1A`,
          border: `1px solid ${ORANGE}40`,
          borderRadius: 4,
          padding: '2px 7px',
        }}>{plan}</span>
      </div>

      {/* ── Nav ──────────────────────────────────────────────────────────── */}
      <nav
        role="navigation"
        aria-label="Main navigation"
        style={{
        flex: 1,
        padding: '0.625rem 0.625rem',
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
      }}>
        {NAV.map(({ href, label, Icon, exact }) => {
          const active = isActive(href, exact)
          const iconColor = active ? ORANGE : 'rgba(255,255,255,0.35)'
          const textColor = active ? '#fff' : 'rgba(255,255,255,0.42)'

          return (
            // data-nav-item is the stagger selector target in useGSAP above
            <Link key={href} href={href} style={{ textDecoration: 'none' }} data-nav-item aria-current={isActive(href, exact) ? 'page' : undefined}>
              <NavRow active={active} ORANGE={ORANGE} iconColor={iconColor} textColor={textColor}>
                <Icon color={iconColor} />
                <span>{label}</span>
              </NavRow>
            </Link>
          )
        })}
      </nav>

      {/* ── User footer ──────────────────────────────────────────────────── */}
      <div style={{
        borderTop: '1px solid rgba(255,255,255,0.06)',
        padding: '0.75rem 0.875rem',
        flexShrink: 0,
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
      }}>

        {/* Avatar + email row */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.625rem',
          padding: '0.375rem 0.375rem',
          borderRadius: '0.5rem',
        }}>
          {/* Avatar circle */}
          <div style={{
            width: 30,
            height: 30,
            borderRadius: '50%',
            background: `linear-gradient(135deg, ${ORANGE}CC, ${ORANGE}66)`,
            border: `1.5px solid ${ORANGE}55`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: 13,
            color: '#fff',
            flexShrink: 0,
            lineHeight: 1,
          }}>{initial}</div>

          {/* Email text */}
          <div style={{ overflow: 'hidden', flex: 1 }}>
            <p style={{
              fontSize: 11,
              color: 'rgba(255,255,255,0.55)',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              lineHeight: 1.3,
            }}>{email || 'Your workspace'}</p>
          </div>
        </div>

        {/* Sign out button — GSAP hover */}
        <button
          ref={signOutRef}
          type="button"
          onClick={signOut}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.42rem 0.75rem',
            borderRadius: '0.5rem',
            fontSize: '0.8rem',
            fontWeight: 400,
            color: 'rgba(255,255,255,0.32)',
            background: 'transparent',
            border: '1px solid transparent',
            cursor: 'pointer',
            textAlign: 'left',
            fontFamily: 'inherit',
            willChange: 'transform',
          }}
          onMouseEnter={() => {
            gsap.to(signOutRef.current, {
              x: 2,
              color: '#FF6B35',
              background: 'rgba(255,107,53,0.08)',
              duration: 0.16,
              ease: 'power2.out',
            })
          }}
          onMouseLeave={() => {
            gsap.to(signOutRef.current, {
              x: 0,
              color: 'rgba(255,255,255,0.32)',
              background: 'transparent',
              duration: 0.22,
              ease: 'power3.out',
            })
          }}
        >
          <IconSignOut />
          Sign out
        </button>
      </div>

    </aside>
  )
}
