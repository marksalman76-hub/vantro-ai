'use client';

import { motion } from 'framer-motion';

const TESTIMONIALS = [
  {
    quote: "We replaced a 3-person ops team with Vantro agents. They run 24/7, never miss a follow-up, and cost a fraction. Best decision we made this year.",
    name: 'Sarah Chen',
    role: 'Head of Revenue Ops',
    company: 'Cleardesk',
    initials: 'SC',
    color: '#FF6B35',
  },
  {
    quote: "Our support ticket volume tripled after a product launch. Vantro's chat and routing agents handled the surge without us adding a single hire.",
    name: 'Marcus Webb',
    role: 'VP Engineering',
    company: 'Stacksmith',
    initials: 'MW',
    color: '#00D9FF',
  },
  {
    quote: "The SEO and content agents ship more qualified content in a week than our old agency delivered in a month. ROI was clear within 30 days.",
    name: 'Priya Nair',
    role: 'Growth Lead',
    company: 'Tidalflow',
    initials: 'PN',
    color: '#10B981',
  },
  {
    quote: "Deploy takes minutes, not months. We had agents live before our first cup of coffee. The integrations just work — no custom code.",
    name: 'Jordan Okafor',
    role: 'CTO',
    company: 'Halden Labs',
    initials: 'JO',
    color: '#FF6B35',
  },
  {
    quote: "I was sceptical about AI agents actually replacing real work. After 60 days, Vantro handles 80% of our routine ops and I have my team back for strategic projects.",
    name: 'Emma Larsson',
    role: 'COO',
    company: 'Lumen Systems',
    initials: 'EL',
    color: '#00D9FF',
  },
  {
    quote: "The lead qualifier alone paid for the annual plan in the first month. Every sales rep now starts their day with a pre-scored, pre-briefed pipeline.",
    name: 'Dev Patel',
    role: 'Director of Sales',
    company: 'Northwind',
    initials: 'DP',
    color: '#10B981',
  },
];

export function Testimonials() {
  return (
    <section style={{ backgroundColor: '#0F1419', paddingTop: '6rem', paddingBottom: '6rem' }}>
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 1.5rem' }}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          style={{ textAlign: 'center', marginBottom: '3.5rem' }}
        >
          <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 800, fontSize: 'clamp(1.75rem, 4vw, 2.75rem)', letterSpacing: '-0.025em', color: '#FFFFFF', marginBottom: '0.875rem', lineHeight: 1.1 }}>
            Teams that{' '}
            <span style={{ color: '#FF6B35' }}>deployed and never looked back.</span>
          </h2>
          <p style={{ color: '#9CA3AF', fontSize: '1.05rem', maxWidth: '32rem', margin: '0 auto', lineHeight: 1.6 }}>
            From solo founders to scaling ops teams — real results from real operators.
          </p>
        </motion.div>

        {/* Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 20rem), 1fr))', gap: '1.25rem' }}>
          {TESTIMONIALS.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.45, delay: (i % 3) * 0.08, ease: [0.22, 1, 0.36, 1] }}
              style={{
                backgroundColor: '#1A1F2E',
                border: '1px solid #2D3748',
                borderLeft: `3px solid ${t.color}`,
                borderRadius: '0.75rem',
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem',
                transition: 'border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease',
              }}
              whileHover={{ y: -4 }}
            >
              {/* Quote mark */}
              <div style={{ fontFamily: 'Georgia, serif', fontSize: '2.5rem', lineHeight: 1, color: t.color, opacity: 0.6, marginBottom: '-0.5rem' }}>
                "
              </div>

              {/* Quote text */}
              <p style={{ color: '#E5E7EB', fontSize: '0.9rem', lineHeight: 1.65, margin: 0, fontStyle: 'italic' }}>
                {t.quote}
              </p>

              {/* Attribution */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', borderTop: '1px solid #2D3748', paddingTop: '1rem', marginTop: 'auto' }}>
                <div style={{ width: 36, height: 36, borderRadius: '50%', backgroundColor: `${t.color}22`, border: `1px solid ${t.color}44`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '0.7rem', color: t.color }}>
                    {t.initials}
                  </span>
                </div>
                <div>
                  <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, fontSize: '0.85rem', color: '#FFFFFF' }}>
                    {t.name}
                  </div>
                  <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.68rem', color: '#9CA3AF' }}>
                    {t.role} · {t.company}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
