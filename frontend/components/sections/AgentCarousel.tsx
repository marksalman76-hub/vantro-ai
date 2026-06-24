'use client'
// v3
import React, { useEffect, useRef, useState } from 'react'

/* ── Agent data ────────────────────────────────────────────────────── */
const AGENTS = [
  { name: 'Atlas',  role: 'Sales',      stat: '847',  unit: 'leads qualified',   color: '#7C3AED' },
  { name: 'Hermes', role: 'Support',    stat: '4.2k', unit: 'tickets resolved',   color: '#06B6D4' },
  { name: 'Oracle', role: 'Research',   stat: '127',  unit: 'reports generated',  color: '#3B82F6' },
  { name: 'Muse',   role: 'Marketing',  stat: '23k',  unit: 'posts scheduled',    color: '#EC4899' },
  { name: 'Nexus',  role: 'Operations', stat: '1.4k', unit: 'workflows automated', color: '#22C55E' },
]

const CARD_VIDEOS = [
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260506_030111_a9e15665-d379-4a7f-8116-695bbe452ad1.mp4',
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260429_171347_f640c30d-ec21-426a-98bc-77e07c2c60cb.mp4',
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260503_104800_bc43ae09-f494-43e3-97d7-2f8c1692cfd7.mp4',
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260423_161253_c72b1869-400f-45ed-ac0c-52f68c2ed5bd.mp4',
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260418_115655_b4d9cd77-feed-43cd-a198-af78ebdf1f7a.mp4',
]

/* ── Smoothstep easing ─────────────────────────────────────────────── */
function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t
}

