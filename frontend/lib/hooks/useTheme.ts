'use client';

import { useState, useEffect } from 'react';

type Theme = 'dark' | 'light' | 'auto';

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>('dark');
  const [mounted, setMounted] = useState(false);

  // Restore theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme-preference') as Theme | null;
    if (savedTheme) {
      setThemeState(savedTheme);
      applyTheme(savedTheme);
    } else {
      applyTheme('dark');
    }
    setMounted(true);
  }, []);

  const applyTheme = (newTheme: Theme) => {
    // Remove old classes
    document.documentElement.classList.remove('dark', 'light', 'auto');

    if (newTheme === 'auto') {
      // Detect OS preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const effectiveTheme = prefersDark ? 'dark' : 'light';
      document.documentElement.classList.add(effectiveTheme);
    } else {
      document.documentElement.classList.add(newTheme);
    }
  };

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('theme-preference', newTheme);
    applyTheme(newTheme);
  };

  return { theme, setTheme };
}
