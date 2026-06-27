'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import ThemeToggle from '@/components/ThemeToggle'

const NAV = [
  { label: 'Overview',       href: '/admin' },
  { label: 'Run Agents',     href: '/admin/agents' },
  { label: 'Creative Studio',href: '/admin/creative' },
  { label: 'Jobs',           href: '/admin/jobs' },
  { label: 'Library',        href: '/admin/library' },
  { label: 'Secrets',        href: '/admin/secrets' },
]

const LS_KEY = 'vantro_admin_sidebar_collapsed'

export default function ClientAdminSidebar({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)

  // Hydrate from localStorage after mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(LS_KEY)
      if (stored !== null) setCollapsed(stored === 'true')
    } catch {}
  }, [])

  function toggle() {
    setCollapsed(prev => {
      const next = !prev
      try { localStorage.setItem(LS_KEY, String(next)) } catch {}
      return next
    })
  }

  const sidebarWidth = collapsed ? 56 : 220

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--t-bg)' }}>
      {/* ── Sidebar ── */}
      <aside
        style={{
          width: sidebarWidth,
          background: 'var(--t-sidebar)',
          borderRight: '1px solid var(--t-border)',
          padding: '1.5rem 0',
          flexShrink: 0,
          position: 'fixed',
          top: 0,
          left: 0,
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          transition: 'width 0.22s ease',
          overflow: 'hidden',
        }}
      >
        {/* Header row — logo text (hidden when collapsed) + toggle button */}
        <div
          style={{
            padding: '0 0.75rem 1.5rem',
            borderBottom: '1px solid var(--t-border)',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: collapsed ? 'center' : 'space-between',
            gap: '0.5rem',
            minWidth: sidebarWidth,
          }}
        >
          {!collapsed && (
            <div style={{ overflow: 'hidden', flexShrink: 1 }}>
              <div style={{ fontSize: 10, color: '#1FFFD6', letterSpacing: '0.2em', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>
                Vantro
              </div>
              <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--t-text-1)', marginTop: 2, whiteSpace: 'nowrap' }}>
                Admin Portal
              </div>
            </div>
          )}

          {/* Toggle button */}
          <button
            onClick={toggle}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--t-text-2)',
              fontSize: 18,
              lineHeight: 1,
              padding: '2px 4px',
              borderRadius: 4,
              flexShrink: 0,
              marginTop: collapsed ? 0 : 4,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'color 0.15s',
            }}
          >
            {collapsed ? '›' : '‹'}
          </button>
        </div>

        {/* Nav links — hidden when collapsed */}
        {!collapsed && (
          <nav style={{ padding: '1rem 0', flex: 1 }}>
            {NAV.map(n => (
              <Link
                key={n.href}
                href={n.href}
                style={{
                  display: 'block',
                  padding: '0.6rem 1.25rem',
                  color: 'var(--t-text-2)',
                  fontSize: 13,
                  textDecoration: 'none',
                  transition: 'color 0.15s',
                  fontFamily: "'Space Grotesk', sans-serif",
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {n.label}
              </Link>
            ))}
          </nav>
        )}

        {/* Spacer when collapsed so ThemeToggle stays at bottom */}
        {collapsed && <div style={{ flex: 1 }} />}

        {/* ThemeToggle — always visible */}
        <div
          style={{
            padding: '0.75rem 1rem',
            borderTop: '1px solid var(--t-border)',
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <ThemeToggle style={collapsed ? undefined : { width: '100%', justifyContent: 'center' }} />
        </div>
      </aside>

      {/* ── Main content ── */}
      <main
        style={{
          marginLeft: sidebarWidth,
          flex: 1,
          minHeight: '100vh',
          background: 'var(--t-bg)',
          transition: 'margin-left 0.22s ease',
        }}
      >
        {children}
      </main>
    </div>
  )
}
