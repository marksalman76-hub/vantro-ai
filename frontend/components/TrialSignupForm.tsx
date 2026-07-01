'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, ArrowRight, Loader2 } from 'lucide-react'

interface FormData {
  email: string
  company: string
  teamSize: string
  password: string
}

const TEAM_SIZES = [
  { value: 'solo',       label: 'Just me'        },
  { value: 'small',      label: '2–10 people'    },
  { value: 'medium',     label: '11–50 people'   },
  { value: 'large',      label: '51–200 people'  },
  { value: 'enterprise', label: '200+ people'    },
]

const STEP_LABELS = ['Your details', 'Set password']

const slideVariants = {
  enter: (dir: number) => ({ opacity: 0, x: dir * 28 }),
  center:               ({ opacity: 1, x: 0             }),
  exit:  (dir: number) => ({ opacity: 0, x: dir * -28   }),
}

export default function TrialSignupForm() {
  const [step,    setStep]    = useState(1)
  const [dir,     setDir]     = useState(1)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [form,    setForm]    = useState<FormData>({ email: '', company: '', teamSize: 'small', password: '' })
  const [errors,  setErrors]  = useState<Partial<FormData>>({})

  const set = (k: keyof FormData) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((prev) => ({ ...prev, [k]: e.target.value }))

  const validateStep1 = () => {
    const errs: Partial<FormData> = {}
    if (!form.email)                      errs.email   = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Enter a valid email'
    if (!form.company.trim())             errs.company = 'Company name is required'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const validateStep2 = () => {
    const errs: Partial<FormData> = {}
    if (!form.password)              errs.password = 'Password is required'
    else if (form.password.length < 8) errs.password = 'At least 8 characters required'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const goNext = () => {
    if (!validateStep1()) return
    setErrors({})
    setDir(1)
    setStep(2)
  }

  const goBack = () => {
    setErrors({})
    setDir(-1)
    setStep(1)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateStep2()) return
    setLoading(true)
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: form.email, password: form.password, name: form.company }),
      })
      const data = await res.json()
      if (!res.ok) {
        setErrors({ password: data.detail || 'Registration failed. Please try again.' })
        return
      }
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user_name', form.company)
      window.location.href = '/onboarding'
    } catch {
      setErrors({ password: 'Something went wrong. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md mx-auto glass rounded-2xl border border-white/10 p-10 text-center"
      >
        <div className="w-14 h-14 rounded-full bg-emerald-500/15 border border-emerald-400/30 flex items-center justify-center mx-auto mb-5">
          <Check className="w-7 h-7 text-emerald-400" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">You&apos;re in!</h2>
        <p className="text-white/55 text-sm leading-relaxed">
          We&apos;ve sent a confirmation email to <span className="text-violet-300 font-medium">{form.email}</span>.
          Check your inbox to activate your 14-day free trial.
        </p>
      </motion.div>
    )
  }

  return (
    <div className="w-full max-w-md mx-auto glass rounded-2xl border border-white/10 p-8">
      {/* Progress */}
      <div className="flex items-center gap-2 mb-7">
        {STEP_LABELS.map((label, i) => {
          const n = i + 1
          const active = step === n
          const done   = step > n
          return (
            <div key={label} className="flex items-center gap-2 flex-1">
              <div
                className={`w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center flex-shrink-0 transition-colors ${
                  done   ? 'bg-emerald-500 text-white' :
                  active ? 'bg-violet-600 text-white'  :
                           'bg-white/[0.08] text-white/30'
                }`}
              >
                {done ? <Check className="w-3.5 h-3.5" /> : n}
              </div>
              <span className={`text-xs font-medium transition-colors ${active ? 'text-white' : 'text-white/35'}`}>
                {label}
              </span>
              {i < STEP_LABELS.length - 1 && (
                <div className={`flex-1 h-px transition-colors ${done ? 'bg-emerald-500/40' : 'bg-white/[0.08]'}`} />
              )}
            </div>
          )
        })}
      </div>

      <AnimatePresence mode="wait" custom={dir}>
        {step === 1 ? (
          <motion.div
            key="step1"
            custom={dir}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.22, ease: 'easeOut' }}
            className="space-y-4"
          >
            <div>
              <h2 className="text-xl font-bold text-white mb-1">Start your free trial</h2>
              <p className="text-sm text-white/45">No credit card required · 14 days free</p>
            </div>

            {/* Email */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-white/70 uppercase tracking-wide">
                Work email
              </label>
              <input
                type="email"
                value={form.email}
                onChange={set('email')}
                autoComplete="email"
                placeholder="you@company.com"
                className={`w-full bg-white/[0.05] border rounded-lg px-4 py-2.5 text-sm text-white placeholder-white/25 focus:outline-none focus:ring-1 transition-all ${
                  errors.email ? 'border-red-500/60 focus:ring-red-500/30' : 'border-white/10 focus:border-violet-500/60 focus:ring-violet-500/20'
                }`}
              />
              {errors.email && <p className="text-xs text-red-400">{errors.email}</p>}
            </div>

            {/* Company */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-white/70 uppercase tracking-wide">
                Company name
              </label>
              <input
                type="text"
                value={form.company}
                onChange={set('company')}
                autoComplete="organization"
                placeholder="Acme Inc."
                className={`w-full bg-white/[0.05] border rounded-lg px-4 py-2.5 text-sm text-white placeholder-white/25 focus:outline-none focus:ring-1 transition-all ${
                  errors.company ? 'border-red-500/60 focus:ring-red-500/30' : 'border-white/10 focus:border-violet-500/60 focus:ring-violet-500/20'
                }`}
              />
              {errors.company && <p className="text-xs text-red-400">{errors.company}</p>}
            </div>

            {/* Team size */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-white/70 uppercase tracking-wide">
                Team size
              </label>
              <select
                value={form.teamSize}
                onChange={set('teamSize')}
                className="w-full bg-white/[0.05] border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/20 transition-all"
              >
                {TEAM_SIZES.map((s) => (
                  <option key={s.value} value={s.value} className="bg-dark-900">
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={goNext}
              className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-[0_4px_20px_rgba(124,58,237,0.35)] hover:shadow-[0_4px_30px_rgba(124,58,237,0.5)] transition-all"
            >
              Continue
              <ArrowRight className="w-4 h-4" />
            </button>

            <p className="text-[11px] text-white/30 text-center leading-relaxed">
              By continuing you agree to our{' '}
              <a href="/terms"   className="text-white/50 hover:text-white underline underline-offset-2">Terms</a>
              {' '}and{' '}
              <a href="/privacy" className="text-white/50 hover:text-white underline underline-offset-2">Privacy Policy</a>
            </p>
          </motion.div>
        ) : (
          <motion.form
            key="step2"
            custom={dir}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.22, ease: 'easeOut' }}
            onSubmit={handleSubmit}
            className="space-y-4"
          >
            <div>
              <h2 className="text-xl font-bold text-white mb-1">Create your password</h2>
              <p className="text-sm text-white/45">Almost done, {form.email}</p>
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-white/70 uppercase tracking-wide">
                Password
              </label>
              <input
                type="password"
                value={form.password}
                onChange={set('password')}
                autoComplete="new-password"
                placeholder="Min. 8 characters"
                className={`w-full bg-white/[0.05] border rounded-lg px-4 py-2.5 text-sm text-white placeholder-white/25 focus:outline-none focus:ring-1 transition-all ${
                  errors.password ? 'border-red-500/60 focus:ring-red-500/30' : 'border-white/10 focus:border-violet-500/60 focus:ring-violet-500/20'
                }`}
              />
              {errors.password && <p className="text-xs text-red-400">{errors.password}</p>}
            </div>

            <div className="flex gap-3 pt-1">
              <button
                type="button"
                onClick={goBack}
                className="flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold text-white/70 bg-white/[0.05] border border-white/10 hover:bg-white/[0.08] hover:text-white transition-all"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 disabled:opacity-60 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Creating…</>
                ) : (
                  'Create Account'
                )}
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  )
}
