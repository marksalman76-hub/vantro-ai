'use client'

import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { X, ArrowRight, Calendar } from 'lucide-react'

const SESSION_KEY = 'vantro_sticky_bar_dismissed'

export default function StickyCtaBar() {
  const pathname = usePathname()
  const [visible,    setVisible]    = useState(false)
  const [dismissed,  setDismissed]  = useState(false)

  // Hide on admin and dashboard routes
  const isAdminOrDashboard = pathname?.startsWith('/admin') || pathname?.startsWith('/dashboard')

  useEffect(() => {
    if (typeof window === 'undefined') return
    if (isAdminOrDashboard) { setDismissed(true); return }
    if (sessionStorage.getItem(SESSION_KEY)) { setDismissed(true); return }

    const handleScroll = () => {
      setVisible(window.scrollY > 300)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [isAdminOrDashboard])

  const dismiss = () => {
    setDismissed(true)
    sessionStorage.setItem(SESSION_KEY, '1')
  }

  return (
    <AnimatePresence>
      {visible && !dismissed && (
        <motion.div
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0,  opacity: 1 }}
          exit={{ y: 80,    opacity: 0 }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
          className="fixed bottom-4 left-4 right-24 z-40"
          role="banner"
          aria-label="Free trial offer"
        >
          <div className="glass rounded-2xl border border-violet-500/20 shadow-[0_8px_40px_rgba(0,0,0,0.5)] px-4 py-3 sm:px-5">
            <div className="flex items-center gap-3">
              {/* Text */}
              <div className="flex-1 min-w-0">
                <p className="text-xs sm:text-sm font-semibold text-white truncate">
                  Ready to 10× your team?{' '}
                  <span className="text-violet-300">Start your free trial today.</span>
                </p>
                <p className="text-[10px] text-white/35 mt-0.5 hidden sm:block">
                  No credit card · Deploy in 10 min
                </p>
              </div>

              {/* CTAs */}
              <div className="flex items-center gap-2 flex-shrink-0">
                <a
                  href="#agents"
                  className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-lg text-xs font-semibold text-white bg-violet-600 hover:bg-violet-500 transition-colors shadow-[0_0_14px_rgba(124,58,237,0.4)] whitespace-nowrap"
                >
                  Start Free
                  <ArrowRight className="w-3 h-3" />
                </a>
                <a
                  href="#roi-calculator"
                  className="hidden sm:inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold text-white glass border border-white/15 hover:border-white/35 transition-all whitespace-nowrap"
                >
                  <Calendar className="w-3 h-3 text-violet-400" />
                  Schedule Demo
                </a>
              </div>

              {/* Dismiss */}
              <button
                onClick={dismiss}
                className="flex-shrink-0 p-1.5 rounded-lg text-white/35 hover:text-white/70 hover:bg-white/[0.06] transition-all"
                aria-label="Dismiss"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
