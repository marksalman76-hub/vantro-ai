'use client';

import { motion, useReducedMotion } from 'framer-motion';
import { useRef } from 'react';

const STATS = [
  {
    number: '24/7',
    label: 'Always on',
    description: 'Your workforce never sleeps, never burns out, never takes a sick day.',
  },
  {
    number: '10x',
    label: 'Faster output',
    description: 'Parallelize work across a full roster instead of a single overloaded queue.',
  },
  {
    number: '70%',
    label: 'Cost reduction',
    description: 'Replace fragmented tooling and manual ops with one orchestrated platform.',
  },
  {
    number: '5 min',
    label: 'Time to value',
    description: 'From signup to your first deployed agent in under five minutes.',
  },
];

interface StatCardProps {
  number: string;
  label: string;
  description: string;
  index: number;
}

function StatCard({ number, label, description, index }: StatCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const el = cardRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    el.style.setProperty('--mx', `${e.clientX - rect.left}px`);
    el.style.setProperty('--my', `${e.clientY - rect.top}px`);
  }

  return (
    <motion.div
      ref={cardRef}
      className="glass-card rounded-xl p-6"
      onMouseMove={handleMouseMove}
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
    >
      <div className="spotlight" />
      <div className="sheen" />
      <p
        className="text-xs uppercase tracking-widest mb-2"
        style={{ fontFamily: 'JetBrains Mono, monospace', color: 'oklch(0.70 0 0)' }}
      >
        {label}
      </p>
      <p
        className="font-bold text-4xl mb-2"
        style={{
          fontFamily: 'Space Grotesk, sans-serif',
          background: 'linear-gradient(180deg, #ffffff 0%, #d8d8d8 30%, #9a9a9a 70%, #555555 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        {number}
      </p>
      <p className="text-sm leading-relaxed mt-2" style={{ color: 'oklch(0.70 0 0)' }}>
        {description}
      </p>
    </motion.div>
  );
}

export function WhyVantro() {
  const prefersReduced = useReducedMotion()
  return (
    <section className="py-32" style={{ backgroundColor: 'oklch(0.12 0.010 248)' }}>
      <div className="max-w-6xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
        {/* Left: orb */}
        <motion.div
          className="relative flex items-center justify-center"
          initial={{ opacity: 0, scale: 0.92 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.8 }}
        >
          {/* Glow behind orb */}
          <div
            className="absolute inset-0 blur-3xl rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(80,130,255,0.10) 0%, transparent 70%)' }}
          />
          <motion.div
            initial={prefersReduced ? false : { scale: 0.86, opacity: 0 }}
            whileInView={prefersReduced ? {} : { scale: 1, opacity: 1 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
            style={{ position: 'relative', width: '100%', maxWidth: '28rem' }}
          >
            {!prefersReduced && (
              <motion.div
                animate={{
                  background: [
                    'radial-gradient(circle 120px at 30% 28%, rgba(255,255,255,0.72) 0%, transparent 65%)',
                    'radial-gradient(circle 120px at 72% 22%, rgba(255,255,255,0.72) 0%, transparent 65%)',
                    'radial-gradient(circle 120px at 76% 74%, rgba(255,255,255,0.72) 0%, transparent 65%)',
                    'radial-gradient(circle 120px at 28% 78%, rgba(255,255,255,0.72) 0%, transparent 65%)',
                    'radial-gradient(circle 120px at 30% 28%, rgba(255,255,255,0.72) 0%, transparent 65%)',
                  ],
                }}
                transition={{ duration: 5.5, repeat: Infinity, ease: 'linear' }}
                style={{
                  position: 'absolute', inset: 0,
                  mixBlendMode: 'screen',
                  pointerEvents: 'none',
                  zIndex: 2,
                  WebkitMaskImage: 'radial-gradient(circle, black 20%, rgba(0,0,0,0.50) 48%, transparent 82%)',
                  maskImage: 'radial-gradient(circle, black 20%, rgba(0,0,0,0.50) 48%, transparent 82%)',
                }}
              />
            )}
            <motion.img
              src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/saLNUqZiiYVuufKN.png"
              alt="Vantro orb"
              className="w-full"
              animate={
                prefersReduced
                  ? {}
                  : {
                      y: [0, -22, -5, -30, -8, 0],
                      x: [0, -16, 11, -9, 5, 0],
                      scale: [1, 1.06, 0.96, 1.08, 0.98, 1],
                      filter: [
                        'brightness(1) drop-shadow(0 0 25px rgba(255,255,255,0.12))',
                        'brightness(1.35) drop-shadow(0 0 70px rgba(255,255,255,0.40))',
                        'brightness(0.90) drop-shadow(0 0 10px rgba(255,255,255,0.04))',
                        'brightness(1.25) drop-shadow(0 0 60px rgba(255,255,255,0.28))',
                        'brightness(1.04) drop-shadow(0 0 35px rgba(255,255,255,0.16))',
                        'brightness(1) drop-shadow(0 0 25px rgba(255,255,255,0.12))',
                      ],
                    }
              }
              transition={prefersReduced ? {} : { duration: 12, repeat: Infinity, ease: 'easeInOut' }}
              style={{
                mixBlendMode: 'screen',
                WebkitMaskImage: 'radial-gradient(circle, black 20%, rgba(0,0,0,0.50) 48%, transparent 82%)',
                maskImage: 'radial-gradient(circle, black 20%, rgba(0,0,0,0.50) 48%, transparent 82%)',
                position: 'relative',
                zIndex: 1,
              }}
            />
          </motion.div>
        </motion.div>

        {/* Right: stats */}
        <div>
          <motion.h2
            className="font-bold text-4xl mb-8"
            style={{ fontFamily: 'Space Grotesk, sans-serif', color: 'oklch(0.97 0 0)' }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            The math is obvious.
          </motion.h2>

          <div className="grid grid-cols-2 gap-4">
            {STATS.map((stat, i) => (
              <StatCard key={stat.label} {...stat} index={i} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
