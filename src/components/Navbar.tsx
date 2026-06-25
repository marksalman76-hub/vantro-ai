'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Zap } from 'lucide-react';

const NAV_LINKS = [
  { label: 'Agents', href: '#agents' },
  { label: 'Integrations', href: '#integrations' },
  { label: 'Pricing', href: '/#pricing' },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <motion.nav
        initial={{ y: -16, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        style={{
          position: 'fixed',
          top: 0, left: 0, right: 0,
          zIndex: 50,
          backgroundColor: scrolled ? 'rgba(15, 20, 25, 0.96)' : '#0F1419',
          borderBottom: scrolled ? '1px solid #2D3748' : '1px solid transparent',
          backdropFilter: scrolled ? 'blur(16px)' : 'none',
          transition: 'background-color 0.3s ease, border-color 0.3s ease',
        }}
      >
        <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '4rem' }}>

            {/* Logo */}
            <a href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
              <img
                src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/uLNNHswnlaLuEQJY.png"
                alt="Vantro"
                style={{ height: '2rem', width: 'auto' }}
              />
              <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '0.9rem', letterSpacing: '0.1em', color: '#FFFFFF' }}>
                VANTRO.ai
              </span>
            </a>

            {/* Desktop nav */}
            <div className="hidden md:flex" style={{ alignItems: 'center', gap: '2rem' }}>
              {NAV_LINKS.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  style={{ color: '#9CA3AF', fontSize: '0.875rem', fontWeight: 500, textDecoration: 'none', transition: 'color 0.15s ease' }}
                  onMouseEnter={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#FFFFFF'; }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#9CA3AF'; }}
                >
                  {link.label}
                </a>
              ))}
            </div>

            {/* Desktop CTA */}
            <div className="hidden md:flex" style={{ alignItems: 'center', gap: '0.75rem' }}>
              <a
                href="/signin"
                style={{ color: '#9CA3AF', fontSize: '0.875rem', fontWeight: 500, textDecoration: 'none', transition: 'color 0.15s ease' }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#FFFFFF'; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#9CA3AF'; }}
              >
                Sign in
              </a>
              <a
                href="/#pricing"
                className="btn-orange"
                style={{ padding: '0.5rem 1.25rem', borderRadius: '0.375rem', fontSize: '0.875rem', textDecoration: 'none' }}
              >
                <Zap size={14} />
                Deploy now
              </a>
            </div>

            {/* Mobile toggle */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden"
              style={{ background: 'none', border: 'none', color: '#FFFFFF', cursor: 'pointer', padding: '0.5rem' }}
              aria-label="Toggle menu"
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </motion.nav>

      {/* Mobile dropdown */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            style={{ position: 'fixed', top: '4rem', left: 0, right: 0, zIndex: 49, backgroundColor: '#0F1419', borderBottom: '1px solid #2D3748', padding: '1.5rem' }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {NAV_LINKS.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  style={{ color: '#E5E7EB', fontSize: '1rem', fontWeight: 500, textDecoration: 'none', padding: '0.625rem 0', borderBottom: '1px solid #2D3748' }}
                >
                  {link.label}
                </a>
              ))}
              <a
                href="/#pricing"
                onClick={() => setMobileOpen(false)}
                className="btn-orange"
                style={{ padding: '0.75rem 1.5rem', borderRadius: '0.375rem', fontSize: '0.95rem', justifyContent: 'center', marginTop: '0.5rem', textDecoration: 'none' }}
              >
                <Zap size={16} />
                Deploy now
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
