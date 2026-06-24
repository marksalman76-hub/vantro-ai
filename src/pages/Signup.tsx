import { useState } from 'react'
import { useLocation, Link } from 'wouter'
import { api } from '../lib/api'

const LOGO_URL =
  'https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/uLNNHswnlaLuEQJY.png'

export function SignupPage() {
  const [, setLocation] = useLocation()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [nameFocused, setNameFocused] = useState(false)
  const [emailFocused, setEmailFocused] = useState(false)
  const [passFocused, setPassFocused] = useState(false)

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const result = await api.register(name, email, password)
      const token = (result.access_token || result.token) as string | undefined
      if (token) {
        localStorage.setItem('token', token)
        setLocation('/onboarding')
      } else {
        setError((result.detail as string) || 'Registration failed. Please try again.')
      }
    } catch {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const inputStyle = (focused: boolean): React.CSSProperties => ({
    width: '100%',
    background: 'oklch(1 0 0 / 0.06)',
    border: `1px solid ${focused ? 'oklch(0.72 0.15 250)' : 'oklch(1 0 0 / 0.12)'}`,
    borderRadius: '0.625rem',
    padding: '0.75rem 1rem',
    color: 'oklch(0.97 0 0)',
    fontFamily: 'Inter, sans-serif',
    fontSize: '0.9rem',
    outline: 'none',
    transition: 'border-color 0.2s ease',
    boxSizing: 'border-box',
  })

  return (
    <div
      style={{
        minHeight: '100dvh',
        background: 'oklch(0.14 0 0)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1rem',
        fontFamily: 'Inter, sans-serif',
      }}
    >
      {/* Logo above card */}
      <Link href="/">
        <a
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            textDecoration: 'none',
            marginBottom: '1.75rem',
          }}
        >
          <img src={LOGO_URL} alt="Vantro logo" style={{ height: 28, width: 'auto' }} />
          <span
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: 700,
              fontSize: '1.05rem',
              color: 'oklch(0.97 0 0)',
              letterSpacing: '-0.01em',
            }}
          >
            VANTRO
          </span>
          <span
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: 400,
              fontSize: '1.05rem',
              color: 'oklch(0.55 0 0)',
            }}
          >
            .ai
          </span>
        </a>
      </Link>

      {/* Card */}
      <div
        style={{
          width: '100%',
          maxWidth: 400,
          background: 'oklch(1 0 0 / 0.04)',
          border: '1px solid oklch(1 0 0 / 0.10)',
          borderRadius: '1.25rem',
          padding: '2.5rem',
          boxSizing: 'border-box',
        }}
      >
        {/* Heading */}
        <h1
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
            fontSize: '1.75rem',
            color: 'oklch(0.97 0 0)',
            margin: '0 0 0.5rem',
            letterSpacing: '-0.02em',
          }}
        >
          Create your account
        </h1>
        <p
          style={{
            color: 'oklch(0.55 0 0)',
            fontSize: '0.9rem',
            margin: '0 0 1.75rem',
            lineHeight: 1.5,
          }}
        >
          Start free — no credit card required
        </p>

        {/* Error */}
        {error && (
          <div
            style={{
              color: 'oklch(0.65 0.18 25)',
              fontSize: '0.85rem',
              marginBottom: '1rem',
              padding: '0.625rem 0.875rem',
              background: 'oklch(0.65 0.18 25 / 0.08)',
              border: '1px solid oklch(0.65 0.18 25 / 0.20)',
              borderRadius: '0.5rem',
              lineHeight: 1.4,
            }}
          >
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSignup} noValidate>
          <div style={{ marginBottom: '1rem' }}>
            <label
              htmlFor="signup-name"
              style={{
                display: 'block',
                fontSize: '0.8125rem',
                color: 'oklch(0.70 0 0)',
                marginBottom: '0.375rem',
                fontWeight: 500,
              }}
            >
              Full name
            </label>
            <input
              id="signup-name"
              type="text"
              autoComplete="name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              onFocus={() => setNameFocused(true)}
              onBlur={() => setNameFocused(false)}
              placeholder="Jane Smith"
              style={inputStyle(nameFocused)}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label
              htmlFor="signup-email"
              style={{
                display: 'block',
                fontSize: '0.8125rem',
                color: 'oklch(0.70 0 0)',
                marginBottom: '0.375rem',
                fontWeight: 500,
              }}
            >
              Email
            </label>
            <input
              id="signup-email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setEmailFocused(true)}
              onBlur={() => setEmailFocused(false)}
              placeholder="you@company.com"
              style={inputStyle(emailFocused)}
            />
          </div>

          <div style={{ marginBottom: '1.75rem' }}>
            <label
              htmlFor="signup-password"
              style={{
                display: 'block',
                fontSize: '0.8125rem',
                color: 'oklch(0.70 0 0)',
                marginBottom: '0.375rem',
                fontWeight: 500,
              }}
            >
              Password
            </label>
            <input
              id="signup-password"
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={() => setPassFocused(true)}
              onBlur={() => setPassFocused(false)}
              placeholder="Min. 8 characters"
              style={inputStyle(passFocused)}
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              background: loading
                ? 'oklch(0.55 0.10 250)'
                : 'linear-gradient(160deg, oklch(0.78 0.13 250) 0%, oklch(0.60 0.18 250) 100%)',
              color: 'oklch(0.98 0 0)',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontFamily: 'Inter, sans-serif',
              fontSize: '0.9375rem',
              fontWeight: 600,
              padding: '0.75rem 1.25rem',
              borderRadius: '9999px',
              boxShadow: loading
                ? 'none'
                : 'inset 0 1px 0 rgba(255,255,255,0.25), 0 4px 16px oklch(0.60 0.18 250 / 0.45)',
              transition: 'box-shadow 0.2s ease, transform 0.15s ease',
              opacity: loading ? 0.7 : 1,
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                const el = e.currentTarget as HTMLButtonElement
                el.style.boxShadow =
                  'inset 0 1px 0 rgba(255,255,255,0.40), 0 8px 28px oklch(0.60 0.18 250 / 0.65)'
                el.style.transform = 'scale(1.01)'
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                const el = e.currentTarget as HTMLButtonElement
                el.style.boxShadow =
                  'inset 0 1px 0 rgba(255,255,255,0.25), 0 4px 16px oklch(0.60 0.18 250 / 0.45)'
                el.style.transform = 'scale(1)'
              }
            }}
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        {/* Footer link */}
        <p
          style={{
            textAlign: 'center',
            fontSize: '0.85rem',
            color: 'oklch(0.55 0 0)',
            marginTop: '1.5rem',
            marginBottom: 0,
          }}
        >
          Already have an account?{' '}
          <Link href="/login">
            <a
              style={{
                color: 'oklch(0.72 0.15 250)',
                textDecoration: 'none',
                fontWeight: 500,
                transition: 'color 0.2s ease',
              }}
              onMouseEnter={(e) =>
                ((e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.82 0.13 250)')
              }
              onMouseLeave={(e) =>
                ((e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.72 0.15 250)')
              }
            >
              Sign in
            </a>
          </Link>
        </p>
      </div>
    </div>
  )
}
