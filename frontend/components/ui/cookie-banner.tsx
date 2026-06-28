'use client'

import { useState, useEffect } from 'react'

export function CookieBanner() {
  const [visible, setVisible] = useState(false)
  const [showManage, setShowManage] = useState(false)
  const [analytics, setAnalytics] = useState(true)
  const [marketing, setMarketing] = useState(false)

  useEffect(() => {
    if (!localStorage.getItem('cookie_consent')) setVisible(true)
  }, [])

  const accept = () => {
    localStorage.setItem('cookie_consent', JSON.stringify({ necessary: true, analytics: true, marketing: true, ts: Date.now() }))
    setVisible(false)
  }
  const reject = () => {
    localStorage.setItem('cookie_consent', JSON.stringify({ necessary: true, analytics: false, marketing: false, ts: Date.now() }))
    setVisible(false)
  }
  const savePreferences = () => {
    localStorage.setItem('cookie_consent', JSON.stringify({ necessary: true, analytics, marketing, ts: Date.now() }))
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div style={{
      position: 'fixed', bottom: '1.5rem', left: '50%', transform: 'translateX(-50%)',
      zIndex: 9999, width: 'min(640px, calc(100vw - 2rem))',
      background: 'oklch(0.16 0 0)', border: '1px solid oklch(1 0 0 / 0.12)',
      borderRadius: '1rem', padding: '1.25rem 1.5rem',
      boxShadow: '0 8px 40px rgba(0,0,0,0.6)', fontFamily: "'Inter', sans-serif",
    }}>
      {!showManage ? (
        <>
          <p style={{ color: 'oklch(0.85 0 0)', fontSize: '0.875rem', marginBottom: '1rem', lineHeight: 1.5, margin: '0 0 1rem' }}>
            We use cookies to improve your experience and analyse site usage. By clicking &ldquo;Accept all&rdquo; you agree to our{' '}
            <a href="#" style={{ color: 'oklch(0.72 0.15 250)', textDecoration: 'underline' }}>cookie policy</a>.
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <button onClick={accept} style={{
              background: 'linear-gradient(160deg, oklch(0.78 0.13 250) 0%, oklch(0.60 0.18 250) 100%)',
              color: 'oklch(0.98 0 0)', border: 'none', borderRadius: '9999px',
              padding: '0.5rem 1.25rem', fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer',
            }}>Accept all</button>
            <button onClick={reject} style={{
              background: 'oklch(1 0 0 / 0.06)', color: 'oklch(0.75 0 0)',
              border: '1px solid oklch(1 0 0 / 0.12)', borderRadius: '9999px',
              padding: '0.5rem 1.25rem', fontSize: '0.875rem', cursor: 'pointer',
            }}>Reject non-essential</button>
            <button onClick={() => setShowManage(true)} style={{
              background: 'none', color: 'oklch(0.55 0 0)', border: 'none',
              fontSize: '0.8rem', cursor: 'pointer', textDecoration: 'underline',
            }}>Manage preferences</button>
          </div>
        </>
      ) : (
        <>
          <p style={{ color: 'oklch(0.85 0 0)', fontSize: '0.875rem', fontWeight: 600, margin: '0 0 0.75rem' }}>Cookie preferences</p>
          {[
            { label: 'Necessary', desc: 'Required for the site to work.', key: 'necessary' as const, locked: true },
            { label: 'Analytics', desc: 'Helps us understand usage.', key: 'analytics' as const, locked: false },
            { label: 'Marketing', desc: 'Personalised ads and content.', key: 'marketing' as const, locked: false },
          ].map(({ label, desc, key, locked }) => {
            const checked = key === 'necessary' ? true : key === 'analytics' ? analytics : marketing
            const toggle = () => key === 'analytics' ? setAnalytics(v => !v) : setMarketing(v => !v)
            return (
              <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0', borderTop: '1px solid oklch(1 0 0 / 0.07)' }}>
                <div>
                  <p style={{ color: 'oklch(0.90 0 0)', fontSize: '0.85rem', fontWeight: 500, margin: 0 }}>{label}</p>
                  <p style={{ color: 'oklch(0.50 0 0)', fontSize: '0.75rem', margin: 0 }}>{desc}</p>
                </div>
                <button onClick={locked ? undefined : toggle} style={{
                  width: 40, height: 22, borderRadius: 11, border: 'none', cursor: locked ? 'not-allowed' : 'pointer',
                  background: checked ? 'oklch(0.60 0.18 250)' : 'oklch(1 0 0 / 0.10)',
                  position: 'relative', transition: 'background 0.2s', flexShrink: 0,
                }}>
                  <span style={{
                    position: 'absolute', top: 3, left: checked ? 21 : 3, width: 16, height: 16,
                    borderRadius: '50%', background: 'oklch(0.97 0 0)', transition: 'left 0.2s',
                  }} />
                </button>
              </div>
            )
          })}
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
            <button onClick={savePreferences} style={{
              background: 'linear-gradient(160deg, oklch(0.78 0.13 250) 0%, oklch(0.60 0.18 250) 100%)',
              color: 'oklch(0.98 0 0)', border: 'none', borderRadius: '9999px',
              padding: '0.5rem 1.25rem', fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer',
            }}>Save preferences</button>
            <button onClick={() => setShowManage(false)} style={{
              background: 'none', color: 'oklch(0.55 0 0)', border: 'none', fontSize: '0.8rem', cursor: 'pointer',
            }}>Back</button>
          </div>
        </>
      )}
    </div>
  )
}
