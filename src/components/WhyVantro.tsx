'use client';

import { useRef } from 'react';
import { motion } from 'framer-motion';

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
        style={{ fontFamily: 'JetBrains Mono, monospace', color: '#9CA3AF' }}
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
      <p className="text-sm leading-relaxed mt-2" style={{ color: '#9CA3AF' }}>
        {description}
      </p>
    </motion.div>
  );
}

export function WhyVantro() {
  return (
    <section className="py-32" style={{ backgroundColor: '#0F1419' }}>
      <div className="max-w-6xl mx-auto px-6">
          <motion.h2
            className="font-bold text-4xl mb-8 text-center"
            style={{ fontFamily: 'Space Grotesk, sans-serif', color: '#FFFFFF' }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            The math is obvious.
          </motion.h2>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {STATS.map((stat, i) => (
              <StatCard key={stat.label} {...stat} index={i} />
            ))}
          </div>
      </div>
    </section>
  );
}
