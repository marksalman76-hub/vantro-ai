import { motion } from 'framer-motion'

interface Step {
  label: string
  title: string
  description: string
}

const STEPS: Step[] = [
  {
    label: '01',
    title: 'Pick your agents',
    description:
      'Choose from 22 specialists or let Atlas recommend a team for your goals.',
  },
  {
    label: '02',
    title: 'Connect and brief',
    description:
      'Link your tools and describe outcomes in plain language. No code required.',
  },
  {
    label: '03',
    title: 'Deploy the workforce',
    description:
      'Agents start working in minutes, coordinating tasks across your operation.',
  },
  {
    label: '04',
    title: 'Watch it compound',
    description:
      'Review results, refine guardrails, and scale the team as you grow.',
  },
]

function StepCard({
  step,
  index,
}: {
  step: Step
  index: number
}) {
  const isLeft = index % 2 === 0

  return (
    <div
      style={{
        position: 'relative',
        display: 'grid',
        gridTemplateColumns: '1fr 2.5rem 1fr',
        alignItems: 'start',
        marginBottom: index < STEPS.length - 1 ? '4rem' : 0,
        gap: 0,
      }}
    >
      {/* Left content */}
      <div
        style={{
          paddingRight: '2rem',
          display: 'flex',
          justifyContent: 'flex-end',
        }}
      >
        {isLeft && (
          <motion.div
            className="glass-card"
            initial={{ opacity: 0, x: -32 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.55, ease: [0.25, 0.46, 0.45, 0.94] }}
            style={{
              borderRadius: '0.75rem',
              padding: '1.5rem',
              maxWidth: '18rem',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <div className="spotlight" />
            <div className="sheen" />
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '0.7rem',
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                color: '#E5E7EB',
                marginBottom: '0.5rem',
                position: 'relative',
                zIndex: 1,
              }}
            >
              Step {step.label}
            </div>
            <h3
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 600,
                color: '#FFFFFF',
                fontSize: '1rem',
                marginBottom: '0.5rem',
                lineHeight: 1.3,
                position: 'relative',
                zIndex: 1,
              }}
            >
              {step.title}
            </h3>
            <p
              style={{
                fontFamily: "'Inter', sans-serif",
                color: '#9CA3AF',
                fontSize: '0.875rem',
                lineHeight: 1.6,
                margin: 0,
                position: 'relative',
                zIndex: 1,
              }}
            >
              {step.description}
            </p>
          </motion.div>
        )}
      </div>

      {/* Center circle */}
      <motion.div
        initial={{ opacity: 0, scale: 0.6 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true, margin: '-60px' }}
        transition={{ duration: 0.4, delay: 0.1, ease: 'backOut' }}
        style={{
          width: '2.5rem',
          height: '2.5rem',
          borderRadius: '50%',
          background: '#232936',
          border: '1px solid rgba(0,217,255,0.28)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '0.75rem',
          color: '#E5E7EB',
          flexShrink: 0,
          position: 'relative',
          zIndex: 2,
        }}
      >
        {step.label}
      </motion.div>

      {/* Right content */}
      <div
        style={{
          paddingLeft: '2rem',
          display: 'flex',
          justifyContent: 'flex-start',
        }}
      >
        {!isLeft && (
          <motion.div
            className="glass-card"
            initial={{ opacity: 0, x: 32 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.55, ease: [0.25, 0.46, 0.45, 0.94] }}
            style={{
              borderRadius: '0.75rem',
              padding: '1.5rem',
              maxWidth: '18rem',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <div className="spotlight" />
            <div className="sheen" />
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '0.7rem',
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                color: '#E5E7EB',
                marginBottom: '0.5rem',
                position: 'relative',
                zIndex: 1,
              }}
            >
              Step {step.label}
            </div>
            <h3
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 600,
                color: '#FFFFFF',
                fontSize: '1rem',
                marginBottom: '0.5rem',
                lineHeight: 1.3,
                position: 'relative',
                zIndex: 1,
              }}
            >
              {step.title}
            </h3>
            <p
              style={{
                fontFamily: "'Inter', sans-serif",
                color: '#9CA3AF',
                fontSize: '0.875rem',
                lineHeight: 1.6,
                margin: 0,
                position: 'relative',
                zIndex: 1,
              }}
            >
              {step.description}
            </p>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export function HowItWorks() {
  return (
    <section
      id="how-it-works"
      style={{
        paddingTop: '8rem',
        paddingBottom: '8rem',
        background: '#1A1F2E',
      }}
    >
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 1.5rem' }}>
        <h2
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
            color: '#FFFFFF',
            letterSpacing: '-0.025em',
            textAlign: 'center',
            marginBottom: '1rem',
            fontSize: 'clamp(1.875rem, 4vw, 3rem)',
            lineHeight: 1.1,
          }}
        >
          From signup to deployed in minutes.
        </h2>

        <p
          style={{
            fontFamily: "'Inter', sans-serif",
            color: '#9CA3AF',
            fontSize: '1.125rem',
            textAlign: 'center',
            marginBottom: '5rem',
            maxWidth: '36rem',
            marginLeft: 'auto',
            marginRight: 'auto',
            lineHeight: 1.6,
          }}
        >
          No complex setup. No engineering overhead. Your team is up and running
          faster than any traditional hiring process.
        </p>

        {/* Timeline container */}
        <div
          style={{
            maxWidth: '52rem',
            margin: '0 auto',
            position: 'relative',
          }}
        >
          {/* Vertical center line */}
          <div
            style={{
              position: 'absolute',
              left: '50%',
              top: 0,
              bottom: 0,
              width: '1px',
              background: 'rgba(0,217,255,0.15)',
              transform: 'translateX(-50%)',
              pointerEvents: 'none',
            }}
          />

          {STEPS.map((step, i) => (
            <StepCard key={step.label} step={step} index={i} />
          ))}
        </div>
      </div>
    </section>
  )
}
