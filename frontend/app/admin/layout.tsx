import Link from 'next/link'
import type { Metadata } from 'next'
import ThemeToggle from '@/components/ThemeToggle'

export const metadata: Metadata = { title: 'Admin | Vantro' }

const NAV = [
  { label: 'Overview', href: '/admin' },
  { label: 'Run Agents', href: '/admin/agents' },
  { label: 'Creative Studio', href: '/admin/creative' },
  { label: 'Jobs', href: '/admin/jobs' },
  { label: 'Library', href: '/admin/library' },
  { label: 'Secrets', href: '/admin/secrets' },
]

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--t-bg)' }}>
      <aside style={{
        width: 220,
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
      }}>
        <div style={{ padding: '0 1.25rem 1.5rem', borderBottom: '1px solid var(--t-border)' }}>
          <div style={{ fontSize: 10, color: '#1FFFD6', letterSpacing: '0.2em', textTransform: 'uppercase' }}>Vantro</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--t-text-1)', marginTop: 2 }}>Admin Portal</div>
        </div>
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
              }}
            >
              {n.label}
            </Link>
          ))}
        </nav>
        <div style={{ padding: '0.75rem 1rem', borderTop: '1px solid var(--t-border)' }}>
          <ThemeToggle style={{ width: '100%', justifyContent: 'center' }} />
        </div>
      </aside>
      <main style={{ marginLeft: 220, flex: 1, minHeight: '100vh', background: 'var(--t-bg)' }}>
        {children}
      </main>
    </div>
  )
}
