'use client'

import { motion } from 'framer-motion'
import { Plug, Settings, Zap, TrendingUp } from 'lucide-react'

const STEPS = [
  {
    num: '01',
    icon: Plug,
    color: '#7C3AED',
    title: 'Connect Your Tools',
    body: 'Link Vantro to your existing stack in minutes. 1,000+ pre-built connectors for CRMs, helpdesks, databases, and APIs — no engineering needed.',
  },
  {
    num: '02',
    icon: Settings,
    color: '#3B82F6',
    title: 'Configure Your Workflows',
    body: 'Define objectives, set guardrails, and personalise agent behaviour through our visual builder. No code — just natural language instructions.',
  },
  {
    num: '03',
    icon: Zap,
    color: '#06B6D4',
    title: 'Deploy Your Agents',
    body: 'Flip the switch. Agents go live instantly and start executing tasks across every connected tool, channel, and workflow in real time.',
  },
  {
    num: '04',
    icon: TrendingUp,
    color: '#10B981',
    title: 'Monitor & Optimise',
    body: 'Watch your agents work from the live dashboard. Track tasks completed, time saved, and outcomes achieved. Fine-tune with one click.',
  },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="section-padding bg-dark">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-cyan-500/20 text-cyan-300 mb-4">
            Simple by Design
          </span>
          <h2 className="section-heading mb-4">From Zero to Autonomous in 4 Steps</h2>
          <p className="section-sub">No MLOps team needed. No months of setup. Just connect, configure, and go.</p>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Vertical connector line (desktop) */}
          <div className="hidden lg:block absolute left-1/2 -translate-x-px top-12 bottom-12 w-px bg-gradient-to-b from-violet-500/40 via-blue-500/30 to-green-500/30" />

          <div className="space-y-16 lg:space-y-0">
            {STEPS.map((step, i) => {
              const Icon = step.icon
              const isLeft = i % 2 === 0
              return (
                <motion.div
                  key={step.num}
                  initial={{ opacity: 0, x: isLeft ? -32 : 32 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{ duration: 0.65, delay: i * 0.1, ease: [0.25, 0.1, 0.25, 1] }}
                  className={`relative flex flex-col lg:flex-row items-center gap-8 lg:gap-0 ${
                    isLeft ? 'lg:flex-row' : 'lg:flex-row-reverse'
                  } mb-12 lg:mb-20`}
                >
                  {/* Content card */}
                  <div className={`lg:w-[46%] ${isLeft ? 'lg:pr-12' : 'lg:pl-12'}`}>
                    <div className="glass glass-hover rounded-2xl p-6 lg:p-8">
                      <div
                        className="w-12 h-12 rounded-xl flex items-center justify-center mb-5"
                        style={{ background: `${step.color}20`, border: `1px solid ${step.color}45` }}
                      >
                        <Icon className="w-6 h-6" style={{ color: step.color }} />
                      </div>
                      <div className="text-xs font-bold text-white/25 tracking-widest mb-2">{step.num}</div>
                      <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                      <p className="text-sm text-white/55 leading-relaxed">{step.body}</p>
                    </div>
                  </div>

                  {/* Centre node */}
                  <div className="hidden lg:flex w-[8%] justify-center">
                    <motion.div
                      initial={{ scale: 0 }}
                      whileInView={{ scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.4, delay: i * 0.1 + 0.2 }}
                      className="relative z-10 w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold text-white"
                      style={{
                        background: `linear-gradient(135deg, ${step.color}, ${step.color}88)`,
                        boxShadow: `0 0 24px ${step.color}55`,
                      }}
                    >
                      {step.num}
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
