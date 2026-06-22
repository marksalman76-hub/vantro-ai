'use client'

import { useState, useRef } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { TrendingUp, MessageCircle, Search, Sparkles, BarChart2, Settings, Check, ChevronRight } from 'lucide-react'
import Button from '@/components/Button'
import SearchComponent from '@/components/ui/animated-glowing-search-bar'

type GlowColor = 'blue' | 'purple' | 'green' | 'red' | 'orange'

const AGENTS = [
  {
    name: 'Atlas',
    role: 'Sales Agent',
    description: 'Qualifies leads, books meetings, and nurtures pipeline 24/7 without manual intervention.',
    color: '#7C3AED',
    colorLight: '#C084FC',
    glowColor: 'purple' as GlowColor,
    icon: TrendingUp,
    capabilities: ['Lead scoring & qualification', 'Personalised email sequences', 'CRM auto-sync (Salesforce / HubSpot)', 'Meeting booking & follow-up'],
    stat: '23 leads now',
    statColor: '#22c55e',
  },
  {
    name: 'Hermes',
    role: 'Support Agent',
    description: 'Resolves customer issues instantly across chat, email, and voice channels around the clock.',
    color: '#06B6D4',
    colorLight: '#67E8F9',
    glowColor: 'blue' as GlowColor,
    icon: MessageCircle,
    capabilities: ['Intelligent ticket routing', 'FAQ & knowledge-base automation', 'Sentiment analysis & escalation', 'Multi-channel (Intercom / Zendesk)'],
    stat: '47 tickets/hr',
    statColor: '#22c55e',
  },
  {
    name: 'Oracle',
    role: 'Research Agent',
    description: 'Gathers competitive intelligence, summarises industry trends, and delivers actionable reports.',
    color: '#3B82F6',
    colorLight: '#93C5FD',
    glowColor: 'blue' as GlowColor,
    icon: Search,
    capabilities: ['Real-time web research', 'Automated report generation', 'Structured data extraction', 'Trend & competitor analysis'],
    stat: '1,200+ sources',
    statColor: '#3B82F6',
  },
  {
    name: 'Muse',
    role: 'Marketing Agent',
    description: 'Creates SEO-optimised content, schedules posts, and runs A/B tests at scale.',
    color: '#EC4899',
    colorLight: '#F9A8D4',
    glowColor: 'red' as GlowColor,
    icon: Sparkles,
    capabilities: ['Long-form & social content', 'SEO optimisation', 'Multi-platform scheduling', 'A/B copy testing'],
    stat: '3× content output',
    statColor: '#EC4899',
  },
  {
    name: 'Sage',
    role: 'Data Agent',
    description: 'Transforms raw data into live dashboards, anomaly alerts, and predictive insights.',
    color: '#10B981',
    colorLight: '#6EE7B7',
    glowColor: 'green' as GlowColor,
    icon: BarChart2,
    capabilities: ['Pipeline data analysis', 'Interactive dashboards', 'Anomaly & outlier detection', 'Predictive trend modelling'],
    stat: '99.8% accuracy',
    statColor: '#10B981',
  },
  {
    name: 'Forge',
    role: 'Operations Agent',
    description: 'Automates multi-step workflows across every tool in your stack without writing code.',
    color: '#F59E0B',
    colorLight: '#FCD34D',
    glowColor: 'orange' as GlowColor,
    icon: Settings,
    capabilities: ['No-code workflow builder', 'Cross-tool API orchestration', 'Error handling & retries', 'Process speed optimisation'],
    stat: '23 workflows live',
    statColor: '#F59E0B',
  },
]

