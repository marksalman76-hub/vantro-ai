import { useRef } from 'react'
import {
  motion,
  useScroll,
  useTransform,
  useReducedMotion,
  useMotionValue,
  useSpring,
} from 'framer-motion'
import { Player } from '@remotion/player'
import { OrbComposition } from '../remotion/OrbComposition'

const STATS = [
  { big: '24/7', small: 'Always on' },
  { big: '200+', small: 'Integrations' },
  { big: '5 min', small: 'To deploy' },
]

const RAYS = [
  { angle: -28, opacity: 0.28, dur: 4.2 },
  { angle: -12, opacity: 0.40, dur: 5.8 },
  { angle:   6, opacity: 0.32, dur: 4.9 },
  { angle:  20, opacity: 0.22, dur: 6.5 },
]

// Animated cobalt gradient text — GPU: opacity+backgroundPosition only
function AnimatedGradientText({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        background:
          'linear-gradient(135deg, #ffffff 0%, #8ab4f8 35%, #4285f4 55%, #7baaf7 75%, #ffffff 100%)',
        backgroundSize: '300% 300%',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
        animation: 'gradient-shift 4s ease infinite',
        display: 'inline',
      }}
    >
      {children}
    </span>
  )
}

export function Hero() {
  const prefersReduced = useReducedMotion()
  const containerRef = useRef<HTMLElement>(null)

  // 60fps scroll parallax — useMotionValue + useTransform (no re-renders)
  const { scrollY } = useScroll()
  const orbY = useTransform(scrollY, [0, 700], [0, prefersReduced ? 0 : -80])
  const orbScale = useTransform(scrollY, [0, 700], [1, prefersReduced ? 1 : 0.90])
  const textY = useTransform(scrollY, [0, 700], [0, prefersReduced ? 0 : -30])
  const textOpacity = useTransform(scrollY, [0, 500], [1, prefersReduced ? 1 : 0.2])

  // Spring-smoothed cursor glow (GPU: transform only)
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)
  const springX = useSpring(mouseX, { stiffness: 80, damping: 20 })
  const springY = useSpring(mouseY, { stiffness: 80, damping: 20 })

  return (
    <section
      ref={containerRef}
      onMouseMove={(e) => {
        const rect = containerRef.current?.getBoundingClientRect()
        if (!rect) return
        mouseX.set(e.clientX - rect.left - rect.width / 2)
        mouseY.set(e.clientY - rect.top - rect.height / 2)
      }}
      style={{
        minHeight: '100dvh',
        display: 'flex',
        alignItems: 'center',
        paddingTop: '4rem',
        paddingBottom: '6rem',
        position: 'relative',
        overflow: 'hidden',
        background:
          'radial-gradient(ellipse 80% 60% at 65% 50%, oklch(0.12 0.08 260) 0%, oklch(0.07 0.04 262) 55%, oklch(0.04 0.03 264) 100%)',
      }}
    >
      {/* Higgsfield-style grain overlay */}
      <div className="grain" style={{ position: 'absolute', inset: 0, zIndex: 10, pointerEvents: 'none' }} />

      {/* Spring-tracked cursor glow — GPU: transform */}
      {!prefersReduced && (
        <motion.div
          style={{
            position: 'absolute',
            width: '600px',
            height: '600px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, oklch(0.62 0.22 248 / 0.08) 0%, transparent 70%)',
            x: springX,
            y: springY,
            top: '50%',
            left: '50%',
            translateX: '-50%',
            translateY: '-50%',
            pointerEvents: 'none',
            zIndex: 1,
            willChange: 'transform',
          }}
        />
      )}

      {/* Soft vignette */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse 100% 100% at 50% 50%, transparent 55%, oklch(0.04 0.03 264 / 0.70) 100%)',
          zIndex: 2,
          pointerEvents: 'none',
        }}
      />

      {/* Animated diagonal rays from orb — GPU: opacity */}
      {!prefersReduced &&
        RAYS.map((ray, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, ray.opacity, 0] }}
            transition={{
              duration: ray.dur,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: i * 1.1,
            }}
            style={{
              position: 'absolute',
              top: '50%',
              left: '55%',
              width: '180%',
              height: '2px',
              background: `linear-gradient(90deg, transparent 0%, rgba(100,140,255,${ray.opacity}) 40%, rgba(100,140,255,${ray.opacity * 0.35}) 70%, transparent 100%)`,
              transform: `rotate(${ray.angle}deg)`,
              transformOrigin: '0% 50%',
              filter: 'blur(1.5px)',
              pointerEvents: 'none',
              zIndex: 1,
              willChange: 'opacity',
            }}
          />
        ))}

      {/* Content grid */}
      <div
        style={{
          maxWidth: '82rem',
          margin: '0 auto',
          padding: '0 1.5rem',
          width: '100%',
          display: 'grid',
          gridTemplateColumns: 'repeat(1, 1fr)',
          gap: '3rem',
          alignItems: 'center',
          position: 'relative',
          zIndex: 5,
        }}
        className="lg:grid-cols-2"
      >
        {/* LEFT — text, GPU parallax via useTransform */}
        <motion.div
          style={{ y: textY, opacity: textOpacity, willChange: 'transform, opacity' }}
          className="flex flex-col gap-6"
        >
          {/* Animated pill badge */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              border: '1px solid oklch(0.62 0.22 248 / 0.35)',
              borderRadius: '9999px',
              padding: '0.3rem 0.85rem',
              width: 'fit-content',
              background: 'oklch(0.62 0.22 248 / 0.08)',
              backdropFilter: 'blur(8px)',
            }}
          >
            <span
              style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: 'oklch(0.62 0.22 248)',
                boxShadow: '0 0 8px oklch(0.62 0.22 248 / 0.80)',
                flexShrink: 0,
                animation: 'ray-pulse 2s ease-in-out infinite',
              }}
            />
            <span
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '0.72rem',
                letterSpacing: '0.12em',
                color: 'oklch(0.78 0.12 248)',
                textTransform: 'uppercase',
              }}
            >
              Autonomous AI Workforce
            </span>
          </motion.div>

          {/* H1 — Higgsfield-style bold, animated gradient on accent */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontSize: 'clamp(2.8rem, 5.2vw, 5rem)',
              lineHeight: 1.03,
              letterSpacing: '-0.025em',
              fontWeight: 700,
              margin: 0,
              color: 'oklch(0.97 0 0)',
            }}
          >
            Deploy a workforce that{' '}
            <br />
            <AnimatedGradientText>never sleeps.</AnimatedGradientText>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '1.125rem',
              color: 'oklch(0.68 0.03 252)',
              maxWidth: '28rem',
              lineHeight: 1.65,
              margin: 0,
            }}
          >
            Your autonomous AI team works across sales, ops, engineering and
            support — around the clock, without burnout.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            style={{ display: 'flex', gap: '0.875rem', flexWrap: 'wrap' }}
          >
            {/* Primary — cobalt gradient, GPU: transform+opacity */}
            <a
              href="/#pricing"
              style={{
                background:
                  'linear-gradient(180deg, oklch(0.65 0.22 248) 0%, oklch(0.52 0.22 248) 100%)',
                color: 'oklch(0.97 0 0)',
                border: 'none',
                cursor: 'pointer',
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.9375rem',
                fontWeight: 600,
                padding: '0.75rem 1.625rem',
                borderRadius: '9999px',
                boxShadow:
                  'inset 0 1px 0 rgba(160,200,255,0.30), 0 4px 24px oklch(0.52 0.22 248 / 0.45)',
                transition: 'opacity 0.18s ease, transform 0.14s ease',
                textDecoration: 'none',
                display: 'inline-block',
                willChange: 'transform, opacity',
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget as HTMLAnchorElement
                el.style.opacity = '0.88'
                el.style.transform = 'translateY(-2px) scale(1.02)'
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget as HTMLAnchorElement
                el.style.opacity = '1'
                el.style.transform = 'translateY(0) scale(1)'
              }}
              onMouseDown={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.transform =
                  'translateY(1px) scale(0.98)'
              }}
              onMouseUp={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.transform =
                  'translateY(-2px) scale(1.02)'
              }}
            >
              Activate your agents
            </a>

            {/* Ghost */}
            <a
              href="#agents"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                border: '1px solid oklch(0.62 0.22 248 / 0.30)',
                borderRadius: '9999px',
                padding: '0.75rem 1.5rem',
                color: 'oklch(0.82 0.06 250)',
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.9375rem',
                textDecoration: 'none',
                transition: 'border-color 0.2s ease, background 0.2s ease, transform 0.14s ease',
                willChange: 'transform',
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget as HTMLAnchorElement
                el.style.background = 'oklch(0.62 0.22 248 / 0.08)'
                el.style.borderColor = 'oklch(0.62 0.22 248 / 0.55)'
                el.style.transform = 'translateY(-2px)'
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget as HTMLAnchorElement
                el.style.background = 'transparent'
                el.style.borderColor = 'oklch(0.62 0.22 248 / 0.30)'
                el.style.transform = 'translateY(0)'
              }}
            >
              Meet the roster
            </a>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.45 }}
            style={{ display: 'flex', gap: '2rem', marginTop: '0.25rem', flexWrap: 'wrap' }}
          >
            {STATS.map((stat, i) => (
              <div key={stat.big} style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                <div>
                  <div
                    style={{
                      fontFamily: "'Space Grotesk', sans-serif",
                      fontSize: '1.5rem',
                      fontWeight: 700,
                      color: 'oklch(0.97 0 0)',
                      lineHeight: 1,
                    }}
                  >
                    {stat.big}
                  </div>
                  <div
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: '0.75rem',
                      color: 'oklch(0.55 0.04 252)',
                      marginTop: '0.2rem',
                    }}
                  >
                    {stat.small}
                  </div>
                </div>
                {i < STATS.length - 1 && (
                  <div
                    style={{
                      width: '1px',
                      height: '2rem',
                      background: 'oklch(0.62 0.22 248 / 0.18)',
                      flexShrink: 0,
                    }}
                  />
                )}
              </div>
            ))}
          </motion.div>
        </motion.div>

        {/* RIGHT — Remotion Player orb, GPU parallax: transform only */}
        <motion.div
          style={{
            y: orbY,
            scale: orbScale,
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            willChange: 'transform',
          }}
        >
          <motion.div
            initial={prefersReduced ? false : { scale: 0.85, opacity: 0 }}
            animate={prefersReduced ? {} : { scale: 1, opacity: 1 }}
            transition={{ duration: 1.0, ease: [0.22, 1, 0.36, 1] }}
            style={{ position: 'relative', width: '100%', maxWidth: '540px' }}
          >
            {/* Cobalt outer corona */}
            <div
              style={{
                position: 'absolute',
                inset: '-12%',
                borderRadius: '50%',
                background:
                  'radial-gradient(circle, oklch(0.62 0.22 248 / 0.12) 0%, oklch(0.48 0.18 248 / 0.06) 50%, transparent 75%)',
                filter: 'blur(30px)',
                pointerEvents: 'none',
              }}
            />

            {/* Remotion Player — video-grade orb animation */}
            <Player
              component={OrbComposition}
              durationInFrames={300}
              compositionWidth={540}
              compositionHeight={540}
              fps={60}
              loop
              autoPlay
              clickToPlay={false}
              style={{
                width: '100%',
                height: 'auto',
                display: 'block',
              }}
            />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
