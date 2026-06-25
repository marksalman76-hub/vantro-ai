'use client'
export default function ClientSidebar() {
  return (
    <aside style={{ width: '240px', background: 'rgba(0,0,0,0.4)', borderRight: '1px solid rgba(255,255,255,0.06)', padding: '1.5rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <p style={{ color: 'rgba(255,255,255,0.3)', fontSize: '0.7rem', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Dashboard</p>
    </aside>
  )
}
