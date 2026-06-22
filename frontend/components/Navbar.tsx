'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Menu, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import Button from './Button'

const NAV_LINKS = [
  { label: 'Why Vantro',    href: '#why-vantro'     },
  { label: 'Agents',        href: '#agents'         },
  { label: 'Industries',    href: '#industry-adaptability' },
  { label: 'Integrations',  href: '#integrations'   },
  { label: 'Pricing',       href: '/pricing'        },
]

export default function Navbar() {
  const [scrolled,    setScrolled]    = useState(false)
  const [mobileOpen,  setMobileOpen]  = useState(false)

  useEffect(() => {
    const threshold = window.innerHeight * 0.65
    const onScroll  = () => setScrolled(window.scrollY > threshold)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const headerCls = [
    'fixed top-0 inset-x-0 z-50 transition-all duration-500',
    mobileOpen
      ? 'bg-dark-900 border-b border-white/10'
      : scrolled
      ? 'bg-dark/80 backdrop-blur-md border-b border-white/[0.07] shadow-[0_4px_28px_rgba(0,0,0,0.45)]'
      : 'bg-transparent border-b border-transparent',
  ].join(' ')

  return (
    <header className={headerCls}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-18">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-1.5 group">
            <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-[0_0_15px_rgba(124,58,237,0.45)]">
              V
            </span>
            <span className="text-xl font-bold text-white tracking-tight">
              Vantro<span className="text-violet-400">.ai</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden lg:flex items-center gap-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="px-4 py-2 text-sm text-white/65 hover:text-white rounded-lg hover:bg-white/[0.06] transition-all duration-200"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Desktop CTAs */}
          <div className="hidden lg:flex items-center gap-3">
            <Button variant="ghost" size="sm" href="/login">Log in</Button>
            <Button variant="primary" size="sm" href="/signup" arrow>Get Started Free</Button>
          </div>

          {/* Mobile toggle */}
          <button
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Toggle menu"
            className="lg:hidden p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/[0.06] transition-all"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="lg:hidden border-t border-white/10 overflow-hidden"
          >
            <div className="px-4 py-4 flex flex-col gap-1">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="px-4 py-3 text-sm text-white/70 hover:text-white rounded-lg hover:bg-white/[0.06] transition-all"
                >
                  {link.label}
                </Link>
              ))}
              <div className="pt-3 flex flex-col gap-2">
                <Button variant="secondary" size="sm" href="/login"  className="w-full">Log in</Button>
                <Button variant="primary"   size="sm" href="/signup" className="w-full" arrow>Get Started Free</Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
