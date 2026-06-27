'use client'

import { useState, useEffect, useCallback } from 'react'

type KeyHealth = {
  name: string
  lastRotated: string | null
  ageDays: number | null
  status: 'ok' | 'warn' | 'stale' | 'unknown'
}

const PROVIDER_LINKS: Record<string, string | null> = {
  ANTHROPIC_API_KEY: 'https://console.anthropic.com/settings/keys',
  RUNWAY_API_KEY: 'https://app.runwayml.com/settings',
  ELEVENLABS_API_KEY: 'https://elevenlabs.io/app/profile/api-key',
  RESEND_API_KEY: 'https://resend.com/api-keys',
  STRIPE_SECRET_KEY: 'https://dashboard.stripe.com/apikeys',
  OTP_SECRET: null,
}

function daysAgo(iso: string | null): string {
  if (!iso) return 'Never recorded'
  const diff = Date.now() - new Date(iso).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return 'Today'
  if (days === 1) return '1 day ago'
  return `${days} days ago`
}

function statusBadge(status: KeyHealth['status'], ageDays: number | null) {
  const map: Record<string, { label: string; bg: string; color: string }> = {
    ok: { label: 'Rotated', bg: 'rgba(31,255,214,0.15)', color: '#1FFFD6' },
    warn: { label: 'Due Soon', bg: 'rgba(255,165,0,0.15)', color: '#ffa500' },
    stale: { label: 'Overdue', bg: 'rgba(255,107,107,0.15)', color: '#ff6b6b' },
    unknown: { label: 'Unknown', bg: 'rgba(85,85,85,0.3)', color: '#888' },
  }
  const s = map[status] ?? map.unknown
  return (
    <span style={{
      display: 'inline-block',
      padding: '2px 10px',
      borderRadius: 99,
      background: s.bg,
      color: s.color,
      fontSize: 11,
      fontWeight: 700,
      letterSpacing: '0.05em',
      textTransform: 'uppercase',
    }}>
      {s.label}{ageDays != null ? ` (${ageDays}d)` : ''}
    </span>
  )
}

function SkeletonRow() {
  return (
    <tr>
      {[180, 100, 140, 200].map((w, i) => (
        <td key={i} style={{ padding: '1rem 1.25rem' }}>
          <div style={{
            height: 14,
            width: w,
            borderRadius: 4,
            background: 'rgba(255,255,255,0.06)',
            animation: 'pulse 1.4s ease-in-out infinite',
          }} />
        </td>
      ))}
    </tr>
  )
}

