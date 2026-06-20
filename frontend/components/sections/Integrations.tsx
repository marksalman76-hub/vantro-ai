'use client'

import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'

const ROW_1 = [
  'Salesforce', 'HubSpot', 'Slack', 'Notion', 'Zapier', 'GitHub',
  'Stripe', 'OpenAI', 'Google Workspace', 'Jira', 'Zendesk', 'Linear',
  'Intercom', 'Twilio', 'Airtable',
]

const ROW_2 = [
  'Shopify', 'Webflow', 'Monday.com', 'Asana', 'Figma', 'Confluence',
  'Datadog', 'Snowflake', 'Databricks', 'AWS', 'Vercel', 'Cloudflare',
  'Mixpanel', 'Amplitude', 'Segment',
]

// Colours for pill backgrounds (cycling)
const PILL_COLORS = [
  'rgba(124,58,237,0.15)', 'rgba(59,130,246,0.15)', 'rgba(6,182,212,0.15)',
  'rgba(16,185,129,0.12)', 'rgba(236,72,153,0.12)', 'rgba(245,158,11,0.12)',
]
const PILL_TEXT = [
  'rgba(196,132,252,0.9)', 'rgba(147,197,253,0.9)', 'rgba(103,232,249,0.9)',
  'rgba(110,231,183,0.9)', 'rgba(249,168,212,0.9)', 'rgba(253,211,77,0.9)',
]

function Pill({ label, index }: { label: string; index: number }) {
  const ci = index % PILL_COLORS.length
  return (
    <span
      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap mx-2 border border-white/[0.07]"
      style={{ background: PILL_COLORS[ci], color: PILL_TEXT[ci] }}
    >
      <span className="w-2 h-2 rounded-full opacity-70" style={{ background: PILL_TEXT[ci] }} />
      {label}
    </span>
  )
}

export default function Integrations() {
  return (
    <section id="integrations" className="section-padding bg-dark overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-blue-500/20 text-blue-300 mb-4">
            1,000+ Integrations
          </span>
          <h2 className="section-heading mb-4">
            Vantro Works Where <span className="gradient-text">You Already Work</span>
          </h2>
          <p className="section-sub">
            Connect to every tool in your stack — from CRMs and helpdesks to databases and data warehouses.
            If it has an API, Vantro can talk to it.
          </p>
        </motion.div>

        {/* Infinite scroll rows */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="space-y-4 mb-14"
        >
          {/* Row 1 — left */}
          <div className="scroll-strip relative">
            <div
              className="absolute left-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
              style={{ background: 'linear-gradient(to right, #0F1A3F, transparent)' }}
            />
            <div
              className="absolute right-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
              style={{ background: 'linear-gradient(to left, #0F1A3F, transparent)' }}
            />
            <div className="scroll-track-left py-1">
              {[...ROW_1, ...ROW_1].map((name, i) => (
                <Pill key={`r1-${i}`} label={name} index={i} />
              ))}
            </div>
          </div>

          {/* Row 2 — right */}
          <div className="scroll-strip relative">
            <div
              className="absolute left-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
              style={{ background: 'linear-gradient(to right, #0F1A3F, transparent)' }}
            />
            <div
              className="absolute right-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
              style={{ background: 'linear-gradient(to left, #0F1A3F, transparent)' }}
            />
            <div className="scroll-track-right py-1">
              {[...ROW_2, ...ROW_2].map((name, i) => (
                <Pill key={`r2-${i}`} label={name} index={i + 5} />
              ))}
            </div>
          </div>
        </motion.div>

        {/* Custom integration CTA */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="glass rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 border border-violet-500/15"
        >
          <div>
            <h3 className="text-xl font-bold text-white mb-2">
              Don&apos;t see your tool?
            </h3>
            <p className="text-sm text-white/55">
              Request a custom integration. Our team typically ships new connectors within 5 business days.
            </p>
          </div>
          <button className="flex-shrink-0 inline-flex items-center gap-2 px-6 py-3 rounded-lg font-semibold text-sm text-white border border-violet-500/40 hover:border-violet-500 hover:bg-violet-500/10 transition-all whitespace-nowrap">
            Request Integration <ArrowRight className="w-4 h-4" />
          </button>
        </motion.div>
      </div>
    </section>
  )
}
