import { useRef, useState, useEffect } from 'react'
import {
  motion,
  AnimatePresence,
  useScroll,
  useTransform,
  useReducedMotion,
  useMotionValue,
} from 'framer-motion'

const STATS = [
  { big: '22', small: 'AI agents' },
  { big: 'SOC 2', small: 'Type II' },
  { big: '$0', small: 'To start' },
]

const RAYS = [
  { angle: -28, opacity: 0.22, dur: 4.2 },
  { angle: -12, opacity: 0.32, dur: 5.8 },
  { angle:   6, opacity: 0.26, dur: 4.9 },
  { angle:  20, opacity: 0.18, dur: 6.5 },
]

const ACTIVITIES = [
  { agent: 'Atlas', action: 'Routed 14 inbound leads to Nova', time: '2s ago' },
  { agent: 'Echo', action: 'Resolved ticket #4,471 via chat', time: '5s ago' },
  { agent: 'Forge', action: 'Merged PR #88 — feat/auth-v2', time: '9s ago' },
  { agent: 'Ledger', action: 'Flagged $2.4K anomaly for review', time: '13s ago' },
  { agent: 'Pulse', action: 'Published Q3 campaign deck', time: '19s ago' },
  { agent: 'Nova', action: 'Closed deal — Westridge Corp', time: '26s ago' },
  { agent: 'Scout', action: 'Compiled 14pg competitor brief', time: '33s ago' },
  { agent: 'Sentinel', action: 'Blocked 3 suspicious login attempts', time: '41s ago' },
]