/* ── AgentCard ─────────────────────────────────────────────────────── */
function AgentCard({ agent, videoSrc, active }: {
  agent: typeof AGENTS[0]
  videoSrc: string
  active: boolean
}) {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const v = videoRef.current
    if (!v) return
    if (active) { v.play().catch(() => {}) }
    else v.pause()
  }, [active])

  return (
    <div
      className="relative w-full h-full overflow-hidden rounded-2xl"
      style={{
        border: `1px solid rgba(255,255,255,0.10)`,
        background: 'rgba(8,10,20,0.85)',
        boxShadow: active
          ? `0 0 40px ${agent.color}55, 0 30px 60px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08)`
          : '0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05)',
        transition: 'box-shadow 0.6s ease',
      }}
    >
      {/* Video background */}
      <video
        ref={videoRef}
        src={videoSrc}
        muted
        loop
        playsInline
        preload="none"
        className="absolute inset-0 w-full h-full object-cover opacity-40"
        style={{ mixBlendMode: 'luminosity' }}
      />

      {/* Gradient overlays */}
      <div
        className="absolute inset-0"
        style={{
          background: `linear-gradient(135deg, ${agent.color}18 0%, transparent 60%, rgba(0,0,0,0.6) 100%)`,
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-black/20" />

      {/* Content */}
      <div className="relative z-10 h-full flex flex-col justify-between p-6">
        {/* Top row */}
        <div className="flex items-start justify-between">
          {/* Agent name */}
          <p
            className="text-[11px] font-mono tracking-[0.15em] uppercase"
            style={{ color: `${agent.color}` }}
          >
            {agent.role} Agent
          </p>
          {/* Status */}
          <div className="flex items-center gap-1.5">
            <span
              className="relative flex h-2 w-2"
            >
              <span
                className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                style={{ backgroundColor: agent.color }}
              />
              <span
                className="relative inline-flex rounded-full h-2 w-2"
                style={{ backgroundColor: agent.color }}
              />
            </span>
            <span className="text-[10px] font-mono text-white/40">ACTIVE</span>
          </div>
        </div>

        {/* Center: agent name large */}
        <div>
          <h3
            className="font-sans font-light text-white leading-none tracking-[-0.04em]"
            style={{ fontSize: 'clamp(32px, 4vw, 48px)' }}
          >
            {agent.name}
          </h3>
        </div>

        {/* Bottom row */}
        <div className="flex items-end justify-between">
          <div>
            <p className="text-[26px] font-semibold text-white leading-none">{agent.stat}</p>
            <p className="text-[10px] text-white/40 tracking-wider mt-1 uppercase">{agent.unit}</p>
          </div>
          {/* Vantro star mark */}
          <svg width="18" height="18" viewBox="0 0 24 24" fill="rgba(255,255,255,0.15)" aria-hidden="true">
            <path d="M12 2L14.09 8.26L20.28 9.27L16.14 13.3L17.18 19.5L12 16.77L6.82 19.5L7.86 13.3L3.72 9.27L9.91 8.26L12 2Z" />
          </svg>
        </div>
      </div>

      {/* Volumetric top edge highlight */}
      <div
        className="absolute top-0 left-[8%] right-[8%] h-px"
        style={{ background: `linear-gradient(90deg, transparent, ${agent.color}60, transparent)` }}
      />
    </div>
  )
}

/* ── AgentCarousel ─────────────────────────────────────────────────── */
export default function AgentCarousel() {
  const containerRef = useRef<HTMLDivElement>(null)
  const sceneRef     = useRef<HTMLDivElement>(null)
  const rafRef       = useRef<number>(0)

  /* Carousel state (mutable, not reactive — drives RAF loop) */
  const angleRef     = useRef(0)        // current rotation angle (radians)
  const targetAngle  = useRef(0)        // target (increments per frame)
  const mouseX       = useRef(0)
  const mouseY       = useRef(0)
  const tiltX        = useRef(0)        // current tilt (smooth)
  const tiltY        = useRef(0)

  const [activeIdx, setActiveIdx]  = useState(0)
  const N = AGENTS.length

  /* Card geometry */
  const CARD_W  = 340
  const CARD_H  = 210
  const RADIUS  = 180

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    /* Mouse parallax */
    const onMouse = (e: MouseEvent) => {
      const rect   = container.getBoundingClientRect()
      const cx     = rect.left + rect.width  / 2
      const cy     = rect.top  + rect.height / 2
      mouseX.current = (e.clientX - cx) / (rect.width  / 2)   // -1…1
      mouseY.current = (e.clientY - cy) / (rect.height / 2)   // -1…1
    }
    container.addEventListener('mousemove', onMouse)

    /* RAF loop */
    const SPEED = 0.0006  // radians per ms

    let lastTime = 0
    const tick = (now: number) => {
      const dt = Math.min(now - lastTime, 50)
      lastTime = now

      /* Advance target angle (continuous spin) */
      targetAngle.current += SPEED * dt

      /* Smooth current angle toward target */
      angleRef.current = lerp(angleRef.current, targetAngle.current, 0.06)

      /* Smooth tilt toward mouse */
      tiltX.current = lerp(tiltX.current, mouseY.current * 12, 0.05)  // deg
      tiltY.current = lerp(tiltY.current, mouseX.current * 8, 0.05)

      /* Determine front-facing card (smallest angular distance to 0 mod 2π) */
      const normalised = ((angleRef.current % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2)
      const front = Math.round((normalised / (Math.PI * 2)) * N) % N
      setActiveIdx(front)

      /* Apply transforms to scene cards */
      const scene = sceneRef.current
      if (!scene) { rafRef.current = requestAnimationFrame(tick); return }

      scene.style.transform = `rotateX(${-tiltX.current}deg) rotateY(${tiltY.current}deg)`

      const cards = scene.querySelectorAll<HTMLElement>('[data-card-idx]')
      cards.forEach((card) => {
        const i     = parseInt(card.dataset.cardIdx || '0')
        const angle = (i / N) * Math.PI * 2 + angleRef.current

        /* Cylinder: rotateX positions cards in a vertical wheel, translateZ pushes out */
        const tx = 0
        const ty = -RADIUS * Math.sin(angle)
        const tz =  RADIUS * Math.cos(angle)
        const rx = -angle * (180 / Math.PI)  // rotate card to face outward

        /* Depth-based opacity and scale */
        const cosAngle = Math.cos(angle)
        /* Only show front half — back-facing cards fade to 0 (kills reversed-text ghost) */
        const opacity  = Math.max(0, cosAngle)
        const scale    = 0.75 + 0.25 * ((cosAngle + 1) / 2)

        card.style.transform  = `translate3d(${tx}px, ${ty}px, ${tz}px) rotateX(${rx}deg)`
        card.style.opacity    = String(opacity)
        card.style.zIndex     = String(Math.round(cosAngle * 100 + 100))

        /* Volumetric thickness: push depth layers */
        const thickness = card.querySelector<HTMLElement>('[data-thickness]')
        if (thickness) {
          thickness.style.transform = `translate3d(0, 0, -4px)`
          thickness.style.opacity   = String(opacity * 0.5)
        }
      })

      rafRef.current = requestAnimationFrame(tick)
    }

    rafRef.current = requestAnimationFrame(tick)

    return () => {
      cancelAnimationFrame(rafRef.current)
      container.removeEventListener('mousemove', onMouse)
    }
  }, [N])

  /* Manual card select */
  const selectCard = (i: number) => {
    const currentAngle = ((angleRef.current % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2)
    const frontAngle   = (i / N) * Math.PI * 2
    let   delta        = frontAngle - currentAngle
    /* Take shortest path */
    if (delta >  Math.PI) delta -= Math.PI * 2
    if (delta < -Math.PI) delta += Math.PI * 2
    targetAngle.current = angleRef.current + delta
  }

  return (
    <section
      id="agents"
      className="relative overflow-hidden"
      style={{
        background: 'linear-gradient(to bottom, rgb(7,11,26), rgb(11,15,25))',
      }}
    >
      {/* Ambient glow — right-biased */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 45% 70% at 75% 50%, rgba(124,58,237,0.07) 0%, transparent 70%)',
        }}
      />

      {/* ── Mobile carousel (lg:hidden) ──────────────────────── */}
      <div className="lg:hidden relative px-4 pt-28 pb-16">
        <div className="mb-10 text-center">
          <p className="text-[11px] font-mono tracking-[0.18em] text-white/30 uppercase mb-4">
            Your AI Workforce
          </p>
          <h2
            className="font-sans font-light text-white leading-tight tracking-[-0.03em] mb-4"
            style={{ fontSize: '38px' }}
          >
            Meet the <span className="text-white/40">agents</span>
          </h2>
          <p className="text-sm text-white/40 leading-relaxed max-w-xs mx-auto">
            Specialist AI workers — trained for one domain, running 24/7.
          </p>
        </div>

        {/* Scroll-snap horizontal cards */}
        <div
          className="flex overflow-x-auto gap-4 pb-4 snap-x snap-mandatory"
          style={{ scrollbarWidth: 'none', WebkitOverflowScrolling: 'touch' } as React.CSSProperties}
        >
          {AGENTS.map((agent, i) => (
            <div
              key={agent.name}
              className="snap-center shrink-0"
              style={{ width: '288px', height: '180px' }}
            >
              <AgentCard agent={agent} videoSrc={CARD_VIDEOS[i]} active={false} />
            </div>
          ))}
        </div>

        {/* Dot indicators */}
        <div className="flex justify-center gap-2 mt-5">
          {AGENTS.map((agent, i) => (
            <div
              key={i}
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: 'rgba(255,255,255,0.18)' }}
            />
          ))}
        </div>
      </div>

      {/* ── Desktop 3D (hidden on mobile) ─────────────────────── */}
      <div className="hidden lg:block relative" style={{ minHeight: '900px' }}>
        {/* 3D Carousel — absolute, right half, vertically centered */}
        <div
          ref={containerRef}
          className="absolute"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translateY(-50%)',
            width:    `${CARD_W + 80}px`,
            height:   `${CARD_H + RADIUS * 2 + 40}px`,
            perspective: '800px',
            perspectiveOrigin: '50% 50%',
            cursor: 'grab',
          }}
        >
          <div
            ref={sceneRef}
            className="absolute inset-0"
            style={{ transformStyle: 'preserve-3d' }}
          >
            <div
              className="absolute"
              style={{
                top: '50%', left: '50%',
                width: 0, height: 0,
                transformStyle: 'preserve-3d',
              }}
            >
              {AGENTS.map((agent, i) => (
                <div
                  key={agent.name}
                  data-card-idx={String(i)}
                  onClick={() => selectCard(i)}
                  style={{
                    position: 'absolute',
                    width:  `${CARD_W}px`,
                    height: `${CARD_H}px`,
                    top:    `-${CARD_H / 2}px`,
                    left:   `-${CARD_W / 2}px`,
                    transformStyle: 'preserve-3d',
                    willChange: 'transform, opacity',
                    cursor: 'pointer',
                  }}
                >
                  <div className="absolute inset-0" style={{ backfaceVisibility: 'hidden' }}>
                    <AgentCard agent={agent} videoSrc={CARD_VIDEOS[i]} active={activeIdx === i} />
                  </div>
                  <div
                    data-thickness="true"
                    className="absolute inset-0 rounded-2xl"
                    style={{
                      backfaceVisibility: 'hidden',
                      background: 'rgba(0,0,0,0.9)',
                      border: '1px solid rgba(255,255,255,0.04)',
                    }}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Content — left side, z-10 above the 3D scene */}
        <div
          className="relative z-10 max-w-7xl mx-auto px-8 md:px-16 lg:px-20"
          style={{ minHeight: '900px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
        >
          <div className="max-w-[460px]">
            <p className="text-[11px] font-mono tracking-[0.18em] text-white/30 uppercase mb-5">
              Your AI Workforce
            </p>
            <h2
              className="font-sans font-light text-white leading-[1.0] tracking-[-0.03em] mb-6"
              style={{ fontSize: 'clamp(36px, 5vw, 64px)' }}
            >
              Meet the<br />
              <span className="text-white/40">agents</span>
            </h2>
            <p className="text-[15px] text-white/45 leading-relaxed mb-10 max-w-[360px]">
              Each Vantro agent is a specialized AI worker — trained for one domain,
              running 24/7, reporting in real time.
            </p>

            {/* Selector pills */}
            <div className="flex items-center gap-2.5 flex-wrap">
              {AGENTS.map((agent, i) => (
                <button
                  key={agent.name}
                  onClick={() => selectCard(i)}
                  className="flex items-center gap-2 px-4 py-2 rounded-full text-[11px] font-mono tracking-wider transition-all duration-300"
                  style={{
                    background: activeIdx === i ? `${agent.color}20` : 'rgba(255,255,255,0.04)',
                    border:     `1px solid ${activeIdx === i ? `${agent.color}50` : 'rgba(255,255,255,0.08)'}`,
                    color:      activeIdx === i ? agent.color : 'rgba(255,255,255,0.35)',
                    transform:  activeIdx === i ? 'scale(1.05)' : 'scale(1)',
                  }}
                >
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: activeIdx === i ? agent.color : 'rgba(255,255,255,0.2)' }}
                  />
                  {agent.name}
                </button>
              ))}
            </div>

            {/* Live stat */}
            <p className="mt-5 text-[11px] font-mono tracking-wider text-white/25 uppercase">
              {AGENTS[activeIdx].stat}&nbsp;{AGENTS[activeIdx].unit}&nbsp;this month
            </p>

            <a
              href="/dashboard/agents"
              className="inline-flex items-center gap-1.5 mt-8 text-[11px] font-mono tracking-[0.15em] uppercase text-white/25 hover:text-violet-400 transition-colors"
            >
              View all 27 agents →
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
