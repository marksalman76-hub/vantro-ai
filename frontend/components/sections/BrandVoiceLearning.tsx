'use client'

import { motion } from 'framer-motion'

const STAGES = [
  {
    day: 'Day 1',
    label: 'First Contact',
    description: 'Agent deploys into your workspace. Reads docs, past conversations, and brand guidelines.',
    match: 30,
    color: '#7C3AED',
  },
  {
    day: 'Day 3',
    label: 'Pattern Detection',
    description: 'Identifies frequently used phrases, tone markers, and communication style preferences.',
    match: 55,
    color: '#5B6FCA',
  },
  {
    day: 'Day 5',
    label: 'Language Activation',
    description: 'Begins naturally using your vocabulary, preferred terms, and sign-off styles.',
    match: 72,
    color: '#3B82F6',
  },
  {
    day: 'Day 7',
    label: 'Voice Alignment',
    description: '"Felt exactly like talking to one of their team members." — Customer feedback survey.',
    match: 85,
    color: '#06B6D4',
  },
  {
    day: 'Month 1',
    label: 'Brand Mastery',
    description: 'Indistinguishable from your best human agents. Now proactively suggests brand improvements.',
    match: 95,
    color: '#10B981',
  },
]

const BEFORE = {
  customer: 'Hey, my package still hasn\'t arrived — what\'s going on?',
  bot: 'Hello. I apologize for any inconvenience regarding your order. Please provide your order number so I can look into this matter for you.',
  label: 'Generic AI',
  accent: '#EF4444',
}

const AFTER = {
  customer: 'Hey, my package still hasn\'t arrived — what\'s going on?',
  bot: 'Oh no, that\'s definitely not the vibe we\'re going for! 😤 Let me jump on this right now — share your order number and I\'ll track it down while we chat. We\'ll get this sorted for you ASAP! 💪',
  label: 'Vantro · Day 7',
  accent: '#10B981',
}

function ChatBubble({ role, text, accent }: { role: 'customer' | 'bot'; text: string; accent: string }) {
  const isBot = role === 'bot'
  return (
    <div className={`flex ${isBot ? '' : 'justify-end'} mb-3`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
          isBot ? 'rounded-tl-sm text-white' : 'rounded-tr-sm text-white'
        }`}
        style={{
          background: isBot ? `${accent}20` : 'rgba(255,255,255,0.08)',
          border: `1px solid ${isBot ? `${accent}35` : 'rgba(255,255,255,0.12)'}`,
        }}
      >
        {text}
      </div>
    </div>
  )
}

function ChatCard({ data, title }: { data: typeof BEFORE; title: string }) {
  return (
    <div className="glass rounded-2xl overflow-hidden">
      <div
        className="px-4 py-3 border-b border-white/[0.08] flex items-center gap-2"
        style={{ background: `${data.accent}10` }}
      >
        <span
          className="w-2 h-2 rounded-full"
          style={{ background: data.accent }}
        />
        <span className="text-xs font-semibold" style={{ color: data.accent }}>
          {data.label}
        </span>
        <span className="text-xs text-white/30 ml-auto">{title}</span>
      </div>
      <div className="p-4">
        <ChatBubble role="customer" text={data.customer} accent={data.accent} />
        <ChatBubble role="bot" text={data.bot} accent={data.accent} />
      </div>
    </div>
  )
}

export default function BrandVoiceLearning() {
  return (
    <section id="brand-voice" className="section-padding bg-dark">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-pink-500/20 text-pink-300 mb-4">
            Brand Voice Learning
          </span>
          <h2 className="section-heading mb-4">
            Learns to Sound <span className="gradient-text">Exactly Like You</span>
          </h2>
          <p className="section-sub">
            In 7 days, Vantro agents are indistinguishable from your best human reps. In 30, they become the gold standard.
          </p>
        </motion.div>

        {/* Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="glass rounded-2xl p-7 mb-10"
        >
          <div className="space-y-6">
            {STAGES.map((stage, i) => (
              <div key={stage.day} className="flex items-start gap-5">
                {/* Timeline node + connector */}
                <div className="flex flex-col items-center flex-shrink-0" style={{ width: 40 }}>
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.35, delay: i * 0.1 }}
                    className="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0"
                    style={{ background: stage.color, boxShadow: `0 0 15px ${stage.color}55` }}
                  >
                    {stage.match}%
                  </motion.div>
                  {i < STAGES.length - 1 && (
                    <div className="w-px flex-1 mt-1" style={{ background: `${stage.color}30`, minHeight: 24 }} />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 pb-4">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 mb-1.5">
                    <span className="text-xs font-bold text-white/30 uppercase tracking-widest">{stage.day}</span>
                    <span className="text-sm font-semibold text-white">{stage.label}</span>
                  </div>
                  <p className="text-sm text-white/50 leading-relaxed mb-2">{stage.description}</p>

                  {/* Match bar */}
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ background: stage.color }}
                        initial={{ width: 0 }}
                        whileInView={{ width: `${stage.match}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.1, delay: i * 0.15, ease: 'easeOut' }}
                      />
                    </div>
                    <span className="text-xs text-white/35 w-16 flex-shrink-0">voice match</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Before / After */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <p className="text-center text-sm text-white/40 mb-6 uppercase tracking-widest text-xs font-semibold">
            The Transformation in Action
          </p>
          <div className="grid sm:grid-cols-2 gap-4">
            <ChatCard data={BEFORE} title="Without Vantro" />
            <ChatCard data={AFTER}  title="With Vantro" />
          </div>
        </motion.div>
      </div>
    </section>
  )
}
