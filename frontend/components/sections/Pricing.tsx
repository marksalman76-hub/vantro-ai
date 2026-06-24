'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, X, ChevronDown, Zap, Users, Building2 } from 'lucide-react'
import Button from '@/components/Button'

const PLANS = [
  {
    name:      'Starter',
    icon:      Zap,
    desc:      'Perfect for trying out Vantro',
    monthly:   99,
    annual:    79,
    agents:    '2–3 agents',
    cta:       'Start Free Trial',
    href:      '/signup',
    highlight: false,
    badge:     null as string | null,
    color:     '#3B82F6',
    features: [
      { text: '2–3 AI Agents',           included: true  },
      { text: '5 integrations',           included: true  },
      { text: 'Email support',            included: true  },
      { text: 'Dashboard analytics',      included: true  },
      { text: 'Custom brand training',    included: false },
      { text: 'Priority support',         included: false },
      { text: 'API access',               included: false },
      { text: 'White-label options',      included: false },
    ],
  },
  {
    name:      'Professional',
    icon:      Users,
    desc:      'For growing teams and agencies',
    monthly:   299,
    annual:    239,
    agents:    '5–7 agents',
    cta:       'Start Free Trial',
    href:      '/signup',
    highlight: true,
    badge:     'Most Popular',
    color:     '#7C3AED',
    features: [
      { text: '5–7 AI Agents',            included: true  },
      { text: '500+ integrations',        included: true  },
      { text: '24/7 priority support',    included: true  },
      { text: 'Advanced analytics',       included: true  },
      { text: 'Custom brand training',    included: true  },
      { text: 'Workflow automation',      included: true  },
      { text: 'API access',               included: false },
      { text: 'White-label options',      included: false },
    ],
  },
  {
    name:      'Enterprise',
    icon:      Building2,
    desc:      'For large organisations',
    monthly:   null as number | null,
    annual:    null as number | null,
    agents:    'Unlimited agents',
    cta:       'Contact Sales',
    href:      '#roi-calculator',
    highlight: false,
    badge:     null as string | null,
    color:     '#06B6D4',
    features: [
      { text: 'Unlimited AI Agents',       included: true },
      { text: 'All integrations + custom', included: true },
      { text: 'Dedicated account manager', included: true },
      { text: 'Custom reporting',          included: true },
      { text: 'Priority brand training',   included: true },
      { text: 'Advanced automation flows', included: true },
      { text: 'Full API access',           included: true },
      { text: 'White-label & SSO',         included: true },
    ],
  },
]

const FAQS = [
  {
    q: 'Can I change plans at any time?',
    a: 'Yes. Upgrade or downgrade whenever you need. Upgrades are pro-rated and take effect immediately; downgrades apply from the next billing cycle.',
  },
  {
    q: 'Is there a long-term contract?',
    a: 'No contracts required. Cancel any time from your dashboard. Annual plans are refundable within the first 14 days.',
  },
  {
    q: 'How does the 14-day free trial work?',
    a: 'You get full Professional access for 14 days, no credit card required. At the end of the trial, pick any plan or walk away — no charges either way.',
  },
  {
    q: 'What if I need more agents than any plan offers?',
    a: "Our Enterprise plan is fully custom. Talk to our solutions team and we'll build a configuration that matches your exact workflow and scale.",
  },
]

function FAQItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="glass-strong rounded-xl border border-white/[0.07] overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left group"
        aria-expanded={open}
      >
        <span className="text-sm font-semibold text-white/80 group-hover:text-white transition-colors">{q}</span>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ type: 'spring', stiffness: 400, damping: 25 }}
          className="flex-shrink-0 text-white/35 group-hover:text-white/60 transition-colors"
        >
          <ChevronDown className="w-4 h-4" />
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            className="overflow-hidden"
          >
            <p className="px-5 pb-5 text-sm text-white/45 leading-relaxed">{a}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function Pricing() {
  const [annual, setAnnual] = useState(false)

  return (
    <section
      id="pricing"
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #070D1F 0%, #0A1230 100%)' }}
    >
      <div className="absolute inset-0 mesh-grid opacity-40 pointer-events-none" />
      <div className="absolute -top-40 left-1/4 w-[600px] h-[500px] bg-violet-600/08 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute -bottom-40 right-1/4 w-[500px] h-[400px] bg-blue-600/08 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="text-center mb-12"
        >
          <span className="section-badge-violet mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
            Transparent Pricing
          </span>
          <h2 className="section-heading mt-4 mb-4">
            Simple Plans,{' '}
            <span className="gradient-text">Serious Results</span>
          </h2>
          <p className="section-sub mb-8 mt-2">
            Start free. No credit card required. Deploy your first agent in 10 minutes.
          </p>

          {/* Toggle */}
          <div className="inline-flex items-center gap-1.5 p-1.5 glass-strong rounded-full border border-white/10">
            {['Monthly', 'Annual'].map((label) => {
              const isAnnual = label === 'Annual'
              const active = annual === isAnnual
              return (
                <button
                  key={label}
                  onClick={() => setAnnual(isAnnual)}
                  className={`px-5 py-2 rounded-full text-sm font-bold transition-all duration-250 flex items-center gap-2 ${
                    active
                      ? 'bg-violet-600 text-white shadow-[0_2px_16px_rgba(124,58,237,0.45)]'
                      : 'text-white/45 hover:text-white/70'
                  }`}
                >
                  {label}
                  {isAnnual && annual && (
                    <span className="text-xs text-cyan-300 font-bold">-20%</span>
                  )}
                </button>
              )
            })}
          </div>
        </motion.div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {PLANS.map((plan, i) => {
            const Icon = plan.icon
            return (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 32 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ type: 'spring', stiffness: 200, damping: 22, delay: i * 0.1 }}
                whileHover={{ y: -6, scale: 1.01 }}
                className="relative"
              >
                {/* Iridescent glow for highlighted plan */}
                {plan.highlight && (
                  <>
                    <div className="absolute -inset-[1px] rounded-2xl bg-gradient-to-b from-violet-500/50 via-blue-500/30 to-cyan-500/20 pointer-events-none" />
                    <div className="absolute -inset-[2px] rounded-2xl blur-sm bg-gradient-to-b from-violet-500/20 to-transparent pointer-events-none" />
                  </>
                )}

                <div
                  className={`relative flex flex-col h-full rounded-2xl p-7 ${
                    plan.highlight
                      ? 'glass-ultra shadow-[0_16px_60px_rgba(124,58,237,0.25)]'
                      : 'glass border border-white/[0.08]'
                  }`}
                >
                  {/* Badge */}
                  {plan.badge && (
                    <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                      <span className="px-4 py-1 rounded-full text-xs font-black text-white bg-gradient-to-r from-violet-600 to-blue-500 shadow-[0_2px_20px_rgba(124,58,237,0.6)] tracking-wide">
                        {plan.badge}
                      </span>
                    </div>
                  )}

                  {/* Header */}
                  <div className="flex items-center gap-3 mb-5">
                    <div
                      className="w-11 h-11 rounded-xl flex items-center justify-center"
                      style={{
                        background: plan.highlight
                          ? 'linear-gradient(135deg, #7C3AED, #3B82F6)'
                          : `${plan.color}18`,
                        border: `1px solid ${plan.color}35`,
                        boxShadow: `0 0 20px ${plan.color}15`,
                      }}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-white">{plan.name}</h3>
                      <p className="text-xs text-white/40 font-medium">{plan.desc}</p>
                    </div>
                  </div>

                  {/* Price */}
                  <div className="mb-6 min-h-[76px] flex flex-col justify-center">
                    {plan.monthly !== null ? (
                      <>
                        <div className="flex items-end gap-1.5">
                          <AnimatePresence mode="wait">
                            <motion.span
                              key={annual ? 'a' : 'm'}
                              initial={{ opacity: 0, y: -10 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: 10 }}
                              transition={{ duration: 0.2 }}
                              className="text-4xl font-black text-white"
                            >
                              ${annual ? plan.annual : plan.monthly}
                            </motion.span>
                          </AnimatePresence>
                          <span className="text-white/35 text-sm pb-1.5">/month</span>
                        </div>
                        <p className="text-xs text-white/30 mt-1">
                          {annual
                            ? `Billed $${(plan.annual! * 12).toLocaleString()} / year`
                            : 'Billed monthly'}
                        </p>
                      </>
                    ) : (
                      <>
                        <p className="text-2xl font-black gradient-text-cyan">Custom</p>
                        <p className="text-xs text-white/30 mt-1">Tailored to your scale</p>
                      </>
                    )}
                  </div>

                  {/* CTA */}
                  <Button
                    href={plan.href}
                    variant={plan.highlight ? 'primary' : 'secondary'}
                    size="md"
                    className="w-full mb-5"
                  >
                    {plan.cta}
                  </Button>

                  {/* Agent badge */}
                  <div
                    className="flex items-center justify-center px-3 py-2 rounded-lg mb-5"
                    style={{ background: `${plan.color}12`, border: `1px solid ${plan.color}20` }}
                  >
                    <span className="text-xs font-semibold" style={{ color: plan.color }}>{plan.agents}</span>
                  </div>

                  {/* Features */}
                  <ul className="space-y-2.5">
                    {plan.features.map((f) => (
                      <li key={f.text} className="flex items-center gap-2.5">
                        {f.included ? (
                          <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                        ) : (
                          <X className="w-4 h-4 text-white/18 flex-shrink-0" />
                        )}
                        <span className={`text-sm ${f.included ? 'text-white/65' : 'text-white/25'}`}>
                          {f.text}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Trust strip */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="flex flex-wrap items-center justify-center gap-6 mb-16 text-xs text-white/35 font-medium"
        >
          {['14-day free trial', 'No credit card required', 'Cancel any time', '99.9% uptime SLA', 'SOC 2 certified'].map((item) => (
            <span key={item} className="flex items-center gap-1.5">
              <Check className="w-3 h-3 text-emerald-400" />
              {item}
            </span>
          ))}
        </motion.div>

        {/* FAQs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="max-w-2xl mx-auto"
        >
          <h3 className="text-xl font-bold text-white text-center mb-7">
            Frequently Asked Questions
          </h3>
          <div className="space-y-3">
            {FAQS.map((faq) => (
              <FAQItem key={faq.q} q={faq.q} a={faq.a} />
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
