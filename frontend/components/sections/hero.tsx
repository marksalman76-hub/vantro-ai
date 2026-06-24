'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import { Swiper, SwiperSlide } from 'swiper/react'
import { EffectCoverflow } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/effect-coverflow'
import s from './hero.module.css'

const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+~|}{[]:;?><'

const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260613_120544_a609e0c2-e52d-4bd5-b10f-b66ac51f1965.mp4'

const STATS = [
  { title: 'TEAMS ACTIVE',        value: '500+',   footer: 'AI AGENTS DEPLOYED GLOBALLY',    details: ['Multi-tenant workspace isolation', 'Real-time agent health monitoring', '24/7 autonomous execution'] },
  { title: 'TASKS AUTOMATED',     value: '2M+',    footer: 'TASKS EXECUTED THIS QUARTER',    details: ['Multi-step workflow completion', 'Cross-platform action execution', 'Zero human intervention required'] },
  { title: 'HOURS SAVED',         value: '40h',    footer: 'SAVED PER TEAM PER MONTH',       details: ['Sales SDR workflows automated', 'Support ticket resolution 10×', 'Research reports in minutes'] },
  { title: 'PREDICTION ACCURACY', value: '93%',    footer: 'FORECAST ACCURACY RATE',         details: ['Reinforced gradient mapping', 'Low latency model resolution', 'Adaptive feedback system'] },
  { title: 'EPOCH LATENCY',       value: '0.4ms',  footer: 'AGENT RESPONSE SPEED',           details: ['Hardware accelerated pipeline', 'Direct execution on task receipt', 'Sub-millisecond job dispatch'] },
  { title: 'UPTIME SLA',          value: '99.9%',  footer: 'PRODUCTION RELIABILITY',         details: ['Multi-region failover active', 'Continuous health checks', 'Zero-downtime deployments'] },
]

// [text, delay, side]
const LINES: [string, number, 'left' | 'right'][] = [
  ['Deploy AI',  100, 'left'],
  ['Agents',     300, 'left'],
  ['That Work',  200, 'right'],
  ['For You',    400, 'right'],
]

export default function Hero() {
  const videoRef        = useRef<HTMLVideoElement>(null)
  const headerRef       = useRef<HTMLElement>(null)
  const mainRef         = useRef<HTMLElement>(null)
  const heroRef         = useRef<HTMLDivElement>(null)
  const heroDescRef     = useRef<HTMLDivElement>(null)
  const cinematicRef    = useRef<HTMLDivElement>(null)
  const statsRef        = useRef<HTMLDivElement>(null)
  const menuPillRef     = useRef<HTMLDivElement>(null)
  const menuPillMRef    = useRef<HTMLDivElement>(null)
  const logoPillMRef    = useRef<HTMLAnchorElement>(null)
  const scrambleRefs    = useRef<(HTMLSpanElement | null)[]>([])

  useEffect(() => {
    if (!videoRef.current || !headerRef.current || !mainRef.current || !heroRef.current || !heroDescRef.current || !cinematicRef.current || !statsRef.current) return
    const video        = videoRef.current
    const header       = headerRef.current
    const mainContent  = mainRef.current
    const heroSection  = heroRef.current
    const heroDesc     = heroDescRef.current
    const cinematic    = cinematicRef.current
    const statsSection = statsRef.current

    let scrollY      = 0
    let smoothScroll = 0
    let entrancePhase: 'loading' | 'animating' | 'complete' = 'loading'
    let entranceStart = 0
    let videoReady   = false
    let rafId        = 0
    let isSeeking    = false
    let nextSeekTime: number | null = null
    let statsRevealed = false

    // Scramble state
    interface ScrambleState {
      el: HTMLSpanElement
      text: string
      delay: number
      phase: 'idle' | 'scrambling-in' | 'revealed' | 'scrambling-out' | 'hidden'
      progress: number
      lastTime: number
      started: boolean
    }
    const scrambles: ScrambleState[] = LINES.map((line, i) => ({
      el: scrambleRefs.current[i]!,
      text: line[0],
      delay: line[1],
      phase: 'idle' as const,
      progress: 0,
      lastTime: 0,
      started: false,
    })).filter(s => s.el != null)

    // Scroll tracking
    function onScroll() { scrollY = window.scrollY }
    window.addEventListener('scroll', onScroll, { passive: true })
    scrollY = window.scrollY

    // Stats reveal on scroll
    function checkStats() {
      if (statsRevealed || !statsSection) return
      const rect = statsSection.getBoundingClientRect()
      if (rect.top < window.innerHeight * 0.9) {
        statsRevealed = true
        statsSection.classList.add(s.revealed)
      }
    }
    window.addEventListener('scroll', checkStats, { passive: true })

    // Video seeking
    video.addEventListener('seeking', () => { isSeeking = true })
    video.addEventListener('seeked', () => {
      isSeeking = false
      if (nextSeekTime !== null) {
        const t = nextSeekTime; nextSeekTime = null
        if (video.readyState >= 1 && video.duration > 0) { isSeeking = true; video.currentTime = t }
      }
    })
    video.addEventListener('loadedmetadata', () => { video.autoplay = false; video.pause() })
    video.autoplay = false; video.pause()

    // Safety timeout
    const safeTimeout = setTimeout(() => {
      if (entrancePhase === 'loading') {
        entrancePhase = 'animating'
        entranceStart = performance.now()
      }
    }, 3500)

    function updateScrambles(now: number) {
      const heroHeight = heroSection.offsetHeight || window.innerHeight * 3
      const scrollNorm = Math.min(1, scrollY / heroHeight)
      const scrollActive = scrollNorm > 0.015

      scrambles.forEach(sc => {
        if (!videoReady && sc.phase === 'idle') return

        if (videoReady && sc.phase === 'idle' && !scrollActive && !sc.started) {
          sc.started = true
          setTimeout(() => {
            sc.phase = 'scrambling-in'; sc.progress = 0; sc.lastTime = now
          }, sc.delay)
          return
        }

        if (scrollActive && (sc.phase === 'revealed' || sc.phase === 'scrambling-in')) {
          sc.phase = 'scrambling-out'; sc.progress = 0; sc.lastTime = now
        } else if (!scrollActive && (sc.phase === 'hidden' || sc.phase === 'scrambling-out')) {
          sc.phase = 'scrambling-in'; sc.progress = 0; sc.lastTime = now
        }

        if (sc.phase === 'scrambling-in') {
          const dur = 900
          sc.progress = Math.min(1, sc.progress + (now - sc.lastTime) / dur)
          sc.lastTime = now
          const t = sc.progress
          let result = ''
          for (let i = 0; i < sc.text.length; i++) {
            if (sc.text[i] === ' ') { result += ' '; continue }
            const threshold = i / sc.text.length
            if (t >= threshold + 0.15)       result += sc.text[i]
            else if (t >= threshold - 0.1)   result += GLYPHS[Math.floor(Math.random() * GLYPHS.length)]
            else                              result += ' '
          }
          sc.el.textContent = result
          sc.el.style.opacity = '1'
          if (t >= 1) { sc.phase = 'revealed'; sc.el.textContent = sc.text }

        } else if (sc.phase === 'scrambling-out') {
          const dur = 700
          sc.progress = Math.min(1, sc.progress + (now - sc.lastTime) / dur)
          sc.lastTime = now
          const t = sc.progress
          let result = ''
          for (let i = 0; i < sc.text.length; i++) {
            if (sc.text[i] === ' ') { result += ' '; continue }
            const threshold = i / sc.text.length
            if (t >= threshold + 0.2)        result += ' '
            else if (t >= threshold - 0.05)  result += GLYPHS[Math.floor(Math.random() * GLYPHS.length)]
            else                             result += sc.text[i]
          }
          sc.el.textContent = result
          sc.el.style.opacity = String(Math.max(0, 1 - t * 1.5))
          if (t >= 1) {
            sc.phase = 'hidden'
            sc.el.textContent = sc.text.replace(/\S/g, ' ')
            sc.el.style.opacity = '0'
          }
        }
      })
    }

    let heroDescEntered = false

    function tick(now: number) {
      // Smooth lerp
      smoothScroll += (scrollY - smoothScroll) * 0.12
      if (Math.abs(scrollY - smoothScroll) < 0.0001) smoothScroll = scrollY

      // Hero-relative scroll progress (0→1 over hero section height)
      const heroHeight = heroSection.offsetHeight || window.innerHeight * 3
      const scrollNorm = Math.min(1, smoothScroll / heroHeight)

      // Video blur / scale
      const subtleBase = Math.max(0, Math.min(1, (scrollNorm - 0.1) / 0.45))
      const progressive = Math.max(0, Math.min(1, (scrollNorm - 0.55) / 0.4))
      const blurVal = subtleBase * 5 + progressive * 50
      const scaleVal = 1.03 + Math.max(0, Math.min(1, (scrollNorm - 0.1) / 0.9)) * 0.08

      // Entrance animation
      let eZoom = 1.0, eOpacity = 1.0
      if (entrancePhase === 'loading') {
        eZoom = 1.12; eOpacity = 0
        if (video.readyState >= 3) { entrancePhase = 'animating'; entranceStart = now }
      }
      if (entrancePhase === 'animating') {
        const elapsed = now - entranceStart
        const prog = Math.min(1, elapsed / 1400)
        const ease = 1 - Math.pow(1 - prog, 3)
        eZoom = 1.12 - 0.12 * ease
        eOpacity = Math.min(1.0, elapsed / 500)
        if (prog >= 1) {
          entrancePhase = 'complete'; videoReady = true
          header.classList.add(s.visible)
          mainContent.classList.add(s.visible)
        }
      }
      if (entrancePhase === 'complete' && !videoReady) {
        videoReady = true
        header.classList.add(s.visible)
        mainContent.classList.add(s.visible)
      }

      video.style.filter = `blur(${blurVal}px)`
      video.style.transform = `scale(${scaleVal * eZoom})`
      video.style.opacity = String(eOpacity)

      // Video seek
      if (video.readyState >= 1 && video.duration > 0) {
        const target = Math.max(0, Math.min(video.duration, scrollNorm * video.duration))
        if (Math.abs(video.currentTime - target) > 0.008) {
          if (!isSeeking && !video.seeking) { isSeeking = true; video.currentTime = target }
          else { nextSeekTime = target }
        }
      }

      // Hero fade / scale
      const heroOp = Math.max(0, Math.min(1, 1 - scrollNorm / 0.26))
      const heroSc = 1 - (1 - 0.96) * Math.min(1, scrollNorm / 0.26)
      heroSection.style.opacity = String(heroOp)
      heroSection.style.transform = `scale(${heroSc})`

      // Desc fade
      const descOp = Math.max(0, Math.min(1, 1 - scrollNorm / 0.12))
      const descY  = -30 * Math.min(1, scrollNorm / 0.12)
      heroDesc.style.opacity = String(descOp)
      heroDesc.style.transform = `translateY(${descY}px)`

      // Cinematic paragraph
      const scrollPx = smoothScroll
      const yVal = -120 * Math.min(1, scrollPx / 1000)
      let cinOp = 0
      if (scrollNorm <= 0.08)       cinOp = 0
      else if (scrollNorm <= 0.22)  cinOp = (scrollNorm - 0.08) / (0.22 - 0.08)
      else if (scrollNorm <= 0.42)  cinOp = 1
      else if (scrollNorm <= 0.65)  cinOp = 1 - (scrollNorm - 0.42) / (0.65 - 0.42)
      else                          cinOp = 0
      cinematic.style.transform = `rotateX(24deg) translateY(${yVal}px) translateZ(15px)`
      cinematic.style.opacity = String(Math.max(0, Math.min(1, cinOp)))

      // Scrambles
      updateScrambles(now)

      // Hero desc entrance
      if (videoReady && !heroDescEntered) {
        heroDescEntered = true
        heroDesc.style.transition = 'opacity 0.9s cubic-bezier(0.215,0.61,0.355,1) 0.2s, transform 0.9s cubic-bezier(0.215,0.61,0.355,1) 0.2s'
        heroDesc.style.opacity = '1'
        heroDesc.style.transform = 'translateY(0)'
      }

      rafId = requestAnimationFrame(tick)
    }

    heroDesc.style.opacity = '0'
    heroDesc.style.transform = 'translateY(25px)'
    rafId = requestAnimationFrame(tick)
    checkStats()

    // Lenis (desktop only)
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768
    let lenisInstance: { destroy: () => void } | null = null
    if (!isMobile) {
      import('lenis').then(({ default: Lenis }) => {
        lenisInstance = new Lenis({
          duration: 1.2,
          easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
          smoothWheel: true,
        }) as unknown as { destroy: () => void }
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ;(lenisInstance as any).on('scroll', () => { scrollY = window.scrollY })
        const raf = (time: number) => { (lenisInstance as any).raf(time); requestAnimationFrame(raf) }
        requestAnimationFrame(raf)
      }).catch(() => null)
    }

    return () => {
      cancelAnimationFrame(rafId)
      clearTimeout(safeTimeout)
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('scroll', checkStats)
      lenisInstance?.destroy()
    }
  }, [])

  // Hamburger handlers
  function toggleMenu() {
    menuPillRef.current?.classList.toggle(s.open)
  }
  function toggleMobileMenu() {
    const pill = menuPillMRef.current
    const logo = logoPillMRef.current
    if (!pill || !logo) return
    pill.classList.toggle(s.open)
    logo.classList.toggle(s.collapsed, pill.classList.contains(s.open))
  }
  function closeMobileMenu() {
    menuPillMRef.current?.classList.remove(s.open)
    logoPillMRef.current?.classList.remove(s.collapsed)
  }

  return (
    <>
      {/* Fixed video background */}
      <div className={s.videoLayer}>
        <video ref={videoRef} loop muted playsInline preload="auto" src={VIDEO_URL} />
      </div>

      {/* Bottom blur */}
      <div className={s.bottomBlur} />

      {/* Header */}
      <header ref={headerRef} className={s.mainHeader}>
        {/* Desktop */}
        <div className={`${s.desktopHeader}`} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', height: '100%' }}>
          <div className={s.headerLeft}>
            <Link href="/" className={s.logoPill}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="white" aria-hidden="true">
                <path d="M12 2L14.09 8.26L20.28 9.27L16.14 13.3L17.18 19.5L12 16.77L6.82 19.5L7.86 13.3L3.72 9.27L9.91 8.26L12 2Z" />
              </svg>
              <span>Vantro</span>
            </Link>
            <div ref={menuPillRef} className={s.menuPill}>
              <button className={s.hamburgerBtn} onClick={toggleMenu} aria-label="Toggle menu">
                <div className={s.hamburgerIcon}>
                  <span /><span /><span />
                </div>
              </button>
              <div className={s.menuLinks}>
                <Link href="#agents"       onClick={toggleMenu}>Agents</Link>
                <Link href="#integrations" onClick={toggleMenu}>Integrations</Link>
                <Link href="/pricing"      onClick={toggleMenu}>Pricing</Link>
              </div>
            </div>
          </div>
          <Link href="/signup" className={s.ctaBtn}>
            <span>Get Started</span>
          </Link>
        </div>

        {/* Mobile */}
        <div className={s.mobileHeader}>
          <div className={s.mobileLeft}>
            <Link ref={logoPillMRef} href="/" className={s.logoPillM}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="white" aria-hidden="true">
                <path d="M12 2L14.09 8.26L20.28 9.27L16.14 13.3L17.18 19.5L12 16.77L6.82 19.5L7.86 13.3L3.72 9.27L9.91 8.26L12 2Z" />
              </svg>
              <span>Vantro</span>
            </Link>
            <div ref={menuPillMRef} className={s.menuPillM}>
              <button className={s.hamburgerBtnM} onClick={toggleMobileMenu} aria-label="Toggle mobile menu">
                <div className={s.hamburgerIconM}>
                  <span /><span /><span />
                </div>
              </button>
              <div className={s.menuLinksM}>
                <Link href="#agents"  onClick={closeMobileMenu}>Agents</Link>
                <Link href="/pricing" onClick={closeMobileMenu}>Pricing</Link>
              </div>
            </div>
          </div>
          <Link href="/signup" className={s.ctaBtnM}>
            <span>Get Started</span>
          </Link>
        </div>
      </header>

      {/* Main content */}
      <main ref={mainRef} className={s.mainContent}>
        <div className={s.dotGrid} />

        {/* Hero */}
        <div ref={heroRef} className={s.heroSection}>
          <div style={{ width: '100%', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '48px' }}>
            <div className={s.heroGrid}>
              <div style={{ textAlign: 'left' }}>
                <div className={s.heroTitle}>
                  <span
                    className={s.scrambleLine}
                    ref={el => { scrambleRefs.current[0] = el }}
                    style={{ opacity: 0 }}
                  >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                  <span
                    className={s.scrambleLine}
                    ref={el => { scrambleRefs.current[1] = el }}
                    style={{ opacity: 0 }}
                  >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                </div>
              </div>
              <div />
            </div>

            <div className={s.heroGridBottom}>
              <div ref={heroDescRef} className={s.heroDesc}>
                <p>
                  Autonomous AI agents that handle sales, support, research, and operations 24/7.
                  No MLOps team required. Connect your tools, configure in plain English, go live today.
                </p>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', textAlign: 'right' }}>
                <div className={`${s.heroTitle} ${s.heroTitleRight}`}>
                  <span
                    className={s.scrambleLine}
                    ref={el => { scrambleRefs.current[2] = el }}
                    style={{ opacity: 0 }}
                  >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                  <span
                    className={s.scrambleLine}
                    ref={el => { scrambleRefs.current[3] = el }}
                    style={{ opacity: 0 }}
                  >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Cinematic paragraph */}
        <div className={s.cinematicSection}>
          <div ref={cinematicRef} className={s.cinematicInner} style={{ opacity: 0 }}>
            <h2>
              A multi-agent intelligence layer built on the architecture of autonomous AI.
              Vantro dispatches specialized agents — each trained for one domain, each running 24/7.
              Every task becomes measurable, structured, and visible.
              Operational noise filters into revenue.
            </h2>
          </div>
        </div>

        {/* Stats carousel */}
        <div ref={statsRef} className={s.statsSection}>
          <Swiper
            modules={[EffectCoverflow]}
            effect="coverflow"
            grabCursor
            slidesPerView="auto"
            centeredSlides
            loop
            spaceBetween={32}
            coverflowEffect={{ rotate: 30, stretch: 0, depth: 100, modifier: 1, slideShadows: false }}
          >
            {STATS.map((card) => (
              <SwiperSlide key={card.title} style={{ width: 380, maxWidth: '85%', height: 480 }}>
                <div className={s.statCardOuter}>
                  <div className={s.statCardInner}>
                    <div>
                      <div className={s.statTitle}>{card.title}</div>
                      <div className={s.statValue}>{card.value}</div>
                    </div>
                    <div className={s.statDetails}>
                      {card.details.map(d => (
                        <div key={d} className={s.statDetail}>
                          <span className={s.statDot} />
                          <span>{d}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className={s.statFooter}>{card.footer}</div>
                </div>
              </SwiperSlide>
            ))}
          </Swiper>
        </div>
      </main>
    </>
  )
}
