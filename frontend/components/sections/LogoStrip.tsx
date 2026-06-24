'use client'

import { motion } from 'framer-motion'

const BRANDS_A = [
  { name: 'Salesforce',        color: '#00A1E0' },
  { name: 'HubSpot',           color: '#FF7A59' },
  { name: 'Slack',             color: '#E01E5A' },
  { name: 'Stripe',            color: '#7B73F7' },
  { name: 'Shopify',           color: '#96BF48' },
  { name: 'Notion',            color: '#fff'    },
  { name: 'GitHub',            color: '#fff'    },
  { name: 'Zapier',            color: '#FF4A00' },
  { name: 'Intercom',          color: '#1F8AFF' },
]

const BRANDS_B = [
  { name: 'Zendesk',           color: '#1F73B7' },
  { name: 'Jira',              color: '#0052CC' },
  { name: 'Linear',            color: '#5E6AD2' },
  { name: 'Snowflake',         color: '#29B5E8' },
  { name: 'Datadog',           color: '#632CA6' },
  { name: 'Vercel',            color: '#fff'    },
  { name: 'Airtable',          color: '#2D7FF9' },
  { name: 'Mixpanel',          color: '#7856FF' },
  { name: 'Amplitude',         color: '#1D84FF' },
]

function BrandMark({ name, color }: { name: string; color: string }) {
  return (
    <span
      className="inline-flex items-center mx-8 text-sm font-bold tracking-tight cursor-default transition-opacity duration-300 whitespace-nowrap opacity-30 hover:opacity-70"
      style={{ color }}
    >
      {name}
    </span>
  )
}

export default function LogoStrip() {
  return (
    <section
      className="relative overflow-hidden py-10"
      style={{ background: 'linear-gradient(180deg, #07091A 0%, #080D1E 100%)' }}
    >
      {/* Edge fades */}
      <div className="absolute left-0 top-0 bottom-0 w-32 z-10 pointer-events-none"
        style={{ background: 'linear-gradient(to right, #07091A, transparent)' }} />
      <div className="absolute right-0 top-0 bottom-0 w-32 z-10 pointer-events-none"
        style={{ background: 'linear-gradient(to left, #07091A, transparent)' }} />

      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="space-y-3"
      >
        {/* Label */}
        <p className="text-center text-[10px] font-mono tracking-[0.22em] uppercase text-white/20 mb-6">
          Trusted by fast-growing teams at
        </p>

        {/* Row A — scroll left */}
        <div className="scroll-strip">
          <div className="scroll-track-left">
            {[...BRANDS_A, ...BRANDS_A].map((b, i) => (
              <BrandMark key={`a-${i}`} name={b.name} color={b.color} />
            ))}
          </div>
        </div>

        {/* Row B — scroll right */}
        <div className="scroll-strip">
          <div className="scroll-track-right">
            {[...BRANDS_B, ...BRANDS_B].map((b, i) => (
              <BrandMark key={`b-${i}`} name={b.name} color={b.color} />
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  )
}
