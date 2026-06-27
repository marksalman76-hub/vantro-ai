'use client'

import { useEffect, useState } from 'react'

export default function ThemeToggle({ style }: { style?: React.CSSProperties }) {
  const [dark, setDark] = useState(true)

  useEffect(() => {
    const saved = localStorage.getItem('vantro_theme')
    const isDark = saved !== 'light'
    setDark(isDark)
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
  }, [])

  function toggle() {
    const next = !dark
    setDark(next)
    const theme = next ? 'dark' : 'light'
    localStorage.setItem('vantro_theme', theme)
    document.documentElement.setAttribute('data-theme', theme)
    window.dispatchEvent(new CustomEvent('vantro-theme', { detail: { dark: next } }))
  }

  return (
    <button
      onClick={toggle}
      aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        background: dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)',
        border: `1px solid ${dark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)'}`,
        borderRadius: 20,
        padding: '5px 12px',
        cursor: 'pointer',
        fontSize: 12,
        fontWeight: 600,
        color: dark ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.6)',
        letterSpacing: '0.04em',
        transition: 'background 0.2s, border-color 0.2s',
        fontFamily: "'Space Grotesk', sans-serif",
        ...style,
      }}
    >
      <span style={{ fontSize: 14, lineHeight: 1 }}>{dark ? '☀' : '☾'}</span>
      {dark ? 'Light' : 'Dark'}
    </button>
  )
}
