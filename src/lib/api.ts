const API = (import.meta as unknown as { env: { VITE_API_URL?: string } }).env.VITE_API_URL ?? 'https://api.vantro.ai'

export const getToken = (): string | null => localStorage.getItem('token')

async function post(path: string, body: unknown, auth = false): Promise<Record<string, unknown>> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth) {
    const t = getToken()
    if (t) headers.Authorization = `Bearer ${t}`
  }
  const res = await fetch(`${API}${path}`, { method: 'POST', headers, body: JSON.stringify(body) })
  return res.json()
}

async function get(path: string): Promise<Record<string, unknown>> {
  const t = getToken()
  const headers: Record<string, string> = t ? { Authorization: `Bearer ${t}` } : {}
  const res = await fetch(`${API}${path}`, { headers })
  return res.json()
}

export const api = {
  register: (name: string, email: string, password: string) =>
    post('/api/auth/register', { name, email, password }),
  login: (email: string, password: string) =>
    post('/api/auth/login', { email, password }),
  get,
  post: (path: string, body: unknown) => post(path, body, true),
}

export function signOut() {
  localStorage.removeItem('token')
  localStorage.removeItem('onboarding_complete')
  window.location.href = '/login'
}
