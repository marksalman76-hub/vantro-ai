'use client'

import { useState, useRef } from 'react'
import { motion, AnimatePresence, useInView } from 'framer-motion'

// ─── Data ─────────────────────────────────────────────────────────────────────

const PLANS = [
  {
    name: 'Starter',
    price: { monthly: 99, annual: 79 },
    description: '5 agents running 24/7 — without hiring.',
    features: [
      '5 AI Agents',
      '50+ Integrations',
      'Email support',
      '10K tasks/month',
      'Basic analytics',
      '1 workspace',
    ],
    cta: 'Start Free Trial',
    recommended: false,
    color: '#00D9FF',
  },
  {
    name: 'Growth',
    price: { monthly: 279, annual: 223 },
    description: 'Your ops, sales, and support on autopilot.',
    features: [
      '15 AI Agents',
      '150+ Integrations',
      'Priority support',
      '100K tasks/month',
      'Advanced analytics',
      '5 workspaces',
      'Custom workflows',
      'API access',
    ],
    cta: 'Start Free Trial',
    recommended: true,
    color: '#FF6B35',
  },
  {
    name: 'Business',
    price: { monthly: 399, annual: 319 },
    description: 'Full 22-agent workforce. Unlimited scale.',
    features: [
      '22 AI Agents (all)',
      '200+ Integrations',
      'Dedicated manager',
      'Unlimited tasks',
      'Custom analytics',
      'Unlimited workspaces',
      'Custom workflows',
      'API access',
      'SLA guarantee',
      'Custom training',
    ],
    cta: 'Talk to Sales',
    recommended: false,
    color: '#FFD700',
  },
] as const

// ─── Constants ────────────────────────────────────────────────────────────────

const EASE = [0.23, 1, 0.32, 1] as const

// ─── Checkmark Icon ───────────────────────────────────────────────────────────

function CheckIcon({ color }: { color: string }) {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 18 18"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ flexShrink: 0 }}
      aria-hidden="true"
    >
      <circle cx="9" cy="9" r="9" fill={`${color}22`} />
      <path
        d="M5.5 9L7.8 11.5L12.5 6.5"
        stroke={color}
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

// ─── Price Display ────────────────────────────────────────────────────────────

function PriceDisplay({
  monthly,
  annual,
  isAnnual,
}: {
  monthly: number
  annual: number
  isAnnual: boolean
}) {
  const price = isAnnual ? annual : monthly

  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, margin: '16px 0' }}>
      <AnimatePresence mode="wait">
        <motion.span
          key={price}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.2, ease: EASE }}
          style={{
            color: '#ffffff',
            fontSize: 64,
            fontWeight: 800,
            lineHeight: 1,
          }}
        >
          ${price}
        </motion.span>
      </AnimatePresence>
      <span style={{ color: '#9ca3af', fontSize: 18, marginBottom: 6 }}>/mo</span>
    </div>
  )
}

// ─── Plan Card ────────────────────────────────────────────────────────────────

