const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

export const apiClient = {
  async register(email: string, password: string, name: string) {
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name }),
    })
    return res.json()
  },

  async login(email: string, password: string) {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    return res.json()
  },

  async getMe(token: string) {
    const res = await fetch(`${API_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    })
    return res.json()
  },

  async getDashboard(token: string) {
    const res = await fetch(`${API_URL}/api/dashboard`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    return res.json()
  },

  logout() {
    if (typeof window !== 'undefined') localStorage.removeItem('token')
  },
}
