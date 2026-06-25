import { useRef } from 'react'
import {
  motion,
  useScroll,
  useTransform,
  useReducedMotion,
} from 'framer-motion'

const STATS = [
  { big: '24/7', small: 'Always on' },
  { big: '200+', small: 'Integrations' },
  { big: '5 min', small: 'To deploy' },
]

const RAYS = [
  { angle: -28, opacity: 0.22, dur: 4.2 },
  { angle: -12, opacity: 0.32, dur: 5.8 },
  { angle:   6, opacity: 0.26, dur: 4.9 },
  { angle:  20, opacity: 0.18, dur: 6.5 },
]

export function Hero() {
  const prefersReduced = useReducedMotion()
  const containerRef = useRef<HTMLElement>(null)

  const { scrollY } = useScroll()
  const orbY = useTransform(scrollY, [0, 600], [0, prefersReduced ? 0 : -60])

  return (
    <section
      ref={containerRef}
      style={{
        minHeight: '100dvh',
        display: 'flex',
        alignItems: 'center',
        paddingTop: '4rem',
        paddingBottom: '6rem',
        position: 'relative',
        overflow: 'hidden',
        background: 'oklch(0.12 0.022 38)',
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
          background: 'radial-gradient(circle, rgba(200,148,60,0.14) 0%, transparent 70%)',
          animation: 'drift1 22s ease-in-out infinite',
          pointerEvents: 'none',
        }}
      />
      <div
        style={{
          position: 'absolute', top: '40%', right: '-15%',
          width: '45vw', height: '45vw', borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(200,148,60,0.10) 0%, transparent 70%)',
          animation: 'drift2 28s ease-in-out infinite',
          animationDelay: '-9s',
          pointerEvents: 'none',
        }}
      />
      <div
        style={{
          position: 'absolute', bottom: '-5%', left: '30%',
          width: '40vw', height: '40vw', borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(200,148,60,0.08) 0%, transparent 70%)',
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
            background: `linear-gradient(90deg, transparent 0%, rgba(210,155,65,${ray.opacity}) 40%, rgba(210,155,65,${ray.opacity * 0.4}) 70%, transparent 100%)`,
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

          {/* Chrome gradient H1 */}
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
            <span
              style={{
                background: 'linear-gradient(180deg, #ffffff 0%, #d8d8d8 28%, #9a9a9a 62%, #555555 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                display: 'inline',
              }}
            >
              Deploy a workforce that
            </span>
            <br />
            <span
              style={{
                background: 'linear-gradient(180deg, #c8c8c8 0%, #888888 50%, #444444 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                display: 'inline',
              }}
            >
              never sleeps.
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
              href="/#pricing"
              style={{
                background: 'linear-gradient(180deg, oklch(0.74 0.16 58) 0%, oklch(0.62 0.18 55) 100%)',
                color: 'oklch(0.10 0.02 38)',
                border: 'none',
                cursor: 'pointer',
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.9375rem',
                fontWeight: 600,
                padding: '0.75rem 1.5rem',
                borderRadius: '9999px',
                boxShadow: 'inset 0 1px 0 rgba(255,225,160,0.35), 0 4px 20px oklch(0.62 0.16 58 / 0.50)',
                transition: 'opacity 0.2s ease, transform 0.15s ease',
                textDecoration: 'none',
                display: 'inline-block',
              }}
              onMouseEnter={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.opacity = '0.88'
                ;(e.currentTarget as HTMLAnchorElement).style.transform = 'scale(1.02)'
              }}
              onMouseLeave={(e) => {
                ;(e.currentTarget as HTMLAnchorElement).style.opacity = '1'
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
            y: orbY,
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
              background: 'radial-gradient(circle, rgba(180,130,55,0.12) 0%, transparent 70%)',
              filter: 'blur(60px)',
              pointerEvents: 'none',
            }}
          />
          <motion.div
            initial={prefersReduced ? false : { scale: 0.86, opacity: 0 }}
            whileInView={prefersReduced ? {} : { scale: 1, opacity: 1 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
            style={{ position: 'relative', width: '100%', maxWidth: '520px' }}
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
