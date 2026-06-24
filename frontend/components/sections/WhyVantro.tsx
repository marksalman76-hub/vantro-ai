'use client'

import { useRef } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'

const REASONS = [
  {
    num: '01',
    color: '#C084FC',
    bg: '#7C3AED',
    title: 'Universal Adaptability',
    description: 'Works across 50+ industries without reconfiguration. Deploy to SaaS, healthcare, finance, or retail in minutes.',
    stat: '50+ industries',
  },
  {
    num: '02',
    color: '#93C5FD',
    bg: '#3B82F6',
    title: 'Flexible Deployment',
    description: 'Start with one specialist agent or roll out a full team on day one. Pay for what you use, scale as you grow, no lock-in.',
    stat: '1 to ∞ agents',
  },
  {
    num: '03',
    color: '#67E8F9',
    bg: '#06B6D4',
    title: 'Dynamic Evolution',
    description: 'Unlike static AI tools, Vantro agents learn from every interaction. By Month 1 they perform 40% better than Day 1.',
    stat: '+40% by Month 1',
  },
  {
    num: '04',
    color: '#F9A8D4',
    bg: '#EC4899',
    title: 'Your Brand Voice',
    description: "Agents learn your tone, vocabulary, and personality within days. By Day 7, customers can't tell whether they're talking to AI.",
    stat: '95% voice match',
  },
]

const METRICS = [
  { value: '50+',  label: 'Industries served',  color: '#C084FC', bg: '#7C3AED' },
  { value: '40%',  label: 'Better by Month 1',  color: '#93C5FD', bg: '#3B82F6' },
  { value: '95%',  label: 'Brand voice match',  color: '#67E8F9', bg: '#06B6D4' },
  { value: '24/7', label: 'Always on, no gaps', color: '#F9A8D4', bg: '#EC4899' },
]

export default function WhyVantro() {
  return (
    <section
      id="why-vantro"
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #070D1F 0%, #0A1230 100%)' }}
    >
      <div className="absolute inset-0 mesh-grid-fine opacity-50 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-violet-600/07 blur-[160px] rounded-full pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="text-center mb-16"
        >
          <span className="section-badge-violet mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
            Why Choose Vantro
          </span>
          <h2 className="section-heading mt-4 mb-4">
            AI That Adapts to{' '}
            <span className="gradient-text">Your Business</span>
          </h2>
          <p className="section-sub mt-2">
            Every other AI tool forces you to adapt to it. Vantro flips the script — it learns your world.
          </p>
        </motion.div>

        {/* Split layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center mb-14">

          {/* Left: numbered reasons */}
          <div className="space-y-0">
            {REASONS.map((r, i) => (
              <motion.div
                key={r.num}
                initial={{ opacity: 0, x: -24 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ type: 'spring', stiffness: 180, damping: 22, delay: i * 0.1 }}
                className="flex gap-5 py-6 group cursor-default"
                style={{ borderBottom: i < REASONS.length - 1 ? '1px solid rgba(255,255,255,0.06)' : 'none' }}
              >
                {/* Step number */}
                <div
                  className="text-3xl font-black leading-none shrink-0 w-10 transition-opacity duration-300 group-hover:opacity-100 opacity-20"
                  style={{ color: r.color }}
                >
                  {r.num}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-base font-bold text-white group-hover:text-white transition-colors">
                      {r.title}
                    </h3>
                    <span
                      className="shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full"
                      style={{ color: r.color, background: `${r.bg}15`, border: `1px solid ${r.bg}25` }}
                    >
                      {r.stat}
                    </span>
                  </div>
                  <p className="text-sm text-white/40 leading-relaxed group-hover:text-white/60 transition-colors">
                    {r.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Right: 2×2 metric cards */}
          <div className="grid grid-cols-2 gap-4">
            {METRICS.map((m, i) => (
              <motion.div
                key={m.value}
                initial={{ opacity: 0, scale: 0.92 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ type: 'spring', stiffness: 200, damping: 22, delay: 0.2 + i * 0.07 }}
                whileHover={{ y: -4, scale: 1.02 }}
                className="relative glass-ultra rounded-2xl p-6 text-center overflow-hidden group cursor-default"
                style={{ border: `1px solid ${m.bg}20` }}
              >
                {/* Top shine */}
                <div
                  className="absolute top-0 left-4 right-4 h-px opacity-60"
                  style={{ background: `linear-gradient(90deg, transparent, ${m.color}50, transparent)` }}
                />
                {/* Hover glow */}
                <div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                  style={{ background: `radial-gradient(ellipse at 50% 50%, ${m.bg}18 0%, transparent 70%)` }}
                />

                <div
                  className="relative text-4xl font-black tracking-tight mb-2 leading-none"
                  style={{ color: m.color }}
                >
                  {m.value}
                </div>
                <p className="relative text-xs text-white/40 font-medium leading-snug">{m.label}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Bottom differentiator strip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22, delay: 0.3 }}
          className="glass-strong rounded-2xl p-6 border border-violet-500/10"
        >
          <p className="text-center text-[10px] text-white/30 mb-5 uppercase tracking-[0.2em] font-bold">
            The Only AI Platform That
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            {[
              'Works across 50+ industries',
              'Learns your brand voice',
              'Scales from 1 to unlimited agents',
              'Gets smarter every day',
              'Suggests strategy, not just executes',
            ].map((item) => (
              <motion.span
                key={item}
                whileHover={{ scale: 1.05, y: -2 }}
                transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium glass border border-white/10 text-white/60 cursor-default"
              >
                <svg className="w-3 h-3 text-emerald-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                {item}
              </motion.span>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
