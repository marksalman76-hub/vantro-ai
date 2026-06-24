'use client'

import { motion } from 'framer-motion'
import { Brain, Globe2, Users, BarChart3, Shield, Zap } from 'lucide-react'

const FEATURES = [
  {
    icon:  Brain,
    color: '#C084FC',
    bg:    '#7C3AED',
    title: 'Autonomous Execution',
    description:
      'Agents complete full multi-step workflows end-to-end — from research and decision-making through to action — with no human hand-holding required.',
    large: true,
  },
  {
    icon:  Zap,
    color: '#FCD34D',
    bg:    '#D97706',
    title: 'Deploy in Hours, Not Months',
    description:
      'No MLOps team required. Connect your existing tools, configure in natural language, and go live the same day. Agents are production-ready on Day 1.',
    large: true,
  },
  {
    icon:  Globe2,
    color: '#67E8F9',
    bg:    '#06B6D4',
    title: 'Multi-Channel Ops',
    description:
      'Deploy across email, chat, voice, CRM, and 1,000+ tools simultaneously. One agent team, every channel, always on.',
    large: false,
  },
  {
    icon:  Users,
    color: '#93C5FD',
    bg:    '#3B82F6',
    title: 'Human-in-the-Loop',
    description:
      'Set approval gates for high-stakes decisions. Agents escalate intelligently with full context, never overstepping their guardrails.',
    large: false,
  },
  {
    icon:  Shield,
    color: '#F9A8D4',
    bg:    '#EC4899',
    title: 'Enterprise Security',
    description:
      'SOC 2 Type II certified, GDPR-ready, with fine-grained RBAC, full audit logs, and data residency options.',
    large: false,
  },
  {
    icon:  BarChart3,
    color: '#6EE7B7',
    bg:    '#10B981',
    title: 'Real-Time Analytics',
    description:
      'Live dashboards surface tasks completed, time saved, revenue influenced, and agent health — so you always know what your AI workforce is delivering.',
    wide: true,
  },
]

