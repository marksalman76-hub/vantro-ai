'use client'

import { motion } from 'framer-motion'
import { Plug, Settings, Zap, TrendingUp } from 'lucide-react'

const STEPS = [
  {
    num: '01',
    icon: Plug,
    color: '#C084FC',
    bg: '#7C3AED',
    title: 'Connect Your Tools',
    body: 'Link Vantro to your existing stack in minutes. 1,000+ pre-built connectors for CRMs, helpdesks, databases, and APIs — no engineering needed.',
    accent: 'rgba(124,58,237,0.15)',
  },
  {
    num: '02',
    icon: Settings,
    color: '#93C5FD',
    bg: '#3B82F6',
    title: 'Configure Your Workflows',
    body: 'Define objectives, set guardrails, and personalise agent behaviour through our visual builder. No code — just natural language instructions.',
    accent: 'rgba(59,130,246,0.15)',
  },
  {
    num: '03',
    icon: Zap,
    color: '#67E8F9',
    bg: '#06B6D4',
    title: 'Deploy Your Agents',
    body: 'Flip the switch. Agents go live instantly and start executing tasks across every connected tool, channel, and workflow in real time.',
    accent: 'rgba(6,182,212,0.15)',
  },
  {
    num: '04',
    icon: TrendingUp,
    color: '#6EE7B7',
    bg: '#10B981',
    title: 'Monitor & Optimise',
    body: 'Watch your agents work from the live dashboard. Track tasks completed, time saved, and outcomes achieved. Fine-tune with one click.',
    accent: 'rgba(16,185,129,0.15)',
  },
]

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #080D1E 0%, #070D1F 100%)' }}
    >
      <div className="absolute inset-0 mesh-grid opacity-30 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-cyan-500/07 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="text-center mb-20"
        >
          <span className="section-badge-cyan mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            Simple by Design
          </span>
          <h2 className="section-heading mt-4 mb-4">
            From Zero to Autonomous{' '}
            <span className="gradient-text-cyan">in 4 Steps</span>
          </h2>
          <p className="section-sub mt-2">No MLOps team needed. No months of setup. Just connect, configure, and go.</p>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Vertical connector line */}
          <div className="hidden lg:block absolute left-1/2 -translate-x-px top-8 bottom-8 w-px overflow-hidden">
            <motion.div
              initial={{ scaleY: 0 }}
              whileInView={{ scaleY: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
              style={{ originY: 0 }}
              className="w-full h-full"
              aria-hidden="true"
            >
              <div className="w-full h-full bg-gradient-to-b from-violet-500/50 via-cyan-500/40 to-emerald-500/40" />
            </motion.div>
          </div>

          <div className="space-y-0">
            {STEPS.map((step, i) => {
              const Icon = step.icon
              const isLeft = i % 2 === 0
              return (
                <motion.div
                  key={step.num}
                  initial={{ opacity: 0, x: isLeft ? -40 : 40 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{ type: 'spring', stiffness: 160, damping: 22, delay: i * 0.12 }}
                  className={`relative flex flex-col lg:flex-row items-center gap-8 lg:gap-0 mb-12 lg:mb-16 ${
                    isLeft ? 'lg:flex-row' : 'lg:flex-row-reverse'
                  }`}
                >
                  {/* Content card */}
                  <div className={`w-full lg:w-[46%] ${isLeft ? 'lg:pr-14' : 'lg:pl-14'}`}>
                    <motion.div
                      whileHover={{ y: -4, scale: 1.01 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                      className="relative glass-ultra rounded-2xl p-7 group overflow-hidden"
                      style={{ border: `1px solid ${step.bg}20` }}
                    >
                      {/* Top shine */}
                      <div
                        className="absolute top-0 left-6 right-6 h-px opacity-70"
                        style={{ background: `linear-gradient(90deg, transparent, ${step.color}50, transparent)` }}
                      />

                      {/* Background accent */}
                      <div
                        className="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"
                        style={{ background: step.accent }}
                      />

                      <div className="relative">
                        <div className="flex items-center gap-4 mb-5">
                          <div
                            className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-300 group-hover:scale-110"
                            style={{
                              background: `${step.bg}18`,
                              border: `1px solid ${step.bg}35`,
                              boxShadow: `0 0 20px ${step.bg}20`,
                            }}
                          >
                            <Icon className="w-6 h-6" style={{ color: step.color }} />
                          </div>
                          <div
                            className="text-xs font-black tracking-[0.2em] px-3 py-1 rounded-full"
                            style={{ color: step.color, background: `${step.bg}15` }}
                          >
                            STEP {step.num}
                          </div>
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                        <p className="text-sm text-white/50 leading-relaxed">{step.body}</p>
                      </div>
                    </motion.div>
                  </div>

                  {/* Centre node */}
                  <div className="hidden lg:flex w-[8%] justify-center z-10">
                    <motion.div
                      initial={{ scale: 0, opacity: 0 }}
                      whileInView={{ scale: 1, opacity: 1 }}
                      viewport={{ once: true }}
                      transition={{ type: 'spring', stiffness: 300, damping: 20, delay: i * 0.12 + 0.2 }}
                      className="relative"
                    >
                      {/* Pulse ring */}
                      <div
                        className="absolute -inset-2 rounded-full opacity-30 animate-ping"
                        style={{ background: step.bg, animationDuration: '2s', animationDelay: `${i * 0.5}s` }}
                      />
                      <div
                        className="relative z-10 w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white"
                        style={{
                          background: `linear-gradient(135deg, ${step.bg}, ${step.bg}88)`,
                          boxShadow: `0 0 24px ${step.bg}60, 0 0 48px ${step.bg}20`,
                        }}
                      >
                        {step.num}
                      </div>
                    </motion.div>
                  </div>

                  {/* Empty half */}
                  <div className="hidden lg:block lg:w-[46%]" />
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
