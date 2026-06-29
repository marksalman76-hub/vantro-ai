'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function CookieConsent() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookie_consent');
    if (consent !== 'accepted' && consent !== 'rejected') {
      setShow(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookie_consent', 'accepted');
    setShow(false);
  };

  const handleDecline = () => {
    localStorage.setItem('cookie_consent', 'rejected');
    setShow(false);
  };

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
          style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: 9999,
            background: 'rgba(10,13,17,0.95)',
            borderTop: '1px solid rgba(0,217,255,0.15)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            padding: '16px 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px',
          }}
        >
          <p
            style={{
              margin: 0,
              color: 'rgba(255,255,255,0.8)',
              fontSize: '14px',
              lineHeight: '1.5',
              flex: '1 1 300px',
            }}
          >
            We use cookies to improve your experience and analyze usage.{' '}
            <a
              href="/cookies"
              style={{
                color: '#00D9FF',
                textDecoration: 'underline',
                textUnderlineOffset: '2px',
              }}
            >
              Cookie Policy
            </a>{' '}
            &amp;{' '}
            <a
              href="/privacy"
              style={{
                color: '#00D9FF',
                textDecoration: 'underline',
                textUnderlineOffset: '2px',
              }}
            >
              Privacy Policy
            </a>
            .
          </p>

          <div
            style={{
              display: 'flex',
              gap: '12px',
              alignItems: 'center',
              flexShrink: 0,
            }}
          >
            <button
              onClick={handleDecline}
              style={{
                background: 'transparent',
                border: '1px solid rgba(255,255,255,0.2)',
                color: 'rgba(255,255,255,0.6)',
                padding: '8px 20px',
                borderRadius: '6px',
                fontSize: '14px',
                cursor: 'pointer',
                transition: 'border-color 0.2s, color 0.2s',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.4)';
                (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.9)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.2)';
                (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.6)';
              }}
            >
              Decline
            </button>

            <button
              onClick={handleAccept}
              style={{
                background: '#FF6B35',
                border: '1px solid #FF6B35',
                color: '#ffffff',
                padding: '8px 20px',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'background 0.2s, opacity 0.2s',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.opacity = '0.85';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.opacity = '1';
              }}
            >
              Accept All
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
