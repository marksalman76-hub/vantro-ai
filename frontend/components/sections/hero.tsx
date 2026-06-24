'use client'

import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowUpRight } from 'lucide-react'

/* ── Constants ─────────────────────────────────────────────────────── */
const VIDEO_URL =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260521_064421_279656fd-e76f-40a0-8fed-7456d4f7715a.mp4'

const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+'

const STATS = [
  { value: '500+', label: 'Teams Active' },
  { value: '2M+',  label: 'Tasks Automated' },
  { value: '40h',  label: 'Saved / Team / Month' },
]

/* ── ScrambleLine ──────────────────────────────────────────────────── */
function ScrambleLine({ text, trigger, delay = 0 }: { text: string; trigger: boolean; delay?: number }) {
  const [display, setDisplay] = useState(' '.repeat(text.length))
  const frameRef = useRef<number | null>(null)

  useEffect(() => {
    if (!trigger) return

    let startTime: number | null = null
    const duration = 900

    const animate = (ts: number) => {
      if (startTime === null) startTime = ts
      const elapsed = ts - startTime - delay
      if (elapsed < 0) { frameRef.current = requestAnimationFrame(animate); return }

      const t = Math.min(1, elapsed / duration)
      let result = ''

      for (let i = 0; i < text.length; i++) {
        if (text[i] === ' ') { result += ' '; continue }
        const threshold = i / text.length
        if (t >= threshold + 0.15) result += text[i]
        else if (t >= threshold - 0.1) result += GLYPHS[Math.floor(Math.random() * GLYPHS.length)]
        else result += ' '
      }

      setDisplay(result)
      if (t < 1) frameRef.current = requestAnimationFrame(animate)
      else setDisplay(text)
    }

    frameRef.current = requestAnimationFrame(animate)
    return () => { if (frameRef.current) cancelAnimationFrame(frameRef.current) }
  }, [trigger, text, delay])

  return <span className="inline-block">{display}</span>
}

/* ── Vantro mark SVG ───────────────────────────────────────────────── */
function VantroMark() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="rgba(255,255,255,0.4)" aria-hidden="true">
      <path d="M12 2L14.09 8.26L20.28 9.27L16.14 13.3L17.18 19.5L12 16.77L6.82 19.5L7.86 13.3L3.72 9.27L9.91 8.26L12 2Z" />
    </svg>
  )
}

