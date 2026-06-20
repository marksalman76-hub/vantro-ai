'use client'

import { motion } from 'framer-motion'
import { Brain, RefreshCw, Mic, Lightbulb } from 'lucide-react'

const FEATURES = [
  {
    icon: Brain,
    color: '#7C3AED',
    title: 'Learning Engine',
    description:
      'Processes every interaction, outcome, and feedback signal to identify patterns and update its behaviour model in real time.',
  },
  {
    icon: RefreshCw,
    color: '#3B82F6',
    title: 'Continuous Adaptation',
    description:
      'Agents re-calibrate daily. Yesterday\'s edge cases become tomorrow\'s strengths. Performance compounds over time.',
  },
  {
    icon: Mic,
    color: '#EC4899',
    title: 'Voice & Tone Learning',
    description:
      'Studies your brand\'s language, vocabulary, and communication style. By Day 7, agents speak with your voice — not a generic AI voice.',
  },
  {
    icon: Lightbulb,
    color: '#F59E0B',
    title: 'Suggestion Engine',
    description:
      'Agents don\'t just execute — they proactively surface opportunities, inefficiencies, and strategic improvements your team might miss.',
  },
]

const TIMELINE = [
  { label: 'Day 1',    brandMatch: 30, completion: 85, suggestions: 0  },
  { label: 'Week 1',   brandMatch: 65, completion: 94, suggestions: 3  },
  { label: 'Month 1',  brandMatch: 95, completion: 98, suggestions: 12 },
]

const item = {
  hidden: { opacity: 0, y: 28 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' as const } },
}

function ProgressBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="relative h-1.5 bg-white/10 rounded-full overflow-hidden">
      <motion.div
        className="absolute inset-y-0 left-0 rounded-full"
        style={{ background: color }}
        initial={{ width: 0 }}
        whileInView={{ width: `${value}%` }}
        viewport={{ once: true }}
        transition={{ duration: 1.1, ease: 'easeOut', delay: 0.2 }}
      />
    </div>
  )
}

export default function DynamicEvolution() {
  return (
    <section id="evolution" className="section-padding bg-dark">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-violet-500/20 text-violet-300 mb-4">
            Always Improving
          </span>
          <h2 className="section-heading mb-4">
            Agents That <span className="gradient-text">Get Smarter Every Day</span>
          </h2>
          <p className="section-sub">
            Static AI stops improving the moment it deploys. Vantro agents compound — every day of use makes them better.
          </p>
        </motion.div>

        {/* Feature cards */}
        <motion.div
          variants={{ hidden: {}, show: { transition: { staggerChildren: 0.1 } } }}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-60px' }}
          className="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-16"
        >
          {FEATURES.map((f) => {
            const Icon = f.icon
            return (
              <motion.div key={f.title} variants={item} className="glass glass-hover rounded-2xl p-6 flex gap-4">
                <div
                  className="w-11 h-11 rounded-xl flex-shrink-0 flex items-center justify-center mt-0.5"
                  style={{ background: `${f.color}1A`, border: `1px solid ${f.color}40` }}
                >
                  <Icon className="w-5 h-5" style={{ color: f.color }} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white mb-2">{f.title}</h3>
                  <p className="text-sm text-white/55 leading-relaxed">{f.description}</p>
                </div>
              </motion.div>
            )
          })}
        </motion.div>

        {/* Timeline stats */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="glass rounded-2xl p-7 lg:p-10"
        >
          <h3 className="text-lg font-bold text-white mb-8 text-center">
            Performance Over Time
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
            {TIMELINE.map((t, i) => (
              <div key={t.label} className="space-y-5">
                <div
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold"
                  style={{ background: i === 2 ? 'rgba(16,185,129,0.15)' : 'rgba(124,58,237,0.15)', color: i === 2 ? '#10B981' : '#C084FC' }}
                >
                  {t.label}
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-white/45">Brand voice match</span>
                      <span className="text-white font-semibold">{t.brandMatch}%</span>
                    </div>
                    <ProgressBar value={t.brandMatch} color="#EC4899" />
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-white/45">Task completion</span>
                      <span className="text-white font-semibold">{t.completion}%</span>
                    </div>
                    <ProgressBar value={t.completion} color="#7C3AED" />
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-white/45">Suggestions this period</span>
                      <span className="text-white font-semibold">{t.suggestions}</span>
                    </div>
                    <ProgressBar value={(t.suggestions / 12) * 100} color="#F59E0B" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
