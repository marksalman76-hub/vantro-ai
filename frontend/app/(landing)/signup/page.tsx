'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import GlassCard from '@/components/ui/glass-card'
import GlassButton from '@/components/ui/glass-button'
import Background3D from '@/components/ui/3d-background'
import { apiClient } from '@/lib/api-client'
import Link from 'next/link'

export default function SignupPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const result = await apiClient.register(email, password, name)
      const token = result.access_token || result.token
      if (token) {
        localStorage.setItem('token', token)
        router.push('/dashboard')
      } else {
        setError(result.detail || 'Signup failed. Please try again.')
      }
    } catch {
      setError('Signup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <Background3D />
      <GlassCard hover={false} className="w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center text-white">Create Account</h1>

        <form onSubmit={handleSignup} className="space-y-4">
          <div>
            <label className="block text-sm mb-2" style={{ color: 'rgb(203, 213, 225)' }}>Name</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full glass rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              placeholder="Your name"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-2" style={{ color: 'rgb(203, 213, 225)' }}>Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full glass rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-2" style={{ color: 'rgb(203, 213, 225)' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full glass rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              placeholder="••••••••"
              required
              minLength={8}
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <GlassButton type="submit" variant="solid" size="lg" className="w-full justify-center" disabled={loading}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </GlassButton>
        </form>

        <p className="text-center mt-6 text-sm" style={{ color: 'rgb(203, 213, 225)' }}>
          Already have an account?{' '}
          <Link href="/login" className="text-blue-400 hover:text-blue-300">Login</Link>
        </p>
      </GlassCard>
    </div>
  )
}
