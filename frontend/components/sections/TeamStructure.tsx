'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { TrendingUp, MessageCircle, Search, Sparkles, BarChart2, Settings, Plus, X, Check } from 'lucide-react'
import Button from '@/components/Button'

const ALL_AGENTS = [
  { id: 'atlas',  name: 'Atlas',  role: 'Sales',       icon: TrendingUp,   color: '#7C3AED' },
  { id: 'hermes', name: 'Hermes', role: 'Support',     icon: MessageCircle,color: '#06B6D4' },
  { id: 'oracle', name: 'Oracle', role: 'Research',    icon: Search,       color: '#3B82F6' },
  { id: 'muse',   name: 'Muse',   role: 'Marketing',   icon: Sparkles,     color: '#EC4899' },
  { id: 'sage',   name: 'Sage',   role: 'Data',        icon: BarChart2,    color: '#10B981' },
  { id: 'forge',  name: 'Forge',  role: 'Operations',  icon: Settings,     color: '#F59E0B' },
]

const PRESETS = [
  { label: 'Startup',    agents: ['atlas', 'hermes', 'sage']           },
  { label: 'Scale-up',  agents: ['atlas', 'hermes', 'muse', 'sage']   },
  { label: 'Enterprise',agents: ['atlas', 'hermes', 'oracle', 'muse', 'sage', 'forge'] },
]

export default function TeamStructure() {
  const [selected, setSelected] = useState<string[]>(['atlas', 'hermes', 'sage'])

  const toggle = (id: string) =>
    setSelected((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id])

  const applyPreset = (agents: string[]) => setSelected(agents)

  return (
    <section className="section-padding bg-dark-900/60">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-14"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-blue-500/20 text-blue-300 mb-4">
            Team Builder
          </span>
          <h2 className="section-heading mb-4">Build Your Perfect AI Team</h2>
          <p className="section-sub">Select the agents your business needs. Mix and match, or start with a preset.</p>
        </motion.div>

        <div className="grid lg:grid-cols-5 gap-8 items-start">
          {/* Left — builder */}
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="lg:col-span-3 space-y-4"
          >
            {/* Presets */}
            <div className="flex items-center gap-2 flex-wrap mb-6">
              <span className="text-xs text-white/40 mr-1">Presets:</span>
              {PRESETS.map((p) => (
                <button
                  key={p.label}
                  onClick={() => applyPreset(p.agents)}
                  className="px-3 py-1 rounded-full text-xs font-medium glass border border-white/10 hover:border-violet-500/40 text-white/60 hover:text-white transition-all"
                >
                  {p.label}
                </button>
              ))}
            </div>

            {/* Agent toggles */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {ALL_AGENTS.map((a) => {
                const Icon = a.icon
                const on = selected.includes(a.id)
                return (
                  <motion.button
                    key={a.id}
                    onClick={() => toggle(a.id)}
                    whileTap={{ scale: 0.96 }}
                    className="relative rounded-xl p-4 text-left transition-all duration-200"
                    style={{
                      background: on ? `${a.color}18` : 'rgba(255,255,255,0.03)',
                      border: `1px solid ${on ? a.color + '55' : 'rgba(255,255,255,0.08)'}`,
                      boxShadow: on ? `0 4px 20px ${a.color}22` : 'none',
                    }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <Icon className="w-4 h-4" style={{ color: on ? a.color : 'rgba(255,255,255,0.35)' }} />
                      <AnimatePresence>
                        {on && (
                          <motion.span
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0 }}
                            className="w-4 h-4 rounded-full flex items-center justify-center"
                            style={{ background: a.color }}
                          >
                            <Check className="w-2.5 h-2.5 text-white" />
                          </motion.span>
                        )}
                        {!on && (
                          <Plus className="w-3.5 h-3.5 text-white/25" />
                        )}
                      </AnimatePresence>
                    </div>
                    <p className="text-sm font-semibold" style={{ color: on ? '#fff' : 'rgba(255,255,255,0.5)' }}>
                      {a.name}
                    </p>
                    <p className="text-xs" style={{ color: on ? a.color : 'rgba(255,255,255,0.3)' }}>
                      {a.role}
                    </p>
                  </motion.button>
                )
              })}
            </div>
          </motion.div>

          {/* Right — summary */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="lg:col-span-2 glass rounded-2xl p-6"
          >
            <h3 className="text-base font-semibold text-white mb-4">
              Your Team
              <span className="ml-2 text-xs font-normal text-white/40">({selected.length} agents)</span>
            </h3>

            <div className="space-y-2 mb-6 min-h-[120px]">
              <AnimatePresence mode="popLayout">
                {selected.length === 0 && (
                  <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-sm text-white/30 py-4 text-center">
                    Select at least one agent
                  </motion.p>
                )}
                {ALL_AGENTS.filter((a) => selected.includes(a.id)).map((a) => {
                  const Icon = a.icon
                  return (
                    <motion.div
                      key={a.id}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      layout
                      className="flex items-center justify-between py-2 px-3 rounded-lg"
                      style={{ background: `${a.color}12`, border: `1px solid ${a.color}25` }}
                    >
                      <div className="flex items-center gap-2">
                        <Icon className="w-3.5 h-3.5" style={{ color: a.color }} />
                        <span className="text-sm text-white">{a.name}</span>
                        <span className="text-xs text-white/40">{a.role}</span>
                      </div>
                      <button onClick={() => toggle(a.id)} className="text-white/30 hover:text-white/70 transition-colors">
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>

            <div className="border-t border-white/[0.07] pt-4 mb-5 space-y-2 text-sm">
              <div className="flex justify-between text-white/50">
                <span>Estimated hours saved/week</span>
                <span className="text-white font-medium">{(selected.length * 18).toFixed(0)}h</span>
              </div>
              <div className="flex justify-between text-white/50">
                <span>Tasks automated / month</span>
                <span className="text-white font-medium">{(selected.length * 2400).toLocaleString()}</span>
              </div>
            </div>

            <Button
              variant="primary"
              size="md"
              className="w-full"
              disabled={selected.length === 0}
            >
              Deploy This Team
            </Button>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
