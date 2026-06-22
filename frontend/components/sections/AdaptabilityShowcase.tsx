'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { TrendingUp, MessageCircle, BarChart2 } from 'lucide-react'

type IndustryKey = 'all' | 'saas' | 'ecommerce' | 'healthcare' | 'finance' | 'realestate' | 'education'

const FILTERS: { id: IndustryKey; label: string }[] = [
  { id: 'all',        label: 'All'          },
  { id: 'saas',       label: 'SaaS'         },
  { id: 'ecommerce',  label: 'E-commerce'   },
  { id: 'healthcare', label: 'Healthcare'   },
  { id: 'finance',    label: 'Finance'      },
  { id: 'realestate', label: 'Real Estate'  },
  { id: 'education',  label: 'Education'    },
]

interface Case {
  industry: IndustryKey
  headline: string
  description: string
  agents: string[]
  agentColors: string[]
  stats: { label: string; value: string }[]
  quote: string
  quoteAuthor: string
  color: string
  glow: string
}

const CASES: Case[] = [
  {
    industry: 'saas',
    headline: 'Cut churn by 34%',
    description: 'Atlas qualifies trials into paid plans. Hermes handles tier-1 support, freeing your CS team for expansion conversations.',
    agents: ['Atlas', 'Hermes'],
    agentColors: ['#7C3AED', '#06B6D4'],
    stats: [
      { label: 'Churn reduction', value: '34%' },
      { label: 'Trial → Paid',    value: '+58%' },
      { label: 'Tickets automated', value: '73%' },
    ],
    quote: 'Our support team went from firefighting to proactively growing accounts.',
    quoteAuthor: 'VP Customer Success, TechFlow',
    color: '#7C3AED',
    glow: 'rgba(124,58,237,0.15)',
  },
  {
    industry: 'ecommerce',
    headline: 'AOV up 21% in 60 days',
    description: 'Forge automates fulfilment ops. Atlas runs personalised upsell and post-purchase flows that feel human.',
    agents: ['Forge', 'Atlas'],
    agentColors: ['#F59E0B', '#7C3AED'],
    stats: [
      { label: 'AOV increase',    value: '+21%' },
      { label: 'Order processing', value: '48 h→0.5 h' },
      { label: 'Return rate',     value: '-18%' },
    ],
    quote: 'Forge handles our entire order pipeline. We haven\'t touched it in weeks.',
    quoteAuthor: 'COO, Luminos Commerce',
    color: '#F59E0B',
    glow: 'rgba(245,158,11,0.15)',
  },
  {
    industry: 'healthcare',
    headline: '99% appointment accuracy',
    description: 'Hermes manages patient intake, reminders, and FAQ resolution. Sage surfaces clinical schedule insights for ops teams.',
    agents: ['Hermes', 'Sage'],
    agentColors: ['#06B6D4', '#10B981'],
    stats: [
      { label: 'Intake time',     value: '-30%'  },
      { label: 'No-show rate',    value: '-42%'  },
      { label: 'Query resolution', value: '94%' },
    ],
    quote: 'Patient satisfaction scores hit an all-time high the month we deployed Hermes.',
    quoteAuthor: 'Ops Director, ClearPath Health',
    color: '#06B6D4',
    glow: 'rgba(6,182,212,0.15)',
  },
  {
    industry: 'finance',
    headline: '5× faster regulatory reporting',
    description: 'Oracle scours filings and market data in real time. Sage compiles reports that would take analysts days in minutes.',
    agents: ['Oracle', 'Sage'],
    agentColors: ['#3B82F6', '#10B981'],
    stats: [
      { label: 'Report time',       value: '5× faster' },
      { label: 'Data sources scanned', value: '1,200+' },
      { label: 'Analyst hours saved', value: '80/mo' },
    ],
    quote: 'Oracle replaced three junior research analysts and delivers better insights at 2 AM.',
    quoteAuthor: 'CIO, Meridian Capital',
    color: '#3B82F6',
    glow: 'rgba(59,130,246,0.15)',
  },
  {
    industry: 'realestate',
    headline: '120 qualified leads / week',
    description: 'Atlas runs inbound qualification and outbound prospecting simultaneously. Hermes nurtures leads who aren\'t yet ready to buy.',
    agents: ['Atlas', 'Hermes'],
    agentColors: ['#7C3AED', '#06B6D4'],
    stats: [
      { label: 'Qualified leads/week', value: '120'  },
      { label: 'Sales cycle',         value: '-40%'  },
      { label: 'Agent time on admin', value: '-65%'  },
    ],
    quote: 'Atlas works the pipeline while I\'m showing properties. I never miss a hot lead anymore.',
    quoteAuthor: 'Principal Agent, Apex Realty',
    color: '#EC4899',
    glow: 'rgba(236,72,153,0.15)',
  },
  {
    industry: 'education',
    headline: '3× enrolment conversion',
    description: 'Hermes handles prospective student queries 24/7. Muse runs personalised nurture sequences that convert inquiries to applications.',
    agents: ['Hermes', 'Muse'],
    agentColors: ['#06B6D4', '#EC4899'],
    stats: [
      { label: 'Enrolment rate',  value: '3×'    },
      { label: 'Avg response time', value: '< 1 min' },
      { label: 'Staff hours freed', value: '45/wk' },
    ],
    quote: 'Students get instant answers at midnight. Our enrolment team gets to do strategy.',
    quoteAuthor: 'Director of Admissions, Northgate Academy',
    color: '#10B981',
    glow: 'rgba(16,185,129,0.15)',
  },
]

