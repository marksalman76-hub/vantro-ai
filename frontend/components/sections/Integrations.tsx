'use client'

import { motion } from 'framer-motion'
import { ArrowRight, Zap } from 'lucide-react'

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

const PILL_COLORS = [
  { bg: 'rgba(192,132,252,0.12)', text: 'rgba(192,132,252,0.9)',  dot: '#C084FC' },
  { bg: 'rgba(147,197,253,0.12)', text: 'rgba(147,197,253,0.9)',  dot: '#93C5FD' },
  { bg: 'rgba(103,232,249,0.12)', text: 'rgba(103,232,249,0.9)',  dot: '#67E8F9' },
  { bg: 'rgba(110,231,183,0.10)', text: 'rgba(110,231,183,0.9)',  dot: '#6EE7B7' },
  { bg: 'rgba(249,168,212,0.10)', text: 'rgba(249,168,212,0.9)',  dot: '#F9A8D4' },
  { bg: 'rgba(253,211,77,0.10)',  text: 'rgba(253,211,77,0.9)',   dot: '#FCD34D' },
]

const BG_COLOR = '#070D1F'

const BRAND_COLORS: Record<string, { text: string; dot: string }> = {
  Salesforce:        { text: 'rgba(0,161,224,0.9)',   dot: '#00A1E0' },
  HubSpot:          { text: 'rgba(255,122,89,0.9)',   dot: '#FF7A59' },
  Slack:            { text: 'rgba(224,30,90,0.9)',    dot: '#E01E5A' },
  Stripe:           { text: 'rgba(123,115,247,0.9)',  dot: '#7B73F7' },
  Shopify:          { text: 'rgba(150,191,72,0.9)',   dot: '#96BF48' },
  Notion:           { text: 'rgba(255,255,255,0.75)', dot: '#fff'    },
  GitHub:           { text: 'rgba(255,255,255,0.75)', dot: '#f0f6fc' },
  Zapier:           { text: 'rgba(255,74,0,0.9)',     dot: '#FF4A00' },
  Jira:             { text: 'rgba(0,82,204,0.9)',     dot: '#0052CC' },
  Zendesk:          { text: 'rgba(31,115,183,0.9)',   dot: '#1F73B7' },
  Linear:           { text: 'rgba(94,106,210,0.9)',   dot: '#5E6AD2' },
  Intercom:         { text: 'rgba(31,138,255,0.9)',   dot: '#1F8AFF' },
  Snowflake:        { text: 'rgba(41,181,232,0.9)',   dot: '#29B5E8' },
  Datadog:          { text: 'rgba(99,44,166,0.9)',    dot: '#632CA6' },
  Vercel:           { text: 'rgba(255,255,255,0.75)', dot: '#fff'    },
}

function Pill({ label, index }: { label: string; index: number }) {
  const branded = BRAND_COLORS[label]
  const ci = index % PILL_COLORS.length
  const p = PILL_COLORS[ci]
  const textColor = branded?.text ?? p.text
  const dotColor  = branded?.dot  ?? p.dot
  const bgColor   = branded ? `${branded.dot}12` : p.bg

  return (
    <span
      className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold whitespace-nowrap mx-2 transition-opacity duration-200 hover:opacity-100 opacity-70"
      style={{
        background: bgColor,
        color: textColor,
        border: `1px solid ${dotColor}20`,
      }}
    >
      <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: dotColor }} />
      {label}
    </span>
  )
}

export default function Integrations() {
  return (
    <section
      id="integrations"
      className="section-padding relative overflow-hidden"
      style={{ background: `linear-gradient(180deg, #080D1E 0%, ${BG_COLOR} 100%)` }}
    >
      <div className="absolute inset-0 mesh-grid-fine opacity-30 pointer-events-none" />
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-blue-600/07 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="text-center mb-14"
        >
          <span className="section-badge-blue mb-5">
            <Zap className="w-3 h-3" />
            1,000+ Integrations
          </span>
          <h2 className="section-heading mt-4 mb-4">
            Vantro Works Where{' '}
            <span className="gradient-text">You Already Work</span>
          </h2>
          <p className="section-sub mt-2">
            Connect to every tool in your stack — from CRMs and helpdesks to databases and data warehouses.
            If it has an API, Vantro can talk to it.
          </p>
        </motion.div>

        {/* Infinite scroll strips */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="space-y-4 mb-12"
        >
          {/* Row 1 */}
          <div className="scroll-strip relative">
            <div className="absolute left-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
              style={{ background: `linear-gradient(to right, ${BG_COLOR}, transparent)` }} />
            <div className="absolute right-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
              style={{ background: `linear-gradient(to left, ${BG_COLOR}, transparent)` }} />
            <div className="scroll-track-left py-1">
              {[...ROW_1, ...ROW_1].map((name, i) => (
                <Pill key={`r1-${i}`} label={name} index={i} />
              ))}
            </div>
          </div>

          {/* Row 2 */}
          <div className="scroll-strip relative">
            <div className="absolute left-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
              style={{ background: `linear-gradient(to right, ${BG_COLOR}, transparent)` }} />
            <div className="absolute right-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
              style={{ background: `linear-gradient(to left, ${BG_COLOR}, transparent)` }} />
            <div className="scroll-track-right py-1">
              {[...ROW_2, ...ROW_2].map((name, i) => (
                <Pill key={`r2-${i}`} label={name} index={i + 5} />
              ))}
            </div>
          </div>
        </motion.div>

        {/* Custom integration CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="glass-iridescent rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6"
        >
          <div>
            <h3 className="text-xl font-bold text-white mb-2">
              Don&apos;t see your tool?
            </h3>
            <p className="text-sm text-white/50 leading-relaxed">
              Request a custom integration. Our team typically ships new connectors within 5 business days.
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.04, y: -2 }}
            whileTap={{ scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 400, damping: 20 }}
            className="flex-shrink-0 inline-flex items-center gap-2.5 px-6 py-3 rounded-xl font-bold text-sm text-violet-300 border border-violet-500/35 hover:border-violet-400 hover:bg-violet-500/10 transition-colors whitespace-nowrap backdrop-blur-sm"
          >
            Request Integration <ArrowRight className="w-4 h-4" />
          </motion.button>
        </motion.div>
      </div>
    </section>
  )
}
