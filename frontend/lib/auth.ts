'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export function useAuth() {
  const [user, setUser] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    if (storedToken) {
      setToken(storedToken)
      verifyToken(storedToken)
    } else {
      setLoading(false)
    }
  }, [])

  const verifyToken = async (t: string) => {
    try {
      const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${t}` } })
      if (res.ok) {
        const data = await res.json()
        setUser(data)
      } else {
        localStorage.removeItem('token')
        router.push('/login')
      }
    } catch {
      localStorage.removeItem('token')
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }

  return { user, loading, token, isAuthenticated: !!token }
}
