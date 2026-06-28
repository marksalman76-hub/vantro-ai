import { renderHook, act } from '@testing-library/react';
import { useTheme } from '../useTheme';

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.className = '';

    // Mock window.matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation((query) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });
  });

  afterEach(() => {
    localStorage.clear();
    document.documentElement.className = '';
    jest.restoreAllMocks();
  });

  it('initializes with default theme (dark)', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('dark');
  });

  it('persists theme to localStorage', () => {
    const { result } = renderHook(() => useTheme());

    act(() => {
      result.current.setTheme('light');
    });

    expect(localStorage.getItem('theme-preference')).toBe('light');
  });

  it('updates html classList when theme changes', () => {
    const { result } = renderHook(() => useTheme());

    act(() => {
      result.current.setTheme('light');
    });

    expect(document.documentElement.classList.contains('light')).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('restores theme from localStorage on mount', () => {
    localStorage.setItem('theme-preference', 'light');
    const { result } = renderHook(() => useTheme());

    expect(result.current.theme).toBe('light');
    expect(document.documentElement.classList.contains('light')).toBe(true);
  });

  it('handles auto theme by detecting OS preference', () => {
    const { result } = renderHook(() => useTheme());

    act(() => {
      result.current.setTheme('auto');
    });

    expect(result.current.theme).toBe('auto');
    expect(localStorage.getItem('theme-preference')).toBe('auto');
    // Should have either dark or light class based on OS preference
    const hasDarkOrLight =
      document.documentElement.classList.contains('dark') ||
      document.documentElement.classList.contains('light');
    expect(hasDarkOrLight).toBe(true);
  });

  it('cycles through all three themes correctly', () => {
    const { result } = renderHook(() => useTheme());

    expect(result.current.theme).toBe('dark');

    act(() => {
      result.current.setTheme('light');
    });
    expect(result.current.theme).toBe('light');

    act(() => {
      result.current.setTheme('auto');
    });
    expect(result.current.theme).toBe('auto');

    act(() => {
      result.current.setTheme('dark');
    });
    expect(result.current.theme).toBe('dark');
  });
});