/* ── Hero ──────────────────────────────────────────────────────────── */
export default function Hero() {
  const videoRef   = useRef<HTMLVideoElement>(null)
  const sectionRef = useRef<HTMLDivElement>(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [arrowHover, setArrowHover] = useState(0)

  /* Video load */
  useEffect(() => {
    const video = videoRef.current
    if (!video) return
    const onCanPlay = () => setIsLoaded(true)
    video.addEventListener('canplaythrough', onCanPlay)
    video.load()
    return () => video.removeEventListener('canplaythrough', onCanPlay)
  }, [])

  /* Scroll → video scrub  (WISA-pattern: video.seeking guard) */
  useEffect(() => {
    if (!isLoaded) return
    const video   = videoRef.current
    const section = sectionRef.current
    if (!video || !section) return

    /* wait one tick so duration is ready */
    const tid = setTimeout(() => {
      const handleScroll = () => {
        if (video.seeking || !video.duration) return
        const rect    = section.getBoundingClientRect()
        const scrolled = -rect.top                          // px past section top
        const max     = section.offsetHeight - window.innerHeight
        const t       = Math.max(0, Math.min(1, scrolled / Math.max(1, max)))
        video.currentTime = t * video.duration
      }
      window.addEventListener('scroll', handleScroll, { passive: true })
      handleScroll()
      return () => window.removeEventListener('scroll', handleScroll)
    }, 100)

    return () => clearTimeout(tid)
  }, [isLoaded])

  return (
    /*
     * min-h-[200vh] + sticky inner:
     * Section is tall so scroll drives the scrub; the viewport content stays
     * pinned via sticky until the section scrolls out.
     */
    <section ref={sectionRef} className="relative min-h-[200vh] w-full">

      {/* ── Pinned viewport ─────────────────────────────────────────── */}
      <div className="sticky top-0 h-screen w-full overflow-hidden">

        {/* Video */}
        <video
          ref={videoRef}
          muted
          playsInline
          preload="metadata"
          poster=""
          className="absolute inset-0 w-full h-full object-cover"
          src={VIDEO_URL}
        />

        {/* Gradient overlays */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/55 via-black/15 to-black/75 pointer-events-none" />
        <div
          className="absolute bottom-0 left-0 w-full h-40 pointer-events-none"
          style={{ background: 'linear-gradient(to top, rgb(11,15,25), transparent)' }}
        />

        {/* Dot grid (SynapseX ambient) */}
        <div
          className="absolute inset-0 pointer-events-none opacity-[0.04]"
          style={{
            backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)',
            backgroundSize: '24px 24px',
          }}
        />

        {/* Loading screen */}
        {!isLoaded && (
          <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-[#07091A]">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
              className="mb-8"
            >
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M12 2L14.09 8.26L20.28 9.27L16.14 13.3L17.18 19.5L12 16.77L6.82 19.5L7.86 13.3L3.72 9.27L9.91 8.26L12 2Z"
                  stroke="url(#star-grad)" strokeWidth="1.5" strokeLinejoin="round"
                />
                <defs>
                  <linearGradient id="star-grad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#C084FC" />
                    <stop offset="100%" stopColor="#3B82F6" />
                  </linearGradient>
                </defs>
              </svg>
            </motion.div>
            <div className="w-40 h-px overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
              <motion.div
                className="h-full"
                initial={{ x: '-100%' }}
                animate={{ x: '100%' }}
                transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
                style={{ background: 'linear-gradient(90deg, transparent, #C084FC, #3B82F6, transparent)' }}
              />
            </div>
          </div>
        )}

        {/* ── Hero content ────────────────────────────────────────── */}
        <div className="relative z-10 h-full flex flex-col max-w-7xl mx-auto px-8 md:px-16 lg:px-20">

          {/* Navbar offset */}
          <div className="h-20 flex-shrink-0" />

          {/* Main title — SynapseX two-line scramble layout */}
          <div className="flex-1 flex items-center">
            <h1
              className="font-sans font-light text-white leading-[0.95] tracking-[-0.03em] select-none"
              style={{ fontSize: 'clamp(52px, 8vw, 104px)' }}
            >
              <ScrambleLine text="Deploy AI" trigger={isLoaded} delay={100} />
              <br />
              <ScrambleLine text="Agents" trigger={isLoaded} delay={300} />
            </h1>
          </div>

          {/* Bottom row — desc left / stats+CTA right */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 pb-10 md:pb-16">

            {/* Description */}
            <div className="flex flex-col gap-4 max-w-[380px]">
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={isLoaded ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.9, delay: 0.85, ease: [0.16, 1, 0.3, 1] }}
                className="text-[15px] text-white/55 leading-[1.65]"
              >
                Autonomous AI agents that handle sales, support, research, and operations 24/7.{' '}
                <span className="text-white/80 font-medium">No MLOps team required.</span>
              </motion.p>
              <motion.div
                initial={{ opacity: 0 }}
                animate={isLoaded ? { opacity: 1 } : {}}
                transition={{ duration: 0.8, delay: 1.2 }}
                className="flex items-center gap-4 flex-wrap"
              >
                {['No credit card', 'SOC 2 certified', 'Cancel any time'].map((t, i) => (
                  <span key={t} className="flex items-center gap-1.5 text-[10px] font-mono tracking-[0.1em] text-white/30 uppercase whitespace-nowrap">
                    <svg className="w-2.5 h-2.5 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/></svg>
                    {t}
                  </span>
                ))}
              </motion.div>
            </div>

            {/* Stats + CTA */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={isLoaded ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.9, delay: 1.05, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col items-start md:items-end gap-6"
            >
              {/* Stats row */}
              <div className="flex gap-8 sm:gap-12">
                {STATS.map((s) => (
                  <div key={s.label}>
                    <p className="text-[24px] sm:text-[28px] font-semibold text-white leading-none">{s.value}</p>
                    <p className="text-[10px] text-white/35 uppercase tracking-[0.12em] mt-1 whitespace-nowrap">{s.label}</p>
                  </div>
                ))}
              </div>

              {/* WISA-style two-part CTA button */}
              <div className="flex items-stretch gap-[1px] group cursor-pointer">
                <Link
                  href="/signup"
                  className="flex items-center px-7 py-4 text-[11px] font-mono tracking-[-0.01em] text-white/85 transition-all duration-200 group-hover:bg-white group-hover:text-black"
                  style={{ background: 'rgba(255,255,255,0.08)', backdropFilter: 'blur(80px)' }}
                >
                  DEPLOY YOUR FIRST AGENT
                </Link>
                <button
                  className="flex items-center justify-center px-5 py-4 text-white transition-all duration-200 group-hover:bg-white group-hover:text-black overflow-hidden relative"
                  style={{ background: 'rgba(255,255,255,0.08)', backdropFilter: 'blur(80px)' }}
                  onMouseEnter={() => setArrowHover((n) => n + 1)}
                  onMouseLeave={() => setArrowHover((n) => n + 1)}
                  aria-label="Get started"
                >
                  {/* WISA fly-out / fly-in arrow animation */}
                  {arrowHover === 0 ? (
                    <ArrowUpRight className="w-4 h-4" />
                  ) : (
                    <>
                      <span
                        key={`out-${arrowHover}`}
                        className="absolute"
                        style={{ animation: 'flyOutRight 0.5s cubic-bezier(0.4,0,0.2,1) forwards' }}
                      >
                        <ArrowUpRight className="w-4 h-4" />
                      </span>
                      <span
                        key={`in-${arrowHover}`}
                        style={{ animation: 'flyInLeft 0.5s cubic-bezier(0.4,0,0.2,1) forwards' }}
                      >
                        <ArrowUpRight className="w-4 h-4" />
                      </span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </div>

          {/* Edge anchors (mentality-pattern, adapted) */}
          <div className="absolute right-8 md:right-16 top-1/2 -translate-y-1/2 hidden lg:flex flex-col items-center gap-3">
            <div
              className="flex items-center gap-2 px-2.5 py-1.5 rounded-full text-[10px] font-mono tracking-widest"
              style={{
                background: 'rgba(255,255,255,0.08)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(255,255,255,0.08)',
                color: 'rgba(255,255,255,0.35)',
              }}
            >
              <VantroMark />
              <span>v2.0</span>
            </div>
          </div>

          <div className="absolute bottom-10 left-8 md:left-16 hidden md:block">
            <span className="text-[10px] font-mono tracking-[0.15em] text-white/20 uppercase">2025</span>
          </div>

          <div className="absolute bottom-10 right-8 md:right-16 hidden md:block">
            <span className="text-[10px] font-mono tracking-[0.15em] text-white/20 uppercase">ai agent platform</span>
          </div>
        </div>
      </div>

      {/* ── Cinematic paragraph (SynapseX §1.5) ────────────────────── */}
      <div
        className="relative z-10 flex items-center justify-center px-8 md:px-16"
        style={{ height: '100vh', background: 'linear-gradient(to bottom, rgb(11,15,25) 0%, rgb(7,11,26) 100%)' }}
      >
        <p
          className="max-w-[900px] text-center font-sans font-light text-white/75 leading-[1.35] tracking-[-0.02em]"
          style={{ fontSize: 'clamp(20px, 3vw, 40px)' }}
        >
          A multi-agent intelligence layer built on the architecture of autonomous AI.
          Vantro dispatches specialized agents — each trained for one domain, each running
          24/7. Every task becomes measurable, structured, and visible.{' '}
          <span className="text-white/90">Operational noise filters into revenue.</span>
        </p>
      </div>
    </section>
  )
}
