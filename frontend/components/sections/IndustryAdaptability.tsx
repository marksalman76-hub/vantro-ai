'use client'

import { motion } from 'framer-motion'
import { Monitor, ShoppingCart, Heart, DollarSign, Home, BookOpen, Cog, Building2, ArrowRight } from 'lucide-react'
import Button from '@/components/Button'

const INDUSTRIES = [
  {
    icon: Monitor,
    name: 'SaaS',
    color: '#7C3AED',
    agents: ['Atlas', 'Hermes'],
    useCases: ['Trial conversion', 'Churn prevention', 'Expansion revenue'],
    metric: '-34% churn',
  },
  {
    icon: ShoppingCart,
    name: 'E-commerce',
    color: '#F59E0B',
    agents: ['Forge', 'Atlas'],
    useCases: ['Order automation', 'Upsell sequences', 'Returns handling'],
    metric: '+21% AOV',
  },
  {
    icon: Heart,
    name: 'Healthcare',
    color: '#10B981',
    agents: ['Hermes', 'Sage'],
    useCases: ['Patient intake', 'Appointment reminders', 'Clinical ops'],
    metric: '99% accuracy',
  },
  {
    icon: DollarSign,
    name: 'Finance',
    color: '#3B82F6',
    agents: ['Oracle', 'Sage'],
    useCases: ['Market research', 'Regulatory reports', 'Client outreach'],
    metric: '5× faster reports',
  },
  {
    icon: Home,
    name: 'Real Estate',
    color: '#EC4899',
    agents: ['Atlas', 'Hermes'],
    useCases: ['Lead qualification', 'Listing follow-up', 'Tenant support'],
    metric: '120 leads/week',
  },
  {
    icon: BookOpen,
    name: 'Education',
    color: '#06B6D4',
    agents: ['Hermes', 'Muse'],
    useCases: ['Admissions queries', 'Student support', 'Campaign nurture'],
    metric: '3× enrolments',
  },
  {
    icon: Cog,
    name: 'Manufacturing',
    color: '#8B5CF6',
    agents: ['Forge', 'Sage'],
    useCases: ['Workflow automation', 'Downtime analysis', 'Supplier comms'],
    metric: '-40% downtime',
  },
  {
    icon: Building2,
    name: 'Hospitality',
    color: '#F97316',
    agents: ['Hermes', 'Atlas'],
    useCases: ['Guest services', 'Booking management', 'Loyalty upsells'],
    metric: '4.8★ avg rating',
  },
]

const item = {
  hidden: { opacity: 0, y: 28 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.45, ease: 'easeOut' as const } },
}

export default function IndustryAdaptability() {
  return (
    <section id="industry-adaptability" className="section-padding bg-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-teal-500/20 text-teal-300 mb-4">
            Works Across Industries
          </span>
          <h2 className="section-heading mb-4">
            <span className="gradient-text">50+ Industries</span>, Zero Reconfiguration
          </h2>
          <p className="section-sub">
            Tell Vantro your industry. It handles the rest — language, workflows, compliance norms, and more.
          </p>
        </motion.div>

        <motion.div
          variants={{ hidden: {}, show: { transition: { staggerChildren: 0.07 } } }}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-60px' }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {INDUSTRIES.map((ind) => {
            const Icon = ind.icon
            return (
              <motion.div
                key={ind.name}
                variants={item}
                className="glass glass-hover rounded-2xl p-5 group cursor-default"
              >
                {/* Icon + name */}
                <div className="flex items-center gap-3 mb-4">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-110"
                    style={{ background: `${ind.color}1A`, border: `1px solid ${ind.color}40` }}
                  >
                    <Icon className="w-5 h-5" style={{ color: ind.color }} />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">{ind.name}</h3>
                    <span
                      className="text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                      style={{ background: `${ind.color}18`, color: ind.color }}
                    >
                      {ind.metric}
                    </span>
                  </div>
                </div>

                {/* Agent tags */}
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {ind.agents.map((a) => (
                    <span key={a} className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.06] text-white/50 border border-white/[0.08]">
                      {a}
                    </span>
                  ))}
                </div>

                {/* Use cases */}
                <ul className="space-y-1">
                  {ind.useCases.map((uc) => (
                    <li key={uc} className="text-xs text-white/40 flex items-center gap-1.5">
                      <span className="w-1 h-1 rounded-full flex-shrink-0" style={{ background: ind.color }} />
                      {uc}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )
          })}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-center mt-12"
        >
          <p className="text-sm text-white/45 mb-4">Don&apos;t see your industry? We cover 50+ and counting.</p>
          <Button variant="secondary" size="md" arrow>
            Explore All Industries
          </Button>
        </motion.div>
      </div>
    </section>
  )
}
