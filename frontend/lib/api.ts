'use client';

/**
 * Shared API fetch utility.
 * - Attaches Authorization header from localStorage token (backward compat)
 * - httpOnly cookie is sent automatically by the browser for same-origin requests
 * - On 401: clears localStorage token and redirects to /login
 */
export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) ?? {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers, credentials: 'include' });

  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.replace('/login?expired=1');
    }
    throw new Error('Session expired');
  }

  return res;
}

/** Sign out: clear localStorage, revoke httpOnly cookie via proxy, redirect. */
export async function signOut(): Promise<void> {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
  }
  try {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
  } catch {
    // Ignore network errors on logout
  }
  if (typeof window !== 'undefined') {
    window.location.replace('/login');
  }
}
