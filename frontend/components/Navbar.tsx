'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Menu, X, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import Button from './Button'

const NAV_LINKS = [
  { label: 'Why Vantro',   href: '#why-vantro'           },
  { label: 'Agents',       href: '#agents'               },
  { label: 'Industries',   href: '#industry-adaptability' },
  { label: 'Integrations', href: '#integrations'         },
  { label: 'Pricing',      href: '/pricing'              },
]

export default function Navbar() {
  const [scrolled,   setScrolled]   = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const threshold = 80
    const onScroll = () => setScrolled(window.scrollY > threshold)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const headerCls = [
    'fixed top-0 inset-x-0 z-50 transition-all duration-500',
    mobileOpen
      ? 'bg-[#070D1F] border-b border-white/08'
      : scrolled
      ? 'border-b border-white/[0.06] shadow-[0_4px_40px_rgba(0,0,0,0.5)]'
      : 'border-b border-transparent',
  ].join(' ')

  const navBg = scrolled || mobileOpen
    ? 'rgba(7,13,31,0.88)'
    : 'transparent'

  return (
    <header
      className={headerCls}
      style={{
        backdropFilter: scrolled ? 'blur(20px) saturate(1.5)' : 'none',
        WebkitBackdropFilter: scrolled ? 'blur(20px) saturate(1.5)' : 'none',
        background: navBg,
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-[68px]">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group flex-shrink-0">
            <motion.div
              whileHover={{ scale: 1.08, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-black text-sm"
              style={{
                background: 'linear-gradient(135deg, #7C3AED, #3B82F6)',
                boxShadow: '0 0 20px rgba(124,58,237,0.45), 0 0 40px rgba(124,58,237,0.15)',
              }}
            >
              V
            </motion.div>
            <span className="text-xl font-bold text-white tracking-tight">
              Vantro<span className="text-violet-400">.ai</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden lg:flex items-center gap-0.5">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="relative px-4 py-2 text-sm text-white/55 hover:text-white rounded-lg transition-all duration-200 group"
              >
                <span className="relative z-10">{link.label}</span>
                <span className="absolute inset-0 rounded-lg bg-white/0 group-hover:bg-white/[0.05] transition-all duration-200" />
              </Link>
            ))}
          </nav>

          {/* Desktop CTAs */}
          <div className="hidden lg:flex items-center gap-3">
            <Button variant="ghost" size="sm" href="/login">Log in</Button>
            <Button variant="primary" size="sm" href="/signup" arrow>Get Started Free</Button>
          </div>

          {/* Mobile toggle */}
          <motion.button
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Toggle menu"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="lg:hidden p-2.5 rounded-xl text-white/60 hover:text-white glass hover:bg-white/[0.06] transition-colors"
          >
            <AnimatePresence mode="wait">
              {mobileOpen ? (
                <motion.div key="x" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.15 }}>
                  <X className="w-5 h-5" />
                </motion.div>
              ) : (
                <motion.div key="menu" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.15 }}>
                  <Menu className="w-5 h-5" />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="lg:hidden border-t border-white/08 overflow-hidden"
          >
            <div className="px-4 py-5 flex flex-col gap-1">
              {NAV_LINKS.map((link, i) => (
                <motion.div
                  key={link.href}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link
                    href={link.href}
                    onClick={() => setMobileOpen(false)}
                    className="block px-4 py-3 text-sm text-white/65 hover:text-white rounded-xl hover:bg-white/[0.05] transition-all font-medium"
                  >
                    {link.label}
                  </Link>
                </motion.div>
              ))}
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
                className="pt-4 flex flex-col gap-2.5 border-t border-white/08 mt-2"
              >
                <Button variant="secondary" size="sm" href="/login" className="w-full justify-center">Log in</Button>
                <Button variant="primary" size="sm" href="/signup" className="w-full justify-center" arrow>Get Started Free</Button>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