export function Hero() {
  const prefersReduced = useReducedMotion()
  const containerRef = useRef<HTMLElement>(null)

  const { scrollY } = useScroll()
  const orbY = useTransform(scrollY, [0, 600], [0, prefersReduced ? 0 : -60])

  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)
  const orbPX = useTransform(mouseX, [-1, 1], [prefersReduced ? 0 : -24, prefersReduced ? 0 : 24])
  const orbPY = useTransform(mouseY, [-1, 1], [prefersReduced ? 0 : -16, prefersReduced ? 0 : 16])
  const orbCombinedY = useTransform(
    [orbY, orbPY],
    ([scroll, mouse]: number[]) => scroll + mouse
  )
  const orbRotate = useTransform(mouseX, [-1, 1], [prefersReduced ? 0 : -4, prefersReduced ? 0 : 4])

  const [feedStart, setFeedStart] = useState(0)
  useEffect(() => {
    const id = setInterval(() => {
      setFeedStart((i) => (i + 1) % ACTIVITIES.length)
    }, 2200)
    return () => clearInterval(id)
  }, [])
  const feedItems = [0, 1, 2, 3].map((offset) => ACTIVITIES[(feedStart + offset) % ACTIVITIES.length])

  return (
    <section
      ref={containerRef}
      onMouseMove={(e) => {
        if (prefersReduced) return
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
        mouseX.set((e.clientX - rect.left) / rect.width * 2 - 1)
        mouseY.set((e.clientY - rect.top) / rect.height * 2 - 1)
      }}
      style={{
        minHeight: '100dvh',
        display: 'flex',
        alignItems: 'center',
        paddingTop: '4rem',
        paddingBottom: '6rem',
        position: 'relative',
        overflow: 'hidden',
        background: 'oklch(0.14 0 0)',
      }}
    >
      {/* Scanline texture */}
      <div
        className="scanlines"
        style={{ position: 'absolute', inset: 0, zIndex: 2, pointerEvents: 'none' }}
      />

      {/* Smoke blobs */}
      <div
        style={{
          position: 'absolute', top: '10%', left: '-10%',
          width: '55vw', height: '55vw', borderRadius: '50%',
          background: 'radial-gradient(circle, oklch(0.97 0 0 / 0.12) 0%, transparent 70%)',
          animation: 'drift1 22s ease-in-out infinite',
          pointerEvents: 'none',
        }}
      />
      <div
        style={{
          position: 'absolute', top: '40%', right: '-15%',
          width: '45vw', height: '45vw', borderRadius: '50%',
          background: 'radial-gradient(circle, oklch(0.97 0 0 / 0.10) 0%, transparent 70%)',
          animation: 'drift2 28s ease-in-out infinite',
          animationDelay: '-9s',
          pointerEvents: 'none',
        }}
      />
      <div
        style={{
          position: 'absolute', bottom: '-5%', left: '30%',
          width: '40vw', height: '40vw', borderRadius: '50%',
          background: 'radial-gradient(circle, oklch(0.97 0 0 / 0.08) 0%, transparent 70%)',
          animation: 'drift1 34s ease-in-out infinite',
          animationDelay: '-17s',
          pointerEvents: 'none',
        }}
      />

      {/* Diagonal light rays from orb area */}
      {!prefersReduced && RAYS.map((ray, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            top: '50%',
            left: '55%',
            width: '180%',
            height: '2px',
            background: `linear-gradient(90deg, transparent 0%, rgba(255,255,255,${ray.opacity}) 40%, rgba(255,255,255,${ray.opacity * 0.4}) 70%, transparent 100%)`,
            transform: `rotate(${ray.angle}deg)`,
            transformOrigin: '0% 50%',
            filter: 'blur(1.5px)',
            pointerEvents: 'none',
            zIndex: 1,
            animation: `ray-pulse ${ray.dur}s ease-in-out infinite`,
            animationDelay: `${i * 1.1}s`,
          }}
        />
      ))}

      {/* Content grid */}
      <div
        style={{
          maxWidth: '80rem',
          margin: '0 auto',
          padding: '0 1.5rem',
          width: '100%',
          display: 'grid',
          gridTemplateColumns: 'repeat(1, 1fr)',
          gap: '3rem',
          alignItems: 'center',
          position: 'relative',
          zIndex: 3,
        }}
        className="lg:grid-cols-2"
      >
        {/* LEFT */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: '0.75rem',
              letterSpacing: '0.15em',
              color: 'oklch(0.70 0 0)',
              textTransform: 'uppercase',
            }}
          >
            Autonomous AI Workforce
          </div>

          {/* Chrome gradient H1 — split-text word animation */}
          <h1
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontSize: 'clamp(2.8rem, 5vw, 4.8rem)',
              lineHeight: 1.05,
              letterSpacing: '-0.02em',
              fontWeight: 700,
              margin: 0,
            }}
          >
            <span style={{ display: 'block' }}>
              {['Deploy', 'a', 'workforce', 'that'].map((word, wordIndex) => (
                <motion.span
                  key={word + wordIndex}
                  initial={prefersReduced ? false : { opacity: 0, y: 18 }}
                  animate={prefersReduced ? {} : { opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: wordIndex * 0.065, ease: [0.22, 1, 0.36, 1] }}
                  style={{
                    display: 'inline-block',
                    marginRight: '0.28em',
                    background: 'linear-gradient(180deg, #ffffff 0%, #d8d8d8 28%, #9a9a9a 62%, #555555 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  {word}
                </motion.span>
              ))}
              <br />
              {['never', 'sleeps.'].map((word, i) => {
                const wordIndex = 4 + i
                return (
                  <motion.span
                    key={word + wordIndex}
                    initial={prefersReduced ? false : { opacity: 0, y: 18 }}
                    animate={prefersReduced ? {} : { opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: wordIndex * 0.065, ease: [0.22, 1, 0.36, 1] }}
                    style={{
                      display: 'inline-block',
                      marginRight: '0.28em',
                      background: 'linear-gradient(180deg, #c8c8c8 0%, #888888 50%, #444444 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                    }}
                  >
                    {word}
                  </motion.span>
                )
              })}
            </span>
          </h1>

          <p
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '1.125rem',
              color: 'oklch(0.70 0 0)',
              maxWidth: '28rem',
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            Your autonomous AI team works across sales, ops, engineering and support
            - around the clock, without burnout.
          </p>

          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <a
              href="https://app.vantro.ai/signup"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                background: 'linear-gradient(160deg, oklch(0.78 0.13 250) 0%, oklch(0.60 0.18 250) 100%)',
                color: 'oklch(0.98 0 0)',
                border: 'none',
                cursor: 'pointer',
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.9375rem',
                fontWeight: 600,
                padding: '0.75rem 1.5rem',
                borderRadius: '9999px',
                boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.25), 0 4px 20px oklch(0.60 0.18 250 / 0.50)',
                transition: 'opacity 0.2s ease, transform 0.15s ease',
                textDecoration: 'none',
                display: 'inline-block',
              }}
              onMouseEnter={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.boxShadow = 'inset 0 1px 0 rgba(255,255,255,0.40), 0 8px 32px oklch(0.60 0.18 250 / 0.75)'
                ;(e.currentTarget as HTMLAnchorElement).style.transform = 'scale(1.02)'
              }}
              onMouseLeave={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.boxShadow = 'inset 0 1px 0 rgba(255,255,255,0.25), 0 4px 20px oklch(0.60 0.18 250 / 0.50)'
                ;(e.currentTarget as HTMLAnchorElement).style.transform = 'scale(1)'
              }}
            >
              Activate your agents
            </a>
            <a
              href="#agents"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                border: '1px solid oklch(0.97 0 0 / 0.20)',
                borderRadius: '9999px',
                padding: '0.75rem 1.5rem',
                color: 'oklch(0.97 0 0)',
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.9375rem',
                textDecoration: 'none',
                boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08)',
                transition: 'border-color 0.2s ease, background 0.2s ease',
              }}
              onMouseEnter={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.background = 'oklch(0.97 0 0 / 0.06)'
                ;(e.currentTarget as HTMLAnchorElement).style.borderColor = 'oklch(0.97 0 0 / 0.35)'
              }}
              onMouseLeave={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.background = 'transparent'
                ;(e.currentTarget as HTMLAnchorElement).style.borderColor = 'oklch(0.97 0 0 / 0.20)'
              }}
            >
              Meet the roster
            </a>
          </div>

          {/* Live agent activity feed */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8, ease: [0.22, 1, 0.36, 1] }}
            style={{
              marginTop: '2rem',
              width: '100%',
              maxWidth: '420px',
              background: 'oklch(1 0 0 / 0.05)',
              border: '1px solid oklch(1 0 0 / 0.12)',
              borderRadius: '0.875rem',
              overflow: 'hidden',
            }}
          >
            {/* Header bar */}
            <div style={{
              padding: '0.5rem 0.875rem',
              borderBottom: '1px solid oklch(1 0 0 / 0.08)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}>
              <span style={{
                width: '6px', height: '6px', borderRadius: '50%',
                background: 'oklch(0.75 0.22 145)',
                boxShadow: '0 0 6px oklch(0.75 0.22 145 / 0.7)',
                flexShrink: 0,
              }} />
              <span style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '0.6rem',
                letterSpacing: '0.14em',
                textTransform: 'uppercase',
                color: 'oklch(0.55 0 0)',
              }}>
                Live agent activity
              </span>
            </div>
            {/* Activity rows */}
            <AnimatePresence mode="popLayout">
              {feedItems.map((item, i) => (
                <motion.div
                  key={`${item.agent}-${item.action}`}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: i === 0 ? 1 : 0.6 - i * 0.12 }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.625rem',
                    padding: '0.45rem 0.875rem',
                    borderBottom: i < 3 ? '1px solid oklch(1 0 0 / 0.04)' : 'none',
                  }}
                >
                  <span style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.65rem',
                    fontWeight: 600,
                    color: 'oklch(0.82 0.18 65)',
                    flexShrink: 0,
                    width: '3.5rem',
                  }}>
                    {item.agent}
                  </span>
                  <span style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: '0.72rem',
                    color: 'oklch(0.65 0 0)',
                    flex: 1,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}>
                    {item.action}
                  </span>
                  <span style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.6rem',
                    color: 'oklch(0.45 0 0)',
                    flexShrink: 0,
                  }}>
                    {item.time}
                  </span>
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>

          <div style={{ display: 'flex', gap: '2rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
            {STATS.map((stat, i) => (
              <div key={stat.big} style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                <div>
                  <div
                    style={{
                      fontFamily: "'Space Grotesk', sans-serif",
                      fontSize: '1.5rem',
                      fontWeight: 700,
                      background: 'linear-gradient(180deg, #ffffff 0%, #999999 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                      lineHeight: 1,
                    }}
                  >
                    {stat.big}
                  </div>
                  <div
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: '0.75rem',
                      color: 'oklch(0.70 0 0)',
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
                      background: 'oklch(0.97 0 0 / 0.10)',
                      flexShrink: 0,
                    }}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT - Orb */}
        <motion.div
          style={{
            y: orbCombinedY,
            x: orbPX,
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              position: 'absolute',
              width: '60%',
              height: '60%',
              background: 'radial-gradient(circle, oklch(0.97 0 0 / 0.06) 0%, transparent 70%)',
              filter: 'blur(60px)',
              pointerEvents: 'none',
            }}
          />
          <motion.div
            initial={prefersReduced ? false : { scale: 0.86, opacity: 0 }}
            whileInView={prefersReduced ? {} : { scale: 1, opacity: 1 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
            style={{ position: 'relative', width: '100%', maxWidth: 'min(520px, 85vw)', rotate: orbRotate }}
          >
            {!prefersReduced && (
              <motion.div
                animate={{
                  background: [
                    'radial-gradient(circle 140px at 30% 28%, rgba(255,255,255,0.75) 0%, transparent 65%)',
                    'radial-gradient(circle 140px at 72% 22%, rgba(255,255,255,0.75) 0%, transparent 65%)',
                    'radial-gradient(circle 140px at 76% 74%, rgba(255,255,255,0.75) 0%, transparent 65%)',
                    'radial-gradient(circle 140px at 28% 78%, rgba(255,255,255,0.75) 0%, transparent 65%)',
                    'radial-gradient(circle 140px at 30% 28%, rgba(255,255,255,0.75) 0%, transparent 65%)',
                  ],
                }}
                transition={{ duration: 5, repeat: Infinity, ease: 'linear' }}
                style={{
                  position: 'absolute', inset: 0,
                  mixBlendMode: 'screen',
                  pointerEvents: 'none',
                  zIndex: 2,
                  maskImage: 'radial-gradient(ellipse 90% 90% at 50% 50%, black 22%, rgba(0,0,0,0.55) 52%, transparent 86%)',
                  WebkitMaskImage: 'radial-gradient(ellipse 90% 90% at 50% 50%, black 22%, rgba(0,0,0,0.55) 52%, transparent 86%)',
                }}
              />
            )}
            <motion.img
              src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/saLNUqZiiYVuufKN.png"
              alt="Vantro AI orb"
              animate={
                prefersReduced
                  ? {}
                  : {
                      y: [0, -28, -8, -36, -12, 0],
                      x: [0, 18, -12, 10, -5, 0],
                      scale: [1, 1.07, 0.96, 1.09, 0.98, 1],
                      filter: [
                        'brightness(1) drop-shadow(0 0 30px rgba(255,255,255,0.15))',
                        'brightness(1.40) drop-shadow(0 0 80px rgba(255,255,255,0.45))',
                        'brightness(0.88) drop-shadow(0 0 12px rgba(255,255,255,0.05))',
                        'brightness(1.30) drop-shadow(0 0 65px rgba(255,255,255,0.32))',
                        'brightness(1.05) drop-shadow(0 0 40px rgba(255,255,255,0.18))',
                        'brightness(1) drop-shadow(0 0 30px rgba(255,255,255,0.15))',
                      ],
                    }
              }
              transition={prefersReduced ? {} : { duration: 10, repeat: Infinity, ease: 'easeInOut' }}
              style={{
                width: '100%',
                height: 'auto',
                mixBlendMode: 'screen',
                maskImage: 'radial-gradient(ellipse 90% 90% at 50% 50%, black 22%, rgba(0,0,0,0.55) 52%, transparent 86%)',
                WebkitMaskImage: 'radial-gradient(ellipse 90% 90% at 50% 50%, black 22%, rgba(0,0,0,0.55) 52%, transparent 86%)',
                position: 'relative',
                zIndex: 1,
              }}
            />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
