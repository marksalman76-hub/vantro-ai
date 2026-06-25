'use client'

// Ported from src/components/DashboardSidebar.tsx (master branch) — adapted for Next.js App Router
import { usePathname, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useEffect, useState } from 'react'

const NAV = [
  { href: '/dashboard',          label: 'Dashboard',      icon: '◈', exact: true },
  { href: '/dashboard/agents',   label: 'Run agents',     icon: '◆', exact: false },
  { href: '/dashboard/jobs',     label: 'Activity',       icon: '⬡', exact: false },
  { href: '/dashboard/library',  label: 'Output library', icon: '▣', exact: false },
  { href: '/dashboard/brand',    label: 'Brand profile',  icon: '◎', exact: false },
  { href: '/dashboard/settings', label: 'Settings',       icon: '◌', exact: false },
]

export default function ClientSidebar() {
  const pathname = usePathname()
  const router   = useRouter()
  const [workspace, setWorkspace] = useState('')

  useEffect(() => {
    const w = localStorage.getItem('workspace_name')
    if (w) setWorkspace(w)
  }, [])

  function signOut() {
    localStorage.removeItem('token')
    localStorage.removeItem('onboarding_complete')
    router.push('/login')
  }

  function isActive(href: string, exact: boolean) {
    return exact ? pathname === href : pathname?.startsWith(href)
  }

  return (
    <aside style={{ width: 220, minWidth: 220, height: '100vh', position: 'sticky', top: 0, display: 'flex', flexDirection: 'column', background: 'rgba(10,13,20,0.90)', borderRight: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(20px)', flexShrink: 0 }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1.5rem 1.25rem 1.25rem', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ width: 24, height: 24, borderRadius: 6, background: 'linear-gradient(135deg,#FF6B35,#00D9FF)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: 11, color: '#fff' }}>V</div>
        <span style={{ fontWeight: 700, fontSize: '0.9rem', letterSpacing: '0.08em', color: '#fff' }}>
          VANTRO<span style={{ color: '#00D9FF', fontWeight: 400 }}>.ai</span>
        </span>
      </div>

      {/* Workspace */}
      {workspace && (
        <div style={{ padding: '0.75rem 1.25rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <p style={{ fontSize: 10, color: 'rgba(255,255,255,0.25)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 2 }}>Workspace</p>
          <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>{workspace}</p>
        </div>
      )}

      {/* Nav */}
      <nav style={{ flex: 1, padding: '0.75rem 0.625rem', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV.map(({ href, label, icon, exact }) => {
          const active = isActive(href, exact)
          return (
            <Link key={href} href={href} style={{ textDecoration: 'none' }}>
              <div
                style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', padding: '0.5rem 0.75rem', borderRadius: '0.625rem', fontSize: '0.85rem', fontWeight: active ? 500 : 400, transition: 'all 0.15s', cursor: 'pointer', background: active ? 'rgba(0,217,255,0.10)' : 'transparent', border: active ? '1px solid rgba(0,217,255,0.20)' : '1px solid transparent', color: active ? '#00D9FF' : 'rgba(255,255,255,0.4)' }}
                onMouseEnter={e => { if (!active) { const el = e.currentTarget as HTMLElement; el.style.color = 'rgba(255,255,255,0.8)'; el.style.background = 'rgba(255,255,255,0.04)' } }}
                onMouseLeave={e => { if (!active) { const el = e.currentTarget as HTMLElement; el.style.color = 'rgba(255,255,255,0.4)'; el.style.background = 'transparent' } }}
              >
                <span style={{ fontSize: '0.9rem', lineHeight: 1 }}>{icon}</span>
                {label}
              </div>
            </Link>
          )
        })}
      </nav>

      {/* Sign out */}
      <div style={{ padding: '0.75rem 0.625rem', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <button
          onClick={signOut}
          style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.625rem', padding: '0.5rem 0.75rem', borderRadius: '0.625rem', fontSize: '0.82rem', fontWeight: 400, color: 'rgba(255,255,255,0.3)', background: 'transparent', border: '1px solid transparent', cursor: 'pointer', transition: 'all 0.15s', textAlign: 'left', fontFamily: 'inherit' }}
          onMouseEnter={e => { const el = e.currentTarget as HTMLElement; el.style.color = 'oklch(0.65 0.18 25)'; el.style.background = 'oklch(0.65 0.18 25 / 0.08)' }}
          onMouseLeave={e => { const el = e.currentTarget as HTMLElement; el.style.color = 'rgba(255,255,255,0.3)'; el.style.background = 'transparent' }}
        >
          <span style={{ fontSize: '0.85rem' }}>↩</span> Sign out
        </button>
      </div>
    </aside>
  )
}