function AgentCard({ agent, index }: { agent: typeof AGENTS[0]; index: number }) {
  const ref = useRef<HTMLDivElement>(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [8, -8]), { stiffness: 500, damping: 35 })
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-8, 8]), { stiffness: 500, damping: 35 })
  const glowX = useTransform(x, [-0.5, 0.5], [0, 100])
  const glowY = useTransform(y, [-0.5, 0.5], [0, 100])
  const Icon = agent.icon

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 36, scale: 0.95 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ type: 'spring', stiffness: 200, damping: 22, delay: index * 0.08 }}
      onMouseMove={(e) => {
        const rect = ref.current?.getBoundingClientRect()
        if (!rect) return
        x.set((e.clientX - rect.left) / rect.width - 0.5)
        y.set((e.clientY - rect.top) / rect.height - 0.5)
      }}
      onMouseLeave={() => { x.set(0); y.set(0) }}
      style={{ rotateX, rotateY, transformPerspective: 900 }}
      className="relative group"
    >
      {/* Dynamic hover glow */}
      <motion.div
        className="absolute -inset-px rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-400 pointer-events-none"
        style={{
          background: `radial-gradient(circle at ${glowX}% ${glowY}%, ${agent.color}25 0%, transparent 60%)`,
        }}
      />

      {/* Border glow on hover */}
      <div
        className="absolute -inset-px rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
        style={{ boxShadow: `0 0 30px ${agent.color}20, inset 0 0 30px ${agent.color}05` }}
      />

      <div
        className="relative flex flex-col h-full glass-ultra rounded-2xl p-5"
        style={{ border: `1px solid ${agent.color}18` }}
      >
        {/* Top shine */}
        <div
          className="absolute top-0 left-4 right-4 h-px opacity-60"
          style={{ background: `linear-gradient(90deg, transparent, ${agent.colorLight}40, transparent)` }}
        />

        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div
            className="w-11 h-11 rounded-xl flex-shrink-0 flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg"
            style={{
              background: `${agent.color}18`,
              border: `1px solid ${agent.color}35`,
              boxShadow: `0 0 20px ${agent.color}15`,
            }}
          >
            <Icon className="w-5 h-5" style={{ color: agent.colorLight }} />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white leading-none">{agent.name}</h3>
              <div className="flex items-center gap-1 text-[10px] font-semibold" style={{ color: agent.statColor }}>
                <div className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                {agent.stat}
              </div>
            </div>
            <span
              className="text-[10px] font-bold px-2 py-0.5 rounded-full mt-1 inline-block leading-none tracking-wide"
              style={{ background: `${agent.color}18`, color: agent.colorLight }}
            >
              {agent.role}
            </span>
          </div>
        </div>

        <p className="text-xs text-white/50 leading-relaxed mb-4">{agent.description}</p>

        <ul className="space-y-2 flex-1">
          {agent.capabilities.map((cap) => (
            <li key={cap} className="flex items-start gap-2 text-xs text-white/55">
              <Check className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style={{ color: agent.colorLight }} />
              {cap}
            </li>
          ))}
        </ul>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          transition={{ type: 'spring', stiffness: 400, damping: 20 }}
          className="mt-5 w-full py-2.5 rounded-xl text-sm font-bold transition-all duration-200 flex items-center justify-center gap-2 group/btn"
          style={{
            background: `${agent.color}15`,
            color: agent.colorLight,
            border: `1px solid ${agent.color}35`,
          }}
        >
          Deploy {agent.name}
          <ChevronRight className="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-0.5" />
        </motion.button>
      </div>
    </motion.div>
  )
}

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
}

export default function AgentRoster() {
  const [search, setSearch] = useState('')

  const filtered = search.trim()
    ? AGENTS.filter((a) =>
        [a.name, a.role, a.description, ...a.capabilities]
          .join(' ')
          .toLowerCase()
          .includes(search.toLowerCase()),
      )
    : AGENTS

  return (
    <section
      id="agents"
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #0A1230 0%, #080D1E 100%)' }}
    >
      {/* Background mesh */}
      <div className="absolute inset-0 mesh-grid opacity-40 pointer-events-none" />

      {/* Side glow accents */}
      <div className="absolute -left-32 top-1/3 w-[400px] h-[600px] bg-violet-600/08 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute -right-32 top-1/2 w-[400px] h-[500px] bg-blue-600/06 blur-[100px] rounded-full pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="text-center mb-10"
        >
          <span className="section-badge-violet mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
            Your AI Workforce
          </span>
          <h2 className="section-heading mt-4 mb-4">
            Meet Your <span className="gradient-text">AI Team</span>
          </h2>
          <p className="section-sub mb-8">
            Six specialised agents, each an expert in their domain — ready to deploy in minutes.
          </p>
          <div className="flex justify-center">
            <SearchComponent
              value={search}
              onChange={setSearch}
              placeholder="Search agents by role or capability..."
            />
          </div>
        </motion.div>

        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-60px' }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mt-8"
        >
          {filtered.length === 0 ? (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="col-span-full text-center text-white/35 py-16 text-sm"
            >
              No agents match &quot;{search}&quot;
            </motion.p>
          ) : (
            filtered.map((agent, i) => (
              <AgentCard key={agent.name} agent={agent} index={i} />
            ))
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22, delay: 0.2 }}
          className="text-center mt-14"
        >
          <Button variant="primary" size="lg" arrow>Build Your Custom Team</Button>
          <p className="text-xs text-white/35 mt-3 font-medium">Mix and match agents for your exact workflow</p>
        </motion.div>
      </div>
    </section>
  )
}
