'use client';

import { motion } from 'framer-motion';

const INTEGRATIONS = {
  Sales: ['Salesforce', 'HubSpot', 'Pipedrive', 'Apollo', 'Outreach', 'Lemlist', 'Close', 'Gong'],
  Operations: ['Notion', 'Airtable', 'Monday', 'Asana', 'Zapier', 'Make', 'Slack', 'ClickUp'],
  Support: ['Intercom', 'Zendesk', 'Freshdesk', 'Front', 'Help Scout', 'Crisp', 'Drift', 'Linear'],
  Engineering: ['GitHub', 'GitLab', 'Jira', 'Sentry', 'Datadog', 'Vercel', 'AWS', 'PagerDuty'],
};

const CATEGORY_COLORS: Record<string, string> = {
  Sales: '#FF6B35',
  Operations: '#00D9FF',
  Support: '#10B981',
  Engineering: '#FF6B35',
};

function MarqueeRow({ items, color, reverse }: { items: string[]; color: string; reverse?: boolean }) {
  const doubled = [...items, ...items];
  return (
    <div style={{ overflow: 'hidden', position: 'relative' }}>
      <div
        style={{
          display: 'flex',
          animation: `marquee${reverse ? '-reverse' : ''} 28s linear infinite`,
          width: 'max-content',
        }}
        className="marquee-track"
      >
        {doubled.map((name, i) => (
          <span
            key={`${name}-${i}`}
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: '0.78rem',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: '#9CA3AF',
              marginLeft: '1.5rem',
              marginRight: '1.5rem',
              whiteSpace: 'nowrap',
              transition: 'color 0.2s ease',
              cursor: 'default',
              userSelect: 'none',
            }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLSpanElement).style.color = color; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLSpanElement).style.color = '#9CA3AF'; }}
          >
            {name}
          </span>
        ))}
      </div>
    </div>
  );
}

export function LogoStrip() {
  return (
    <section
      id="integrations"
      style={{
        backgroundColor: '#1A1F2E',
        paddingTop: '5rem',
        paddingBottom: '5rem',
        borderTop: '1px solid #2D3748',
        borderBottom: '1px solid #2D3748',
      }}
    >
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 1.5rem' }}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          style={{ textAlign: 'center', marginBottom: '3rem' }}
        >
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.7rem', color: '#9CA3AF', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
            Integrations
          </p>
          <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 800, fontSize: 'clamp(1.5rem, 3.5vw, 2.25rem)', letterSpacing: '-0.025em', color: '#FFFFFF', lineHeight: 1.15 }}>
            Works with{' '}
            <span style={{ color: '#00D9FF' }}>everything</span>{' '}
            you already use.
          </h2>
          <p style={{ color: '#9CA3AF', fontSize: '0.95rem', marginTop: '0.75rem' }}>
            200+ native integrations across Sales, Ops, Support, and Engineering.
          </p>
        </motion.div>

        {/* Category rows */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {Object.entries(INTEGRATIONS).map(([category, items], i) => (
            <motion.div
              key={category}
              initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.875rem' }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: CATEGORY_COLORS[category], flexShrink: 0 }} />
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.7rem', color: CATEGORY_COLORS[category], letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                  {category}
                </span>
                <div style={{ flex: 1, height: 1, backgroundColor: '#2D3748' }} />
              </div>
              <div className="marquee-row">
                <MarqueeRow items={items} color={CATEGORY_COLORS[category]} reverse={i % 2 === 1} />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
