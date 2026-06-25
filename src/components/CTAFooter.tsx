'use client';

import { motion, useReducedMotion } from 'framer-motion';
import { Zap } from 'lucide-react';

export function CTAFooter() {
  const prefersReduced = useReducedMotion();

  return (
    <section
      style={{
        backgroundColor: '#0F1419',
        paddingTop: '7rem',
        paddingBottom: '7rem',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Orange radial glow */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          pointerEvents: 'none',
        }}
      >
        {!prefersReduced && (
          <motion.div
            animate={{ scale: [1, 1.12, 1], opacity: [0.5, 0.8, 0.5] }}
            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
            style={{
              width: 600,
              height: 300,
              borderRadius: '50%',
              background: 'radial-gradient(ellipse, rgba(255,107,53,0.18) 0%, transparent 70%)',
            }}
          />
        )}
      </div>

      {/* Content */}
      <motion.div
        className="relative z-10"
        style={{ textAlign: 'center', maxWidth: '44rem', margin: '0 auto', padding: '0 1.5rem', position: 'relative', zIndex: 1 }}
        initial={{ opacity: 0, y: 32 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      >
        <h2
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 800,
            fontSize: 'clamp(2rem, 5vw, 3.25rem)',
            letterSpacing: '-0.03em',
            lineHeight: 1.08,
            color: '#FFFFFF',
            marginBottom: '1.25rem',
          }}
        >
          Deploy Your{' '}
          <span style={{ color: '#FF6B35' }}>Autonomous Workforce</span>{' '}
          Today.
        </h2>

        <p style={{ color: '#9CA3AF', fontSize: '1.1rem', lineHeight: 1.65, marginBottom: '2.5rem', maxWidth: '30rem', margin: '0 auto 2.5rem' }}>
          First agents live in under 5 minutes. No credit card. No integrations team. No excuses.
        </p>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <a
            href="/#pricing"
            className="btn-orange"
            style={{
              padding: '1rem 2rem',
              borderRadius: '0.5rem',
              fontSize: '1.05rem',
              fontWeight: 700,
              textDecoration: 'none',
              boxShadow: '0 0 60px rgba(255,107,53,0.45), 0 0 120px rgba(255,107,53,0.20), 0 8px 24px rgba(255,107,53,0.40), inset 0 1px 0 rgba(255,255,255,0.20)',
            }}
          >
            <Zap size={20} />
            Deploy Now — It's Free
          </a>
          <a
            href="#agents"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
              padding: '1rem 1.5rem',
              borderRadius: '0.5rem',
              fontSize: '1.05rem',
              fontWeight: 600,
              color: '#E5E7EB',
              textDecoration: 'none',
              border: '1px solid #2D3748',
              backgroundColor: 'rgba(45,55,72,0.3)',
              transition: 'border-color 0.2s ease, color 0.2s ease',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLAnchorElement).style.borderColor = 'rgba(0,217,255,0.45)';
              (e.currentTarget as HTMLAnchorElement).style.color = '#FFFFFF';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLAnchorElement).style.borderColor = '#2D3748';
              (e.currentTarget as HTMLAnchorElement).style.color = '#E5E7EB';
            }}
          >
            Browse all 22 agents
          </a>
        </div>
      </motion.div>
    </section>
  );
}