function PlanCard({
  plan,
  isAnnual,
  index,
  isInView,
}: {
  plan: (typeof PLANS)[number]
  isAnnual: boolean
  index: number
  isInView: boolean
}) {
  const [hovered, setHovered] = useState(false)
  const { recommended, color } = plan

  const baseStyle: React.CSSProperties = recommended
    ? {
        background: 'rgba(255,107,53,0.06)',
        border: '1px solid rgba(255,107,53,0.35)',
        borderRadius: 24,
        padding: '40px 32px',
        backdropFilter: 'blur(16px)',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: '0 0 60px rgba(255,107,53,0.12), 0 40px 80px rgba(0,0,0,0.3)',
        transform: 'scale(1.04)',
      }
    : {
        background: hovered ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.04)',
        border: `1px solid ${hovered ? `${color}33` : 'rgba(255,255,255,0.09)'}`,
        borderRadius: 24,
        padding: '40px 32px',
        backdropFilter: 'blur(16px)',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: hovered ? `0 0 32px ${color}11` : 'none',
        transition: 'background 0.2s ease, border-color 0.2s ease, box-shadow 0.25s ease',
      }

  return (
    <motion.div
      style={baseStyle}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.55, ease: EASE, delay: index * 0.1 }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      whileHover={recommended ? { scale: 1.06 } : { scale: 1.02 }}
    >
      {/* Most Popular badge */}
      {recommended && (
        <div
          style={{
            position: 'absolute',
            top: -14,
            right: 28,
            background: 'linear-gradient(135deg, #FF6B35, #FFD700)',
            padding: '6px 20px',
            borderRadius: 99,
            fontSize: 11,
            fontWeight: 800,
            color: '#fff',
            boxShadow: '0 4px 20px rgba(255,107,53,0.6)',
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
          }}
        >
          Most Popular
        </div>
      )}

      {/* Plan name */}
      <p
        style={{
          color,
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
        }}
      >
        {plan.name}
      </p>

      {/* Price */}
      <PriceDisplay
        monthly={plan.price.monthly}
        annual={plan.price.annual}
        isAnnual={isAnnual}
      />

      {/* Annual original price */}
      <AnimatePresence>
        {isAnnual && (
          <motion.p
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            style={{
              color: '#6b7280',
              fontSize: 13,
              marginTop: -8,
              marginBottom: 8,
              textDecoration: 'line-through',
            }}
          >
            ${plan.price.monthly}/mo billed monthly
          </motion.p>
        )}
      </AnimatePresence>

      {/* Description */}
      <p
        style={{
          color: 'rgba(255,255,255,0.5)',
          fontSize: 14,
          lineHeight: 1.65,
        }}
      >
        {plan.description}
      </p>

      {/* Divider */}
      <div style={{ height: 1, background: 'rgba(255,255,255,0.08)', margin: '24px 0' }} />

      {/* Features */}
      <ul
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
          flex: 1,
          listStyle: 'none',
          padding: 0,
          margin: 0,
        }}
      >
        {plan.features.map((feature) => (
          <li
            key={feature}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
            }}
          >
            <CheckIcon color={color} />
            <span style={{ color: 'rgba(255,255,255,0.75)', fontSize: 14 }}>{feature}</span>
          </li>
        ))}
      </ul>

      {/* CTA button */}
      <CTAButton recommended={recommended} color={color} cta={plan.cta} />
    </motion.div>
  )
}

// ─── CTA Button ───────────────────────────────────────────────────────────────

