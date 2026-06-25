'use client';

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const STORAGE_KEY = 'vantro_cookie_consent';

export function CookieBanner() {
  const [visible, setVisible] = useState(() => {
    try { return !localStorage.getItem(STORAGE_KEY); } catch { return true; }
  });

  function accept() {
    localStorage.setItem(STORAGE_KEY, 'all');
    setVisible(false);
  }

  function essential() {
    localStorage.setItem(STORAGE_KEY, 'essential');
    setVisible(false);
  }

  if (!visible) return null;

  return (
    <div
      role="dialog"
      aria-label="Cookie consent"
      style={{
        position: 'fixed',
        bottom: 24,
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 900,
        width: 'min(640px, calc(100vw - 32px))',
        backgroundColor: 'oklch(0.18 0 0)',
        border: '1px solid rgba(255,255,255,0.10)',
        borderRadius: 16,
        boxShadow: '0 24px 80px rgba(0,0,0,0.65)',
        padding: '18px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        flexWrap: 'wrap',
      }}
    >
      <p style={{
        flex: 1,
        minWidth: 200,
        fontSize: 13,
        lineHeight: 1.55,
        color: 'oklch(0.70 0 0)',
        fontFamily: 'Inter, sans-serif',
        margin: 0,
      }}>
        We use cookies to keep you signed in and improve your experience.{' '}
        <a
          href="/cookies"
          style={{ color: 'oklch(0.85 0 0)', textDecoration: 'underline', textUnderlineOffset: 3 }}
        >
          Cookie Policy
        </a>
      </p>

      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0 }}>
        <button
          onClick={essential}
          style={{
            background: 'rgba(255,255,255,0.07)',
            border: '1px solid rgba(255,255,255,0.12)',
            borderRadius: 8,
            padding: '7px 14px',
            fontSize: 12,
            fontFamily: 'Inter, sans-serif',
            fontWeight: 500,
            color: 'oklch(0.70 0 0)',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            transition: 'border-color 0.15s, color 0.15s',
          }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.25)';
            (e.currentTarget as HTMLButtonElement).style.color = 'oklch(0.90 0 0)';
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.12)';
            (e.currentTarget as HTMLButtonElement).style.color = 'oklch(0.70 0 0)';
          }}
        >
          Essential only
        </button>

        <button
          onClick={accept}
          style={{
            background: 'linear-gradient(180deg, #ffffff 0%, #d8d8d8 100%)',
            border: 'none',
            borderRadius: 8,
            padding: '7px 14px',
            fontSize: 12,
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            color: 'oklch(0.12 0 0)',
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.55)',
            transition: 'opacity 0.15s',
          }}
          onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.opacity = '0.88'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.opacity = '1'; }}
        >
          Accept all
        </button>

        <button
          onClick={essential}
          aria-label="Dismiss"
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'oklch(0.50 0 0)',
            display: 'flex',
            padding: 4,
            transition: 'color 0.15s',
          }}
          onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = 'oklch(0.80 0 0)'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = 'oklch(0.50 0 0)'; }}
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
