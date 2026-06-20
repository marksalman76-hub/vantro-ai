'use client'

import { motion } from 'framer-motion'
import { Globe, Layers, RefreshCw, Mic } from 'lucide-react'

const DIFFERENTIATORS = [
  {
    icon: Globe,
    color: '#7C3AED',
    glow: 'rgba(124,58,237,0.20)',
    title: 'Universal Adaptability',
    description:
      'Works across 50+ industries without reconfiguration. Deploy to SaaS, healthcare, finance, or retail in minutes — the agent figures out the rest.',
    stat: '50+ industries',
  },
  {
    icon: Layers,
    color: '#3B82F6',
    glow: 'rgba(59,130,246,0.18)',
    title: 'Flexible Deployment',
    description:
      'Start with one specialist agent or roll out a full team on day one. Pay for what you use. Scale as you grow. No lock-in, no minimum commitment.',
    stat: '1 to unlimited agents',
  },
  {
    icon: RefreshCw,
    color: '#06B6D4',
    glow: 'rgba(6,182,212,0.18)',
    title: 'Dynamic Evolution',
    description:
      'Unlike static AI tools, Vantro agents learn from every interaction. By Month 1 they perform 40% better than Day 1 — and they never stop improving.',
    stat: '+40% by Month 1',
  },
  {
    icon: Mic,
    color: '#EC4899',
    glow: 'rgba(236,72,153,0.18)',
    title: 'Your Brand Voice',
    description:
      'Agents learn your tone, vocabulary, and personality within days. By Day 7, customers can\'t tell whether they\'re talking to an AI or your best human rep.',
    stat: '95% voice match',
  },
]

const item = {
  hidden: { opacity: 0, y: 28 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.55, ease: 'easeOut' as const } },
}

export default function WhyVantro() {
  return (
    <section id="why-vantro" className="section-padding bg-dark-900/70">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-violet-500/20 text-violet-300 mb-4">
            Why Choose Vantro
          </span>
          <h2 className="section-heading mb-4">
            AI That Adapts to{' '}
            <span className="gradient-text">Your Business</span>
            <br />
            Not the Other Way Around
          </h2>
          <p className="section-sub">
            Every other AI tool forces you to adapt to it. Vantro flips the script — it learns your world.
          </p>
        </motion.div>

        <motion.div
          variants={{ hidden: {}, show: { transition: { staggerChildren: 0.1 } } }}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-60px' }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5"
        >
          {DIFFERENTIATORS.map((d) => {
            const Icon = d.icon
            return (
              <motion.div
                key={d.title}
                variants={item}
                className="glass glass-hover rounded-2xl p-6 text-center group"
              >
                {/* Icon */}
                <div
                  className="w-14 h-14 rounded-2xl mx-auto flex items-center justify-center mb-5 transition-all duration-300 group-hover:scale-110"
                  style={{
                    background: `${d.color}1A`,
                    border: `1px solid ${d.color}40`,
                    boxShadow: `0 0 20px ${d.glow}`,
                  }}
                >
                  <Icon className="w-6 h-6" style={{ color: d.color }} />
                </div>

                {/* Stat badge */}
                <div
                  className="inline-block px-2.5 py-1 rounded-full text-[10px] font-bold tracking-wide mb-3"
                  style={{ background: `${d.color}18`, color: d.color }}
                >
                  {d.stat}
                </div>

                <h3 className="text-base font-bold text-white mb-3">{d.title}</h3>
                <p className="text-sm text-white/55 leading-relaxed">{d.description}</p>
              </motion.div>
            )
          })}
        </motion.div>

        {/* Bottom differentiator strip */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-12 glass rounded-2xl p-6 border border-violet-500/10"
        >
          <p className="text-center text-sm text-white/40 mb-4 uppercase tracking-widest text-xs font-semibold">
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
              <span
                key={item}
                className="px-3 py-1.5 rounded-full text-xs font-medium glass border border-white/10 text-white/65"
              >
                ✓ {item}
              </span>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