export default function Features() {
  const largeFt  = FEATURES.filter(f => f.large)
  const midFt    = FEATURES.filter(f => !f.large && !f.wide)
  const wideFt   = FEATURES.filter(f => f.wide)

  return (
    <section id="features" className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #080D1E 0%, #070D1F 100%)' }}>

      <div className="absolute inset-0 mesh-grid-fine opacity-30 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] rounded-full blur-[140px] opacity-10 pointer-events-none"
        style={{ background: 'radial-gradient(ellipse, #7C3AED, transparent)' }} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 180, damping: 22 }}
          className="text-center mb-16"
        >
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide mb-5"
            style={{ background: 'rgba(124,58,237,0.12)', border: '1px solid rgba(124,58,237,0.28)', color: '#C084FC' }}>
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
            Built for Autonomous Scale
          </span>
          <h2 className="section-heading mt-4 mb-4">
            Everything your AI workforce{' '}
            <span className="gradient-text">needs to perform</span>
          </h2>
          <p className="section-sub mt-2">
            Purpose-built for autonomous operation across every department, channel, and workflow.
          </p>
        </motion.div>

        {/* Bento grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-5">

          {/* Large cards (row 1) */}
          {largeFt.map((f, i) => {
            const Icon = f.icon
            return (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 28 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ type: 'spring', stiffness: 160, damping: 22, delay: i * 0.08 }}
                whileHover={{ y: -5, transition: { type: 'spring', stiffness: 400, damping: 25 } }}
                className={`relative group glass-ultra rounded-2xl p-8 overflow-hidden cursor-default ${
                  i === 0 ? 'md:col-span-7' : 'md:col-span-5'
                }`}
                style={{ border: `1px solid ${f.bg}20`, minHeight: '240px' }}
              >
                {/* Hover radial glow */}
                <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                  style={{ background: `radial-gradient(ellipse at 20% 20%, ${f.bg}20 0%, transparent 65%)` }} />
                <div className="absolute top-0 left-6 right-6 h-px opacity-60"
                  style={{ background: `linear-gradient(90deg, transparent, ${f.color}45, transparent)` }} />

                {/* Icon — larger on big cards */}
                <div className="relative w-16 h-16 rounded-2xl flex items-center justify-center mb-6 transition-transform duration-300 group-hover:scale-110"
                  style={{ background: `${f.bg}18`, border: `1px solid ${f.bg}30`, boxShadow: `0 0 30px ${f.bg}18` }}>
                  <Icon className="w-7 h-7" style={{ color: f.color }} />
                </div>

                <h3 className="text-xl font-bold text-white mb-3">{f.title}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{f.description}</p>

                {/* Decorative corner accent */}
                <div className="absolute bottom-0 right-0 w-32 h-32 rounded-tl-[80px] opacity-[0.04] pointer-events-none"
                  style={{ background: f.bg }} />
              </motion.div>
            )
          })}

          {/* Mid cards (row 2) — 3 equal columns */}
          {midFt.map((f, i) => {
            const Icon = f.icon
            return (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ type: 'spring', stiffness: 180, damping: 22, delay: 0.15 + i * 0.07 }}
                whileHover={{ y: -4, transition: { type: 'spring', stiffness: 400, damping: 25 } }}
                className="relative group glass-ultra rounded-2xl p-6 overflow-hidden cursor-default md:col-span-4"
                style={{ border: `1px solid ${f.bg}18` }}
              >
                <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                  style={{ background: `radial-gradient(ellipse at 20% 20%, ${f.bg}18 0%, transparent 65%)` }} />
                <div className="absolute top-0 left-6 right-6 h-px opacity-60"
                  style={{ background: `linear-gradient(90deg, transparent, ${f.color}45, transparent)` }} />

                <div className="relative w-12 h-12 rounded-xl flex items-center justify-center mb-5 transition-transform duration-300 group-hover:scale-110"
                  style={{ background: `${f.bg}18`, border: `1px solid ${f.bg}30`, boxShadow: `0 0 20px ${f.bg}15` }}>
                  <Icon className="w-5 h-5" style={{ color: f.color }} />
                </div>

                <h3 className="text-base font-bold text-white mb-2.5">{f.title}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{f.description}</p>
              </motion.div>
            )
          })}

          {/* Wide card (row 3) — full width, horizontal layout */}
          {wideFt.map((f) => {
            const Icon = f.icon
            return (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ type: 'spring', stiffness: 160, damping: 22, delay: 0.28 }}
                whileHover={{ y: -3, transition: { type: 'spring', stiffness: 400, damping: 25 } }}
                className="relative group glass-ultra rounded-2xl p-7 overflow-hidden cursor-default md:col-span-12"
                style={{ border: `1px solid ${f.bg}18` }}
              >
                <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                  style={{ background: `radial-gradient(ellipse at 10% 50%, ${f.bg}15 0%, transparent 60%)` }} />
                <div className="absolute top-0 left-6 right-6 h-px opacity-60"
                  style={{ background: `linear-gradient(90deg, transparent, ${f.color}45, transparent)` }} />

                <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
                  {/* Left */}
                  <div className="flex items-start gap-5 flex-1 min-w-0">
                    <div className="relative w-14 h-14 rounded-2xl flex-shrink-0 flex items-center justify-center transition-transform duration-300 group-hover:scale-110"
                      style={{ background: `${f.bg}18`, border: `1px solid ${f.bg}30`, boxShadow: `0 0 24px ${f.bg}15` }}>
                      <Icon className="w-6 h-6" style={{ color: f.color }} />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">{f.title}</h3>
                      <p className="text-sm text-white/50 leading-relaxed max-w-xl">{f.description}</p>
                    </div>
                  </div>

                  {/* Right: mini bar chart decoration */}
                  <div className="flex items-end gap-1.5 shrink-0 h-12 opacity-60 group-hover:opacity-100 transition-opacity duration-500">
                    {[40, 65, 55, 80, 70, 95, 85, 100, 90, 100].map((h, i) => (
                      <div
                        key={i}
                        className="w-2.5 rounded-sm transition-all duration-300"
                        style={{
                          height: `${h}%`,
                          background: `linear-gradient(180deg, ${f.color} 0%, ${f.bg}80 100%)`,
                          animationDelay: `${i * 0.05}s`,
                        }}
                      />
                    ))}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
