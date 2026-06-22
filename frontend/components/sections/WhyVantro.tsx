'use client'

import { useRef } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { Globe, Layers, RefreshCw, Mic } from 'lucide-react'

const DIFFERENTIATORS = [
  {
    icon: Globe,
    color: '#C084FC',
    bg: '#7C3AED',
    title: 'Universal Adaptability',
    description: 'Works across 50+ industries without reconfiguration. Deploy to SaaS, healthcare, finance, or retail in minutes — the agent figures out the rest.',
    stat: '50+ industries',
  },
  {
    icon: Layers,
    color: '#93C5FD',
    bg: '#3B82F6',
    title: 'Flexible Deployment',
    description: 'Start with one specialist agent or roll out a full team on day one. Pay for what you use. Scale as you grow. No lock-in.',
    stat: '1 to ∞ agents',
  },
  {
    icon: RefreshCw,
    color: '#67E8F9',
    bg: '#06B6D4',
    title: 'Dynamic Evolution',
    description: 'Unlike static AI tools, Vantro agents learn from every interaction. By Month 1 they perform 40% better than Day 1 — and never stop improving.',
    stat: '+40% by Month 1',
  },
  {
    icon: Mic,
    color: '#F9A8D4',
    bg: '#EC4899',
    title: 'Your Brand Voice',
    description: "Agents learn your tone, vocabulary, and personality within days. By Day 7, customers can't tell whether they're talking to AI or your best human rep.",
    stat: '95% voice match',
  },
]

function TiltCard({
  d,
  index,
}: {
  d: typeof DIFFERENTIATORS[0]
  index: number
}) {
  const ref = useRef<HTMLDivElement>(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [10, -10]), { stiffness: 500, damping: 35 })
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-10, 10]), { stiffness: 500, damping: 35 })
  const glowX = useTransform(x, [-0.5, 0.5], [0, 100])
  const glowY = useTransform(y, [-0.5, 0.5], [0, 100])

  const Icon = d.icon

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.55, delay: index * 0.1, ease: [0.22, 1, 0.36, 1] }}
      onMouseMove={(e) => {
        const rect = ref.current?.getBoundingClientRect()
        if (!rect) return
        x.set((e.clientX - rect.left) / rect.width - 0.5)
        y.set((e.clientY - rect.top) / rect.height - 0.5)
      }}
      onMouseLeave={() => { x.set(0); y.set(0) }}
      style={{ rotateX, rotateY, transformPerspective: 900 }}
      className="relative group cursor-default"
    >
      {/* Dynamic glow on hover */}
      <motion.div
        className="absolute -inset-px rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
        style={{
          background: `radial-gradient(circle at ${glowX}% ${glowY}%, ${d.bg}35 0%, transparent 65%)`,
          borderRadius: '16px',
        }}
      />

      <div
        className="relative h-full glass-ultra rounded-2xl p-6 text-center"
        style={{ boxShadow: `0 4px 30px ${d.bg}10` }}
      >
        {/* Shine top edge */}
        <div className="absolute top-0 left-4 right-4 h-px rounded-full opacity-60"
          style={{ background: `linear-gradient(90deg, transparent, ${d.color}40, transparent)` }}
        />

        {/* Icon */}
        <div className="relative mb-5">
          <div
            className="w-14 h-14 rounded-2xl mx-auto flex items-center justify-center transition-transform duration-300 group-hover:scale-110"
            style={{
              background: `${d.bg}18`,
              border: `1px solid ${d.bg}35`,
              boxShadow: `0 0 24px ${d.bg}20`,
            }}
          >
            <Icon className="w-6 h-6" style={{ color: d.color }} />
          </div>
          {/* Icon glow pulse */}
          <div
            className="absolute inset-0 w-14 h-14 mx-auto rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-md"
            style={{ background: `${d.bg}25` }}
          />
        </div>

        {/* Stat badge */}
        <div
          className="inline-block px-3 py-1 rounded-full text-[10px] font-bold tracking-wide mb-3"
          style={{ background: `${d.bg}18`, color: d.color, border: `1px solid ${d.bg}30` }}
        >
          {d.stat}
        </div>

        <h3 className="text-base font-bold text-white mb-3 leading-snug">{d.title}</h3>
        <p className="text-sm text-white/50 leading-relaxed">{d.description}</p>
      </div>
    </motion.div>
  )
}

export default function WhyVantro() {
  return (
    <section
      id="why-vantro"
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #070D1F 0%, #0A1230 100%)' }}
    >
      {/* Background mesh */}
      <div className="absolute inset-0 mesh-grid-fine opacity-50 pointer-events-none" />

      {/* Ambient blob */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-violet-600/08 blur-[160px] rounded-full pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
            <br />
            <span className="text-white/55 text-2xl sm:text-3xl lg:text-4xl font-medium">
              Not the Other Way Around
            </span>
          </h2>
          <p className="section-sub mt-4">
            Every other AI tool forces you to adapt to it. Vantro flips the script — it learns your world.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {DIFFERENTIATORS.map((d, i) => (
            <TiltCard key={d.title} d={d} index={i} />
          ))}
        </div>

        {/* Bottom differentiator strip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22, delay: 0.3 }}
          className="mt-12 glass-strong rounded-2xl p-6 border border-violet-500/10"
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
                className="px-3 py-1.5 rounded-full text-xs font-medium glass border border-white/10 text-white/60 cursor-default"
              >
                ✓ {item}
              </motion.span>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
