import { useRef, MouseEvent } from 'react'
import { motion } from 'framer-motion'
import { Cpu, BrainCircuit, Plug, ShieldCheck, Workflow, Lock } from 'lucide-react'

interface Feature {
  Icon: React.ElementType
  title: string
  description: string
}

const FEATURES: Feature[] = [
  {
    Icon: Cpu,
    title: 'Autonomous by Design',
    description:
      'Agents plan, act and verify their own work. No babysitting, no brittle scripts.',
  },
  {
    Icon: BrainCircuit,
    title: 'One Shared Memory',
    description:
      'Every agent reads from a unified context, so handoffs are instant and nothing slips.',
  },
  {
    Icon: Plug,
    title: 'Connect Your Stack',
    description:
      '200+ native integrations plug into the tools your team already runs on.',
  },
  {
    Icon: ShieldCheck,
    title: 'Human-in-the-Loop',
    description:
      'Set approval gates on any action. You stay in command of what matters.',
  },
  {
    Icon: Workflow,
    title: 'Real-Time Orchestration',
    description:
      'Atlas routes tasks across the roster and balances load automatically.',
  },
  {
    Icon: Lock,
    title: 'Enterprise-Grade Security',
    description:
      'SOC 2 Type II, SSO, audit logs and data isolation out of the box.',
  },
]

function FeatureCard({ feature, index }: { feature: Feature; index: number }) {
  const cardRef = useRef<HTMLDivElement>(null)
  const spotlightRef = useRef<HTMLDivElement>(null)

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current
    if (!card) return

    const rect = card.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const cx = rect.width / 2
    const cy = rect.height / 2
    const maxTilt = 6

    const rotateX = ((y - cy) / cy) * -maxTilt
    const rotateY = ((x - cx) / cx) * maxTilt

    card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02,1.02,1.02)`

    // Spotlight
    const pct = (val: number, total: number) =>
      Math.round((val / total) * 100)
    card.style.setProperty('--mx', `${pct(x, rect.width)}%`)
    card.style.setProperty('--my', `${pct(y, rect.height)}%`)
  }

  const handleMouseLeave = () => {
    const card = cardRef.current
    if (!card) return
    card.style.transform =
      'perspective(900px) rotateX(0deg) rotateY(0deg) scale3d(1,1,1)'
  }

  const { Icon, title, description } = feature

  return (
    <motion.div
      initial={{ opacity: 0, y: 44 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ type: 'spring', stiffness: 195, damping: 22, delay: index * 0.07 }}
    >
      <div
        ref={cardRef}
        className="glass-card"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{
          borderRadius: '1.25rem',
          padding: '1.5rem',
          transition: 'transform 0.15s ease, box-shadow 0.3s ease',
          willChange: 'transform',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div ref={spotlightRef} className="spotlight" />
        <div className="sheen" />

        <div
          style={{
            color: 'oklch(0.97 0 0 / 0.80)',
            marginBottom: '1rem',
            position: 'relative',
            zIndex: 1,
          }}
        >
          <Icon size={24} />
        </div>

        <h3
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 600,
            color: 'oklch(0.97 0 0)',
            fontSize: '1rem',
            marginBottom: '0.5rem',
            lineHeight: 1.3,
            position: 'relative',
            zIndex: 1,
          }}
        >
          {title}
        </h3>

        <p
          style={{
            fontFamily: "'Inter', sans-serif",
            color: 'oklch(0.78 0 0)',
            fontSize: '0.875rem',
            lineHeight: 1.65,
            margin: 0,
            position: 'relative',
            zIndex: 1,
          }}
        >
          {description}
        </p>
      </div>
    </motion.div>
  )
}

export function Features() {
  return (
    <section
      id="features"
      style={{
        paddingTop: '8rem',
        paddingBottom: '8rem',
        background: 'oklch(0.33 0 0)',
      }}
    >
      <div style={{ maxWidth: '72rem', margin: '0 auto', padding: '0 1.5rem' }}>
        <h2
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 700,
            color: 'oklch(0.97 0 0)',
            letterSpacing: '-0.025em',
            textAlign: 'center',
            marginBottom: '1rem',
            fontSize: 'clamp(1.875rem, 4vw, 3rem)',
            lineHeight: 1.1,
          }}
        >
          Built like a real operating system.
        </h2>

        <p
          style={{
            fontFamily: "'Inter', sans-serif",
            color: 'oklch(0.70 0 0)',
            fontSize: '1.125rem',
            textAlign: 'center',
            marginBottom: '4rem',
            maxWidth: '36rem',
            marginLeft: 'auto',
            marginRight: 'auto',
            lineHeight: 1.6,
          }}
        >
          Every layer is designed so your agents can work independently and together -
          reliably, at scale.
        </p>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(1, 1fr)',
            gap: '1rem',
          }}
          className="md:grid-cols-2 lg:grid-cols-3"
        >
          {FEATURES.map((feature, i) => (
            <FeatureCard key={feature.title} feature={feature} index={i} />
          ))}
        </div>
      </div>
    </section>
  )
}
