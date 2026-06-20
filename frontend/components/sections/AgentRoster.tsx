'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, MessageCircle, Search, Sparkles, BarChart2, Settings, Check } from 'lucide-react'
import Button from '@/components/Button'
import { GlowCard } from '@/components/ui/spotlight-card'
import SearchComponent from '@/components/ui/animated-glowing-search-bar'

type GlowColor = 'blue' | 'purple' | 'green' | 'red' | 'orange'

const AGENTS = [
  {
    name: 'Atlas',
    role: 'Sales Agent',
    description: 'Qualifies leads, books meetings, and nurtures pipeline 24/7 without manual intervention.',
    color: '#7C3AED',
    glowColor: 'purple' as GlowColor,
    icon: TrendingUp,
    capabilities: ['Lead scoring & qualification', 'Personalised email sequences', 'CRM auto-sync (Salesforce / HubSpot)', 'Meeting booking & follow-up'],
  },
  {
    name: 'Hermes',
    role: 'Support Agent',
    description: 'Resolves customer issues instantly across chat, email, and voice channels around the clock.',
    color: '#06B6D4',
    glowColor: 'blue' as GlowColor,
    icon: MessageCircle,
    capabilities: ['Intelligent ticket routing', 'FAQ & knowledge-base automation', 'Sentiment analysis & escalation', 'Multi-channel (Intercom / Zendesk)'],
  },
  {
    name: 'Oracle',
    role: 'Research Agent',
    description: 'Gathers competitive intelligence, summarises industry trends, and delivers actionable reports.',
    color: '#3B82F6',
    glowColor: 'blue' as GlowColor,
    icon: Search,
    capabilities: ['Real-time web research', 'Automated report generation', 'Structured data extraction', 'Trend & competitor analysis'],
  },
  {
    name: 'Muse',
    role: 'Marketing Agent',
    description: 'Creates SEO-optimised content, schedules posts, and runs A/B tests at scale.',
    color: '#EC4899',
    glowColor: 'red' as GlowColor,
    icon: Sparkles,
    capabilities: ['Long-form & social content', 'SEO optimisation', 'Multi-platform scheduling', 'A/B copy testing'],
  },
  {
    name: 'Sage',
    role: 'Data Agent',
    description: 'Transforms raw data into live dashboards, anomaly alerts, and predictive insights.',
    color: '#10B981',
    glowColor: 'green' as GlowColor,
    icon: BarChart2,
    capabilities: ['Pipeline data analysis', 'Interactive dashboards', 'Anomaly & outlier detection', 'Predictive trend modelling'],
  },
  {
    name: 'Forge',
    role: 'Operations Agent',
    description: 'Automates multi-step workflows across every tool in your stack without writing code.',
    color: '#F59E0B',
    glowColor: 'orange' as GlowColor,
    icon: Settings,
    capabilities: ['No-code workflow builder', 'Cross-tool API orchestration', 'Error handling & retries', 'Process speed optimisation'],
  },
]

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
}
const item = {
  hidden: { opacity: 0, y: 30 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' as const } },
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
    <section id="agents" className="section-padding bg-gradient-section bg-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-violet-500/20 text-violet-300 mb-4">
            Your AI Workforce
          </span>
          <h2 className="section-heading mb-4">Meet Your AI Team</h2>
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
          viewport={{ once: true, margin: '-80px' }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mt-10"
        >
          {filtered.length === 0 ? (
            <motion.p
              variants={item}
              className="col-span-full text-center text-white/40 py-12 text-sm"
            >
              No agents match &quot;{search}&quot;
            </motion.p>
          ) : (
            filtered.map((agent) => {
              const Icon = agent.icon
              return (
                <motion.div key={agent.name} variants={item}>
                  <GlowCard
                    glowColor={agent.glowColor}
                    customSize={true}
                    className="w-full"
                  >
                    <div className="flex flex-col h-full">
                      <div className="flex items-center gap-3 mb-3">
                        <div
                          className="w-11 h-11 rounded-xl flex-shrink-0 flex items-center justify-center"
                          style={{ background: agent.color + '22', border: '1px solid ' + agent.color + '44' }}
                        >
                          <Icon className="w-5 h-5" style={{ color: agent.color }} />
                        </div>
                        <div className="min-w-0">
                          <h3 className="text-base font-bold text-white leading-none">{agent.name}</h3>
                          <span
                            className="text-[10px] font-semibold px-2 py-0.5 rounded-full mt-1 inline-block leading-none"
                            style={{ background: agent.color + '22', color: agent.color }}
                          >
                            {agent.role}
                          </span>
                        </div>
                      </div>

                      <p className="text-xs text-white/50 leading-relaxed mb-4">{agent.description}</p>

                      <ul className="space-y-1.5 flex-1">
                        {agent.capabilities.map((cap) => (
                          <li key={cap} className="flex items-start gap-2 text-xs text-white/55">
                            <Check className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style={{ color: agent.color }} />
                            {cap}
                          </li>
                        ))}
                      </ul>

                      <div className="pt-4 mt-4">
                        <button
                          className="w-full py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 hover:opacity-80"
                          style={{
                            background: agent.color + '22',
                            color:      agent.color,
                            border:     '1px solid ' + agent.color + '44',
                          }}
                        >
                          Deploy {agent.name}
                        </button>
                      </div>
                    </div>
                  </GlowCard>
                </motion.div>
              )
            })
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-center mt-12"
        >
          <Button variant="primary" size="lg" arrow>Build Your Custom Team</Button>
          <p className="text-xs text-white/40 mt-3">Mix and match agents for your exact workflow</p>
        </motion.div>
      </div>
    </section>
  )
}
