'use client';

import { motion } from 'framer-motion';
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
  return (
    <section className="py-32" style={{ backgroundColor: 'oklch(0.10 0 0)' }}>
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
            style={{ background: 'radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%)' }}
          />
          <img
            src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/saLNUqZiiYVuufKN.png"
            alt="Vantro orb"
            className="relative w-full max-w-md"
            style={{
              mixBlendMode: 'screen',
              WebkitMaskImage: 'radial-gradient(circle, black 40%, transparent 75%)',
              maskImage: 'radial-gradient(circle, black 40%, transparent 75%)',
              animation: 'float 8s ease-in-out infinite',
            }}
          />
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
