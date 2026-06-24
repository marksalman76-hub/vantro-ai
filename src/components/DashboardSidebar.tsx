import { Link, useLocation } from 'wouter'
import { signOut } from '../lib/api'

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: '◈', exact: true },
  { href: '/dashboard/agents', label: 'Run agents', icon: '◆', exact: false },
  { href: '/dashboard/jobs', label: 'Activity', icon: '⬡', exact: false },
  { href: '/dashboard/library', label: 'Output library', icon: '▣', exact: false },
  { href: '/dashboard/brand', label: 'Brand profile', icon: '◎', exact: false },
  { href: '/dashboard/settings', label: 'Settings', icon: '◌', exact: false },
]

export function DashboardSidebar() {
  const [path] = useLocation()

  function isActive(href: string, exact: boolean) {
    if (exact) return path === href
    return path.startsWith(href)
  }

  return (
    <aside
      style={{
        width: '220px',
        minWidth: '220px',
        height: '100vh',
        position: 'sticky',
        top: 0,
        display: 'flex',
        flexDirection: 'column',
        background: 'oklch(0.12 0 0 / 0.90)',
        borderRight: '1px solid oklch(1 0 0 / 0.07)',
        backdropFilter: 'blur(20px)',
        flexShrink: 0,
      }}
    >
      {/* Logo */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '1.5rem 1.25rem 1.25rem',
          borderBottom: '1px solid oklch(1 0 0 / 0.06)',
        }}
      >
        <img
          src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/uLNNHswnlaLuEQJY.png"
          alt="Vantro logo"
          style={{ width: '24px', height: '24px', objectFit: 'contain' }}
        />
        <span style={{ fontWeight: 700, fontSize: '0.9rem', letterSpacing: '0.08em', color: 'oklch(0.97 0 0)' }}>
          VANTRO
          <span style={{ color: 'oklch(0.60 0.18 250)', fontWeight: 400 }}>.ai</span>
        </span>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '0.75rem 0.625rem', display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {NAV_ITEMS.map(({ href, label, icon, exact }) => {
          const active = isActive(href, exact)
          return (
            <Link key={href} href={href}>
              <a
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.625rem',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '0.625rem',
                  fontSize: '0.85rem',
                  fontWeight: active ? 500 : 400,
                  textDecoration: 'none',
                  transition: 'all 0.15s ease',
                  cursor: 'pointer',
                  ...(active
                    ? {
                        background: 'oklch(0.60 0.18 250 / 0.12)',
                        border: '1px solid oklch(0.60 0.18 250 / 0.20)',
                        color: 'oklch(0.78 0.13 250)',
                      }
                    : {
                        background: 'transparent',
                        border: '1px solid transparent',
                        color: 'oklch(0.50 0 0)',
                      }),
                }}
                onMouseEnter={(e) => {
                  if (!active) {
                    const el = e.currentTarget as HTMLElement
                    el.style.color = 'oklch(0.85 0 0)'
                    el.style.background = 'oklch(1 0 0 / 0.04)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    const el = e.currentTarget as HTMLElement
                    el.style.color = 'oklch(0.50 0 0)'
                    el.style.background = 'transparent'
                  }
                }}
              >
                <span style={{ fontSize: '0.9rem', lineHeight: 1 }}>{icon}</span>
                {label}
              </a>
            </Link>
          )
        })}
      </nav>

      {/* Sign out */}
      <div style={{ padding: '0.75rem 0.625rem', borderTop: '1px solid oklch(1 0 0 / 0.06)' }}>
        <button
          onClick={() => signOut()}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            gap: '0.625rem',
            padding: '0.5rem 0.75rem',
            borderRadius: '0.625rem',
            fontSize: '0.82rem',
            fontWeight: 400,
            color: 'oklch(0.42 0 0)',
            background: 'transparent',
            border: '1px solid transparent',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
            textAlign: 'left',
          }}
          onMouseEnter={(e) => {
            const el = e.currentTarget as HTMLElement
            el.style.color = 'oklch(0.65 0.18 25)'
            el.style.background = 'oklch(0.65 0.18 25 / 0.08)'
          }}
          onMouseLeave={(e) => {
            const el = e.currentTarget as HTMLElement
            el.style.color = 'oklch(0.42 0 0)'
            el.style.background = 'transparent'
          }}
        >
          <span style={{ fontSize: '0.85rem' }}>↩</span>
          Sign out
        </button>
      </div>
    </aside>
  )
}
