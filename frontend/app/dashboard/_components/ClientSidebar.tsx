'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { useEffect, useState } from 'react'

const NAV = [
  { label: 'Overview',      href: '/dashboard',              icon: '▦' },
  { label: 'Agents',        href: '/dashboard/agents',       icon: '◈' },
  { label: 'Conversations', href: '/dashboard/conversations', icon: '◎' },
  { label: 'Analytics',     href: '/dashboard/analytics',    icon: '◌' },
  { label: 'Settings',      href: '/dashboard/settings',     icon: '◉' },
]

export default function ClientSidebar() {
  const pathname = usePathname()
  const [workspace, setWorkspace] = useState('Workspace')

  useEffect(() => {
    const w = localStorage.getItem('workspace_name')
    if (w) setWorkspace(w)
  }, [])

  return (
    <aside style={{
      width: 220,
      minWidth: 220,
      background: 'rgba(0,0,0,0.35)',
      borderRight: '1px solid rgba(255,255,255,0.06)',
      display: 'flex',
      flexDirection: 'column',
      padding: '20px 12px',
      gap: 4,
      flexShrink: 0,
    }}>
      <Link href="https://vantro.ai" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 8, padding: '4px 8px', marginBottom: 20 }}>
        <div style={{ width: 28, height: 28, borderRadius: 8, background: 'linear-gradient(135deg,#FF6B35,#00D9FF)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: 12, color: '#fff' }}>V</div>
        <span style={{ fontWeight: 700, fontSize: 14, color: '#fff', letterSpacing: '-0.01em' }}>Vantro<span style={{ color: '#FF6B35' }}>.ai</span></span>
      </Link>

      <div style={{ padding: '8px 10px', borderRadius: 8, background: 'rgba(255,107,53,0.08)', border: '1px solid rgba(255,107,53,0.15)', marginBottom: 8 }}>
        <p style={{ fontSize: 10, color: 'rgba(255,255,255,0.35)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 2 }}>Workspace</p>
        <p style={{ fontSize: 12, color: '#fff', fontWeight: 600 }}>{workspace}</p>
      </div>

      {NAV.map(item => {
        const active = pathname === item.href || (item.href !== '/dashboard' && pathname?.startsWith(item.href))
        return (
          <Link key={item.href} href={item.href} style={{ textDecoration: 'none' }}>
            <div
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '9px 10px', borderRadius: 8,
                background: active ? 'rgba(255,107,53,0.12)' : 'transparent',
                color: active ? '#FF6B35' : 'rgba(255,255,255,0.45)',
                fontSize: 13, fontWeight: active ? 600 : 400,
                transition: 'all 0.15s',
                cursor: 'pointer',
              }}
              onMouseEnter={e => { if (!active) (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.05)' }}
              onMouseLeave={e => { if (!active) (e.currentTarget as HTMLElement).style.background = 'transparent' }}
            >
              <span style={{ fontSize: 14, opacity: active ? 1 : 0.6 }}>{item.icon}</span>
              {item.label}
            </div>
          </Link>
        )
      })}

      <div style={{ marginTop: 'auto' }}>
        <button
          onClick={() => { localStorage.clear(); window.location.href = '/login' }}
          style={{ width: '100%', padding: '9px 10px', borderRadius: 8, background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.25)', fontSize: 13, cursor: 'pointer', textAlign: 'left', display: 'flex', alignItems: 'center', gap: 10, fontFamily: 'inherit' }}
          onMouseEnter={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.5)')}
          onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.25)')}
        >
          <span>↩</span> Sign out
        </button>
      </div>
    </aside>
  )
}
