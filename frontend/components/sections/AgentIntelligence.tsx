'use client'

import { motion } from 'framer-motion'
import { X, Check } from 'lucide-react'
import Button from '@/components/Button'

const ROWS = [
  {
    label: 'Response type',
    generic: 'Executes commands only',
    vantro: 'Strategic partner + proactive executor',
  },
  {
    label: 'Industry knowledge',
    generic: 'Generic, one-size-fits-all responses',
    vantro: 'Industry-trained specialist agents',
  },
  {
    label: 'Learning',
    generic: 'Static — same performance Day 1 to Day 365',
    vantro: '+40% improvement by Month 1, compounds daily',
  },
  {
    label: 'Brand voice',
    generic: 'Robotic, generic tone',
    vantro: 'Matches your exact brand voice within 7 days',
  },
  {
    label: 'Suggestions',
    generic: 'None — waits for commands',
    vantro: 'Proactively surfaces improvements & opportunities',
  },
  {
    label: 'Team coordination',
    generic: 'Operates in isolation',
    vantro: 'Full team orchestration across functions',
  },
  {
    label: 'Setup time',
    generic: 'Weeks of configuration',
    vantro: 'Deploy in under 10 minutes',
  },
]

const item = {
  hidden: { opacity: 0, y: 16 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' as const } },
}

export default function AgentIntelligence() {
  return (
    <section id="comparison" className="section-padding bg-dark-900/70">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-14"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-pink-500/20 text-pink-300 mb-4">
            Why Vantro Wins
          </span>
          <h2 className="section-heading mb-4">
            Vantro vs Generic AI
          </h2>
          <p className="section-sub">
            Generic AI tools are command-executers. Vantro agents are strategic partners — the difference shows up in your bottom line.
          </p>
        </motion.div>

        {/* Comparison table */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="glass rounded-2xl overflow-hidden border border-white/[0.08]"
        >
          {/* Header */}
          <div className="grid grid-cols-3 border-b border-white/[0.08]">
            <div className="px-5 py-4 text-xs font-semibold text-white/35 uppercase tracking-widest">Feature</div>
            <div className="px-5 py-4 border-l border-white/[0.08] bg-red-500/[0.04]">
              <p className="text-sm font-bold text-red-400/80">Generic AI</p>
              <p className="text-xs text-white/35">ChatGPT plugins, basic automation</p>
            </div>
            <div className="px-5 py-4 border-l border-white/[0.08] bg-violet-500/[0.06]">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
                <p className="text-sm font-bold text-violet-300">Vantro</p>
              </div>
              <p className="text-xs text-white/35">Adaptive AI agent platform</p>
            </div>
          </div>

          {/* Rows */}
          <motion.div
            variants={{ hidden: {}, show: { transition: { staggerChildren: 0.07 } } }}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
          >
            {ROWS.map((row, i) => (
              <motion.div
                key={row.label}
                variants={item}
                className={`grid grid-cols-3 border-b border-white/[0.05] last:border-0 ${
                  i % 2 === 0 ? '' : 'bg-white/[0.015]'
                }`}
              >
                <div className="px-5 py-4 text-sm text-white/55 flex items-center">{row.label}</div>

                {/* Generic */}
                <div className="px-5 py-4 border-l border-white/[0.05] bg-red-500/[0.02]">
                  <div className="flex items-start gap-2">
                    <X className="w-4 h-4 text-red-400/60 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-white/45">{row.generic}</span>
                  </div>
                </div>

                {/* Vantro */}
                <div className="px-5 py-4 border-l border-white/[0.05] bg-violet-500/[0.03]">
                  <div className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-violet-400 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-white font-medium">{row.vantro}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-center mt-10"
        >
          <Button variant="primary" size="lg" arrow>
            See the Difference Live
          </Button>
          <p className="text-xs text-white/35 mt-3">Book a 15-minute side-by-side demo</p>
        </motion.div>
      </div>
    </section>
  )
}
