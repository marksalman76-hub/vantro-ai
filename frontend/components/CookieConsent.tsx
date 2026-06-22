'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Cookie, X } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface Prefs {
  essential:   true
  analytics:   boolean
  marketing:   boolean
  preferences: boolean
  timestamp:   number
}

const STORAGE_KEY   = 'vantro_cookie_consent'
const THIRTY_DAYS   = 30 * 24 * 60 * 60 * 1000

function loadPrefs(): Prefs | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const p: Prefs = JSON.parse(raw)
    if (Date.now() - p.timestamp > THIRTY_DAYS) return null
    return p
  } catch { return null }
}

function savePrefs(p: Omit<Prefs, 'essential' | 'timestamp'>) {
  const full: Prefs = { essential: true, timestamp: Date.now(), ...p }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(full))
}

export default function CookieConsent() {
  const pathname = usePathname()
  const [visible,     setVisible]     = useState(false)
  const [customizing, setCustomizing] = useState(false)
  const [analytics,   setAnalytics]   = useState(true)
  const [marketing,   setMarketing]   = useState(false)
  const [prefsCookie, setPrefsCookie] = useState(true)

  const isAdmin = pathname?.startsWith('/admin') ?? false

  useEffect(() => {
    if (!isAdmin && !loadPrefs()) setVisible(true)
  }, [isAdmin])

  const accept = () => {
    savePrefs({ analytics: true, marketing: true, preferences: true })
    setVisible(false)
  }

  const reject = () => {
    savePrefs({ analytics: false, marketing: false, preferences: false })
    setVisible(false)
  }

  const save = () => {
    savePrefs({ analytics, marketing, preferences: prefsCookie })
    setVisible(false)
  }

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ y: 120, opacity: 0 }}
          animate={{ y: 0,   opacity: 1 }}
          exit={{ y: 120,    opacity: 0 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          className="fixed bottom-0 left-0 right-0 z-[60] p-4 sm:p-6"
          role="dialog"
          aria-label="Cookie consent"
        >
          <div className="max-w-5xl mx-auto glass rounded-2xl border border-white/10 shadow-[0_-8px_40px_rgba(0,0,0,0.5)] overflow-hidden">
            {!customizing ? (
              /* ── Default banner ── */
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 p-5">
                <Cookie className="w-5 h-5 text-violet-400 flex-shrink-0 mt-0.5 sm:mt-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white/80 leading-relaxed">
                    We use cookies to improve your experience and analyse site usage.
                    See our{' '}
                    <Link href="/privacy#cookies" className="text-violet-400 hover:text-violet-300 underline underline-offset-2">
                      Cookie Policy
                    </Link>{' '}
                    for details.
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => setCustomizing(true)}
                    className="text-xs text-white/45 hover:text-white/70 transition-colors px-2 py-1.5 underline underline-offset-2"
                  >
                    Customize
                  </button>
                  <button
                    onClick={reject}
                    className="px-4 py-2 rounded-lg text-xs font-semibold glass border border-white/20 text-white/70 hover:text-white hover:border-white/40 transition-all"
                  >
                    Reject All
                  </button>
                  <button
                    onClick={accept}
                    className="px-4 py-2 rounded-lg text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white transition-colors shadow-[0_0_14px_rgba(124,58,237,0.4)]"
                  >
                    Accept All
                  </button>
                </div>
              </div>
            ) : (
              /* ── Customise panel ── */
              <div className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-bold text-white">Cookie Preferences</h2>
                  <button onClick={() => setCustomizing(false)} className="text-white/40 hover:text-white/70 transition-colors">
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-3 mb-5">
                  {[
                    {
                      label: 'Essential',
                      desc: 'Required for the site to work. Cannot be disabled.',
                      checked: true,
                      disabled: true,
                      onChange: () => {},
                    },
                    {
                      label: 'Analytics',
                      desc: 'Helps us understand how visitors use the site (Google Analytics).',
                      checked: analytics,
                      disabled: false,
                      onChange: () => setAnalytics((v) => !v),
                    },
                    {
                      label: 'Marketing',
                      desc: 'Used for targeted advertising and retargeting campaigns.',
                      checked: marketing,
                      disabled: false,
                      onChange: () => setMarketing((v) => !v),
                    },
                    {
                      label: 'Preferences',
                      desc: 'Remembers your choices so you don\'t have to set them each visit.',
                      checked: prefsCookie,
                      disabled: false,
                      onChange: () => setPrefsCookie((v) => !v),
                    },
                  ].map((item) => (
                    <label
                      key={item.label}
                      className={`flex items-start gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] ${item.disabled ? '' : 'cursor-pointer hover:bg-white/[0.06] transition-colors'}`}
                    >
                      <div className="relative flex-shrink-0 mt-0.5">
                        <input
                          type="checkbox"
                          checked={item.checked}
                          disabled={item.disabled}
                          onChange={item.onChange}
                          className="sr-only"
                          aria-label={item.label}
                        />
                        <div
                          className="w-5 h-5 rounded flex items-center justify-center transition-colors"
                          style={{ background: item.checked ? '#7C3AED' : 'rgba(255,255,255,0.08)', border: `1px solid ${item.checked ? '#7C3AED' : 'rgba(255,255,255,0.2)'}`, opacity: item.disabled ? 0.7 : 1 }}
                        >
                          {item.checked && <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none"><path d="M2 6l3 3 5-5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-white mb-0.5">{item.label} {item.disabled && <span className="text-white/30 font-normal">(Required)</span>}</p>
                        <p className="text-xs text-white/45">{item.desc}</p>
                      </div>
                    </label>
                  ))}
                </div>

                <div className="flex gap-2 justify-end">
                  <button
                    onClick={reject}
                    className="px-4 py-2 rounded-lg text-xs font-semibold glass border border-white/20 text-white/60 hover:text-white hover:border-white/40 transition-all"
                  >
                    Reject All
                  </button>
                  <button
                    onClick={save}
                    className="px-4 py-2 rounded-lg text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white transition-colors"
                  >
                    Save Preferences
                  </button>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
