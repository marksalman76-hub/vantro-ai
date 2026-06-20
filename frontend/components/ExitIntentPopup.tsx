'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Zap, Calendar } from 'lucide-react'

const SESSION_KEY = 'vantro_exit_shown'
const MIN_TIME_MS = 20_000

export default function ExitIntentPopup() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return
    if (sessionStorage.getItem(SESSION_KEY)) return

    let armed = false
    const timer = setTimeout(() => { armed = true }, MIN_TIME_MS)

    const handleMouseOut = (e: MouseEvent) => {
      if (!armed) return
      if (e.clientY > 0) return
      if ((e.target as Node).nodeName === 'HTML') return
      setVisible(true)
      sessionStorage.setItem(SESSION_KEY, '1')
      document.removeEventListener('mouseleave', handleMouseOut)
    }

    document.addEventListener('mouseleave', handleMouseOut)
    return () => {
      clearTimeout(timer)
      document.removeEventListener('mouseleave', handleMouseOut)
    }
  }, [])

  const dismiss = () => setVisible(false)

  return (
    <AnimatePresence>
      {visible && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-[70]"
            onClick={dismiss}
            aria-hidden="true"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1,   y: 0  }}
            exit={{ opacity: 0,   scale: 0.9, y: 20  }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="fixed inset-0 flex items-center justify-center z-[71] p-4 pointer-events-none"
          >
            <div
              className="relative w-full max-w-lg glass rounded-2xl border border-white/10 shadow-[0_20px_80px_rgba(0,0,0,0.7)] p-8 pointer-events-auto"
              role="dialog"
              aria-modal="true"
              aria-labelledby="exit-heading"
            >
              {/* Close */}
              <button
                onClick={dismiss}
                className="absolute top-4 right-4 p-2 rounded-lg text-white/40 hover:text-white hover:bg-white/[0.08] transition-all"
                aria-label="Close"
              >
                <X className="w-4 h-4" />
              </button>

              {/* Glow */}
              <div className="absolute inset-0 bg-gradient-to-br from-violet-600/10 to-blue-600/5 rounded-2xl pointer-events-none" />

              {/* Badge */}
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-violet-500/20 text-violet-300 border border-violet-500/25 mb-5">
                <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
                500+ teams already inside
              </div>

              <h2 id="exit-heading" className="text-2xl sm:text-3xl font-bold text-white mb-3">
                Wait! Don&apos;t Miss Out
              </h2>
              <p className="text-white/60 leading-relaxed mb-8">
                See how 500+ forward-thinking teams are saving 100+ hours per week with Vantro AI agents — in just 15 minutes.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <a
                  href="#agents"
                  onClick={dismiss}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-[0_4px_20px_rgba(124,58,237,0.35)] transition-all"
                >
                  <Zap className="w-4 h-4" />
                  Start Free Trial
                </a>
                <a
                  href="#roi-calculator"
                  onClick={dismiss}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold text-white glass border border-white/20 hover:border-white/40 hover:bg-white/[0.08] transition-all"
                >
                  <Calendar className="w-4 h-4 text-violet-400" />
                  See My ROI First
                </a>
              </div>

              <p className="text-center text-xs text-white/30 mt-4">
                No credit card · Setup in 10 min · Cancel any time
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