function CTAButton({
  recommended,
  color,
  cta,
}: {
  recommended: boolean
  color: string
  cta: string
}) {
  const [hovered, setHovered] = useState(false)

  return (
    <a
      href="/register"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={
        recommended
          ? {
              display: 'block',
              width: '100%',
              marginTop: 32,
              paddingTop: 14,
              paddingBottom: 14,
              borderRadius: 14,
              textAlign: 'center',
              fontWeight: 700,
              fontSize: 15,
              color: '#fff',
              background: 'linear-gradient(135deg, #FF6B35 0%, #E84D1C 100%)',
              boxShadow: hovered
                ? '0 0 50px rgba(255,107,53,0.75), 0 20px 40px rgba(255,107,53,0.4), inset 0 1px 0 rgba(255,255,255,0.25)'
                : '0 0 30px rgba(255,107,53,0.5), 0 8px 20px rgba(255,107,53,0.25), inset 0 1px 0 rgba(255,255,255,0.20)',
              transition: 'box-shadow 0.25s ease, transform 0.15s ease',
              transform: hovered ? 'translateY(-1px)' : 'none',
              textDecoration: 'none',
            }
          : {
              display: 'block',
              width: '100%',
              marginTop: 32,
              paddingTop: 14,
              paddingBottom: 14,
              borderRadius: 14,
              textAlign: 'center',
              fontWeight: 700,
              fontSize: 15,
              color: color,
              background: hovered ? `${color}11` : 'transparent',
              border: `1px solid ${hovered ? `${color}88` : `${color}44`}`,
              transition: 'background 0.2s ease, border-color 0.2s ease',
              textDecoration: 'none',
            }
      }
    >
      {cta}
    </a>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function Pricing() {
  const [isAnnual, setIsAnnual] = useState(false)
  const sectionRef = useRef<HTMLElement>(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  return (
    <section
      id="pricing"
      ref={sectionRef}
      style={{
        background: '#0F1419',
        paddingTop: 120,
        paddingBottom: 120,
        paddingLeft: 24,
        paddingRight: 24,
        width: '100%',
      }}
    >
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>

        {/* Header */}
        <motion.div
          style={{ textAlign: 'center', marginBottom: 56 }}
          initial={{ opacity: 0, y: 32 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, ease: EASE }}
        >
          <p
            style={{
              color: '#00D9FF',
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              marginBottom: 16,
            }}
          >
            TRANSPARENT PRICING
          </p>
          <h2
            style={{
              color: '#ffffff',
              fontSize: 'clamp(2rem, 3.5vw, 3.2rem)',
              fontWeight: 800,
              lineHeight: 1.1,
              marginBottom: 16,
            }}
          >
            Choose Your Plan
          </h2>
          <p style={{ color: '#9ca3af', fontSize: 18 }}>
            Start free. Scale as you grow.
          </p>
        </motion.div>

        {/* Monthly / Annual toggle */}
        <motion.div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 16,
            marginBottom: 64,
          }}
          initial={{ opacity: 0, y: 16 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, ease: EASE, delay: 0.1 }}
        >
          <span
            style={{
              fontSize: 14,
              fontWeight: 600,
              color: !isAnnual ? '#ffffff' : '#6b7280',
              transition: 'color 0.2s',
            }}
          >
            Monthly
          </span>

          <button
            onClick={() => setIsAnnual((v) => !v)}
            style={{
              position: 'relative',
              width: 56,
              height: 28,
              borderRadius: 99,
              background: isAnnual ? '#FF6B35' : 'rgba(255,255,255,0.15)',
              border: 'none',
              cursor: 'pointer',
              transition: 'background 0.3s ease',
              flexShrink: 0,
            }}
            aria-label="Toggle billing period"
          >
            <motion.span
              style={{
                position: 'absolute',
                top: 4,
                left: 4,
                width: 20,
                height: 20,
                borderRadius: '50%',
                background: '#ffffff',
                boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
              }}
              animate={{ x: isAnnual ? 28 : 0 }}
              transition={{ type: 'spring', stiffness: 500, damping: 35 }}
            />
          </button>

          <span
            style={{
              fontSize: 14,
              fontWeight: 600,
              color: isAnnual ? '#ffffff' : '#6b7280',
              transition: 'color 0.2s',
            }}
          >
            Annual
          </span>

          <AnimatePresence>
            {isAnnual && (
              <motion.span
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.2 }}
                style={{
                  background: 'rgba(255,215,0,0.15)',
                  color: '#FFD700',
                  padding: '4px 12px',
                  borderRadius: 99,
                  fontSize: 12,
                  fontWeight: 700,
                }}
              >
                Save 20%
              </motion.span>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Plan cards */}
        <div
          className="pricing-grid"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 24,
            alignItems: 'center',
          }}
        >
          {PLANS.map((plan, i) => (
            <PlanCard
              key={plan.name}
              plan={plan}
              isAnnual={isAnnual}
              index={i}
              isInView={isInView}
            />
          ))}
        </div>

        {/* Footer note */}
        <motion.p
          style={{
            textAlign: 'center',
            color: '#6b7280',
            fontSize: 14,
            marginTop: 48,
          }}
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          All plans include 14-day free trial · No credit card required
        </motion.p>

      </div>

      {/* Responsive grid fallback */}
      <style>{`
        @media (max-width: 768px) {
          #pricing .pricing-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  )
}