export default function SecretsPage() {
  const [keys, setKeys] = useState<KeyHealth[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [markingRotated, setMarkingRotated] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<string | null>(null)
  const [newValues, setNewValues] = useState<Record<string, string>>({})
  const [pushing, setPushing] = useState<string | null>(null)
  const [pushResult, setPushResult] = useState<Record<string, { ok: boolean; msg: string }>>({})
  const [autoRotating, setAutoRotating] = useState(false)
  const [autoRotateMsg, setAutoRotateMsg] = useState<{ ok: boolean; msg: string } | null>(null)

  const fetchKeys = useCallback(async () => {
    try {
      setError(null)
      const res = await fetch('/api/admin/secrets')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setKeys(data)
    } catch (e: any) {
      setError(e.message ?? 'Failed to load secrets')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchKeys() }, [fetchKeys])

  async function markRotated(keyName: string) {
    setMarkingRotated(keyName)
    try {
      const res = await fetch('/api/admin/secrets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'mark_rotated', keyName }),
      })
      if (!res.ok) throw new Error()
      const now = new Date().toISOString()
      setKeys(prev => prev.map(k =>
        k.name === keyName
          ? { ...k, status: 'ok', lastRotated: now, ageDays: 0 }
          : k
      ))
    } catch {
      // silent — row stays unchanged
    } finally {
      setMarkingRotated(null)
    }
  }

  async function autoRotateAnthropic() {
    setAutoRotating(true)
    setAutoRotateMsg(null)
    try {
      const res = await fetch('/api/admin/secrets/rotate-anthropic', { method: 'POST' })
      if (res.status === 503) {
        setAutoRotateMsg({ ok: false, msg: 'Requires ANTHROPIC_ADMIN_KEY env var' })
      } else if (res.status === 500) {
        setAutoRotateMsg({ ok: false, msg: 'Rotation failed' })
      } else if (!res.ok) {
        setAutoRotateMsg({ ok: false, msg: 'Rotation failed' })
      } else {
        setAutoRotateMsg({ ok: true, msg: 'Rotated — new key active in ~30s' })
        await fetchKeys()
      }
    } catch {
      setAutoRotateMsg({ ok: false, msg: 'Rotation failed' })
    } finally {
      setAutoRotating(false)
    }
  }

  async function pushToVercel(keyName: string) {
    const newValue = newValues[keyName] ?? ''
    if (!newValue.trim()) return
    setPushing(keyName)
    setPushResult(prev => ({ ...prev, [keyName]: undefined as any }))
    try {
      const res = await fetch('/api/admin/secrets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'update', keyName, newValue }),
      })
      if (res.status === 503) {
        setPushResult(prev => ({
          ...prev,
          [keyName]: { ok: false, msg: 'Configure VERCEL_TOKEN + VERCEL_PROJECT_ID in Vercel env vars first' },
        }))
        return
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setPushResult(prev => ({ ...prev, [keyName]: { ok: true, msg: '✓ Updated in Vercel' } }))
      setExpanded(null)
      setNewValues(prev => { const c = { ...prev }; delete c[keyName]; return c })
      await fetchKeys()
    } catch (e: any) {
      setPushResult(prev => ({
        ...prev,
        [keyName]: { ok: false, msg: e.message ?? 'Update failed' },
      }))
    } finally {
      setPushing(null)
    }
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif', color: '#fff', minHeight: '100vh', background: '#0A0D14' }}>
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.4; }
          50% { opacity: 0.9; }
        }
        .secret-row:hover { background: rgba(255,255,255,0.025) !important; }
        .btn-ghost:hover { background: rgba(255,255,255,0.08) !important; }
        .btn-teal:hover { opacity: 0.85; }
      `}</style>

      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, color: '#fff' }}>Secrets Manager</h1>
        <p style={{ margin: '0.35rem 0 0', color: '#666', fontSize: 13 }}>Manage API key rotation</p>
      </div>

      {error && (
        <div style={{
          background: 'rgba(255,107,107,0.1)',
          border: '1px solid rgba(255,107,107,0.3)',
          borderRadius: 8,
          padding: '0.75rem 1rem',
          color: '#ff6b6b',
          fontSize: 13,
          marginBottom: '1.5rem',
        }}>
          {error}
        </div>
      )}

      <div style={{ background: '#12151E', borderRadius: 12, border: '1px solid rgba(255,255,255,0.06)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              {['Key', 'Status', 'Last Rotated', 'Actions'].map(h => (
                <th key={h} style={{
                  padding: '0.75rem 1.25rem',
                  textAlign: 'left',
                  fontSize: 11,
                  fontWeight: 600,
                  color: '#555',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading
              ? Array.from({ length: 6 }).map((_, i) => <SkeletonRow key={i} />)
              : keys.map(k => {
                  const link = PROVIDER_LINKS[k.name]
                  const isExpanded = expanded === k.name
                  const result = pushResult[k.name]
                  return (
                    <>
                      <tr
                        key={k.name}
                        className="secret-row"
                        style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', background: 'transparent', transition: 'background 0.15s' }}
                      >
                        <td style={{ padding: '1rem 1.25rem' }}>
                          <span style={{ fontFamily: 'monospace', fontSize: 13, color: '#1FFFD6' }}>{k.name}</span>
                        </td>
                        <td style={{ padding: '1rem 1.25rem' }}>
                          {statusBadge(k.status, k.ageDays)}
                        </td>
                        <td style={{ padding: '1rem 1.25rem', fontSize: 13, color: '#888' }}>
                          {daysAgo(k.lastRotated)}
                        </td>
                        <td style={{ padding: '1rem 1.25rem' }}>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                            <button
                              className="btn-ghost"
                              disabled={markingRotated === k.name}
                              onClick={() => markRotated(k.name)}
                              style={{
                                padding: '4px 12px',
                                borderRadius: 6,
                                border: '1px solid rgba(255,255,255,0.12)',
                                background: 'transparent',
                                color: '#ccc',
                                fontSize: 12,
                                cursor: 'pointer',
                                transition: 'background 0.15s',
                                opacity: markingRotated === k.name ? 0.5 : 1,
                              }}
                            >
                              {markingRotated === k.name ? '...' : 'Mark Rotated'}
                            </button>
                            <button
                              className="btn-ghost"
                              onClick={() => {
                                setExpanded(isExpanded ? null : k.name)
                                setPushResult(prev => { const c = { ...prev }; delete c[k.name]; return c })
                              }}
                              style={{
                                padding: '4px 12px',
                                borderRadius: 6,
                                border: '1px solid rgba(255,255,255,0.12)',
                                background: 'transparent',
                                color: '#ccc',
                                fontSize: 12,
                                cursor: 'pointer',
                                transition: 'background 0.15s',
                              }}
                            >
                              Update Key
                            </button>
                            {k.name === 'ANTHROPIC_API_KEY' && (
                              <button
                                className="btn-ghost"
                                disabled={autoRotating}
                                onClick={() => autoRotateAnthropic()}
                                style={{
                                  padding: '4px 12px',
                                  borderRadius: 6,
                                  border: '1px solid rgba(255,165,0,0.3)',
                                  background: 'transparent',
                                  color: '#ffa500',
                                  fontSize: 12,
                                  cursor: 'pointer',
                                  transition: 'background 0.15s',
                                  opacity: autoRotating ? 0.5 : 1,
                                }}
                              >
                                {autoRotating ? 'Rotating...' : 'Auto-rotate'}
                              </button>
                            )}
                            {link && (
                              <a
                                href={link}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                  padding: '4px 10px',
                                  borderRadius: 6,
                                  border: '1px solid rgba(31,255,214,0.2)',
                                  color: '#1FFFD6',
                                  fontSize: 11,
                                  textDecoration: 'none',
                                  opacity: 0.8,
                                }}
                              >
                                ↗ Dashboard
                              </a>
                            )}
                          </div>
                          {k.name === 'ANTHROPIC_API_KEY' && autoRotateMsg && (
                            <div style={{ marginTop: 6, fontSize: 12, color: autoRotateMsg.ok ? '#1FFFD6' : '#ff6b6b' }}>
                              {autoRotateMsg.msg}
                            </div>
                          )}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr key={`${k.name}-expand`} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', background: 'rgba(31,255,214,0.02)' }}>
                          <td colSpan={4} style={{ padding: '0.75rem 1.25rem 1rem' }}>
                            <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                              <input
                                type="password"
                                placeholder={`New value for ${k.name}`}
                                value={newValues[k.name] ?? ''}
                                onChange={e => setNewValues(prev => ({ ...prev, [k.name]: e.target.value }))}
                                style={{
                                  flex: '1 1 260px',
                                  padding: '6px 10px',
                                  borderRadius: 6,
                                  border: '1px solid rgba(255,255,255,0.12)',
                                  background: '#0A0D14',
                                  color: '#fff',
                                  fontSize: 13,
                                  fontFamily: 'monospace',
                                  outline: 'none',
                                }}
                              />
                              <button
                                className="btn-teal"
                                disabled={pushing === k.name || !(newValues[k.name] ?? '').trim()}
                                onClick={() => pushToVercel(k.name)}
                                style={{
                                  padding: '6px 16px',
                                  borderRadius: 6,
                                  border: 'none',
                                  background: '#1FFFD6',
                                  color: '#0A0D14',
                                  fontSize: 12,
                                  fontWeight: 700,
                                  cursor: 'pointer',
                                  transition: 'opacity 0.15s',
                                  opacity: pushing === k.name || !(newValues[k.name] ?? '').trim() ? 0.5 : 1,
                                }}
                              >
                                {pushing === k.name ? 'Pushing...' : 'Push to Vercel'}
                              </button>
                            </div>
                            {result && (
                              <div style={{
                                marginTop: 8,
                                fontSize: 12,
                                color: result.ok ? '#1FFFD6' : '#ff6b6b',
                              }}>
                                {result.msg}
                              </div>
                            )}
                          </td>
                        </tr>
                      )}
                    </>
                  )
                })
            }
          </tbody>
        </table>
      </div>
    </div>
  )
}
