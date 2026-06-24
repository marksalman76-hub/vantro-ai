'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import GlassCard from '@/components/ui/glass-card'
import GlassButton from '@/components/ui/glass-button'
import Background3D from '@/components/ui/3d-background'
import { apiClient } from '@/lib/api-client'
import Link from 'next/link'
import { useFormValidation } from '@/hooks/useFormValidation'

const LOGIN_RULES = {
  email: { required: true, email: true },
  password: { required: true, minLength: 8 },
}

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { errors, validate, clearError } = useFormValidation(LOGIN_RULES)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    const isValid = validate({ email, password })
    if (!isValid) return
    setLoading(true)
    setError('')
    try {
      const result = await apiClient.login(email, password)
      const token = result.access_token || result.token
      if (token) {
        localStorage.setItem('token', token)
        router.push('/dashboard')
      } else {
        setError(result.detail || 'Login failed. Please check your credentials.')
      }
    } catch {
      setError('Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const hasValidationErrors = Object.keys(errors).length > 0

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <Background3D />
      <GlassCard hover={false} className="w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center text-white">Login to Vantro</h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm mb-2" style={{ color: 'rgb(203, 213, 225)' }}>Email</label>
            <input
              type="email"
              value={email}
              onChange={e => { setEmail(e.target.value); clearError('email') }}
              className="w-full glass rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              placeholder="you@example.com"
            />
            {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
          </div>

          <div>
            <label className="block text-sm mb-2" style={{ color: 'rgb(203, 213, 225)' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => { setPassword(e.target.value); clearError('password') }}
              className="w-full glass rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              placeholder="••••••••"
            />
            {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password}</p>}
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <GlassButton
            type="submit"
            variant="solid"
            size="lg"
            className="w-full justify-center"
            disabled={loading || hasValidationErrors}
          >
            {loading ? 'Logging in...' : 'Login'}
          </GlassButton>
        </form>

        <p className="text-center mt-6 text-sm" style={{ color: 'rgb(203, 213, 225)' }}>
          Don&apos;t have an account?{' '}
          <Link href="/signup" className="text-blue-400 hover:text-blue-300">Sign up</Link>
        </p>
      </GlassCard>
    </div>
  )
}