export default function AdaptabilityShowcase() {
  const [active, setActive] = useState<IndustryKey>('all')

  const visible = active === 'all' ? CASES : CASES.filter((c) => c.industry === active)

  return (
    <section
      id="adaptability"
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #070D1F 0%, #080D1E 100%)' }}
    >
      <div className="absolute inset-0 mesh-grid opacity-35 pointer-events-none" />
      <div className="absolute top-0 right-0 w-[500px] h-[400px] bg-cyan-500/06 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="text-center mb-12"
        >
          <span className="section-badge-cyan mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            Industry Adaptability
          </span>
          <h2 className="section-heading mt-4 mb-4">
            Works Wherever <span className="gradient-text">You Work</span>
          </h2>
          <p className="section-sub mt-2">
            No re-training, no new configuration. Vantro agents recognise your industry and adapt automatically.
          </p>
        </motion.div>

        {/* Filters */}
        <div className="flex flex-wrap justify-center gap-2 mb-10">
          {FILTERS.map((f) => (
            <motion.button
              key={f.id}
              onClick={() => setActive(f.id)}
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-200 ${
                active === f.id
                  ? 'bg-violet-600 text-white shadow-[0_4px_20px_rgba(124,58,237,0.45)]'
                  : 'glass-strong border border-white/10 text-white/50 hover:text-white hover:border-white/20'
              }`}
            >
              {f.label}
            </motion.button>
          ))}
        </div>

        {/* Case cards */}
        <motion.div layout className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <AnimatePresence mode="popLayout">
            {visible.map((c) => (
              <motion.div
                key={c.industry}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ type: 'spring', stiffness: 200, damping: 22 }}
                whileHover={{ y: -4, scale: 1.01 }}
                className="glass-ultra rounded-2xl p-6 flex flex-col"
                style={{ border: `1px solid ${c.color}22`, boxShadow: `0 8px 40px ${c.glow}` }}
              >
                {/* Headline + agents */}
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-xl font-bold text-white leading-tight">{c.headline}</h3>
                  <div className="flex -space-x-1.5 ml-3 flex-shrink-0">
                    {c.agentColors.map((col, i) => (
                      <div
                        key={i}
                        className="w-7 h-7 rounded-full border-2 border-dark"
                        style={{ background: col }}
                        title={c.agents[i]}
                      />
                    ))}
                  </div>
                </div>

                <p className="text-sm text-white/55 leading-relaxed mb-5">{c.description}</p>

                {/* Stat badges */}
                <div className="grid grid-cols-3 gap-2 mb-5">
                  {c.stats.map((s) => (
                    <div key={s.label} className="rounded-lg p-2.5 text-center" style={{ background: `${c.color}12` }}>
                      <p className="text-sm font-bold" style={{ color: c.color }}>{s.value}</p>
                      <p className="text-[10px] text-white/40 mt-0.5 leading-tight">{s.label}</p>
                    </div>
                  ))}
                </div>

                {/* Quote */}
                <div className="mt-auto pt-4 border-t border-white/[0.07]">
                  <p className="text-xs text-white/60 italic leading-relaxed mb-1">&ldquo;{c.quote}&rdquo;</p>
                  <p className="text-[10px] text-white/35">— {c.quoteAuthor}</p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      </div>
    </section>
  )
}

