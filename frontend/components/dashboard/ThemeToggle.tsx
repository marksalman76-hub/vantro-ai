'use client';

import React from 'react';
import { useTheme } from '../../lib/hooks/useTheme';

type Theme = 'dark' | 'light' | 'auto';

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  const getThemeIcon = (): string => {
    switch (theme) {
      case 'dark':
        return '☀️';
      case 'light':
        return '🌙';
      case 'auto':
        return '🔄';
      default:
        return '☀️';
    }
  };

  const cycleTheme = () => {
    const themes: Theme[] = ['dark', 'light', 'auto'];
    const currentIndex = themes.indexOf(theme as Theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
  };

  return (
    <button
      onClick={cycleTheme}
      title={`Theme: ${theme}`}
      style={{
        position: 'fixed',
        bottom: '2rem',
        left: '2rem',
        zIndex: 50,
        background: 'oklch(1 0 0 / 0.08)',
        border: '1px solid oklch(1 0 0 / 0.16)',
        color: 'oklch(0.5 0 0)',
        padding: '0.5rem 0.75rem',
        borderRadius: '0.375rem',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        fontSize: '1rem',
        fontWeight: 500,
        transition: 'all 0.2s ease-in-out',
      }}
      onMouseEnter={(e) => {
        const target = e.currentTarget as HTMLButtonElement;
        target.style.filter = 'brightness(1.2)';
      }}
      onMouseLeave={(e) => {
        const target = e.currentTarget as HTMLButtonElement;
        target.style.filter = 'brightness(1)';
      }}
    >
      {getThemeIcon()}
    </button>
  );
}
