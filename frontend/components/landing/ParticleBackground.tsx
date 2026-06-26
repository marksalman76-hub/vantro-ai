'use client'

import { useEffect, useRef } from 'react'

// ─── Types ────────────────────────────────────────────────────────────────────

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  maxOpacity: number
  life: number
  maxLife: number
  hue: number
  twinkle: number
}

// ─── Factory ──────────────────────────────────────────────────────────────────

function createParticle(w: number, h: number): Particle {
  const life = 200 + Math.random() * 300
  return {
    x: Math.random() * w,
    y: h * 0.3 + Math.random() * h * 0.7,
    vx: (Math.random() - 0.5) * 0.3,
    vy: -Math.random() * 0.4 - 0.1,
    size: 80 + Math.random() * 160,
    opacity: 0,
    maxOpacity: 0.03 + Math.random() * 0.05,
    life: 0,
    maxLife: life,
    hue: Math.random() > 0.5 ? 210 : 28,
    twinkle: Math.random() * Math.PI * 2,
  }
}

// ─── Component ────────────────────────────────────────────────────────────────

interface ParticleBackgroundProps {
  count?: number
  className?: string
}

export default function ParticleBackground({
  count = 18,
  className = '',
}: ParticleBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const rafRef = useRef<number>(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Cap at 18 max
    const particleCount = Math.min(count, 18)

    let w = canvas.offsetWidth
    let h = canvas.offsetHeight
    canvas.width = w
    canvas.height = h

    const particles: Particle[] = Array.from({ length: particleCount }, () => {
      const p = createParticle(w, h)
      // Stagger initial life so they don't all appear at once
      p.life = Math.random() * p.maxLife
      return p
    })

    const draw = () => {
      ctx.clearRect(0, 0, w, h)

      particles.forEach((p, i) => {
        p.life++
        p.x += p.vx
        p.y += p.vy

        // Twinkle: phase advances each frame
        p.twinkle += 0.02

        // Fade in/out envelope
        const progress = p.life / p.maxLife
        let baseOpacity: number
        if (progress < 0.2) {
          baseOpacity = (progress / 0.2) * p.maxOpacity
        } else if (progress > 0.7) {
          baseOpacity = ((1 - progress) / 0.3) * p.maxOpacity
        } else {
          baseOpacity = p.maxOpacity
        }

        // Apply twinkle modulation
        p.opacity = baseOpacity * (0.8 + 0.2 * Math.sin(p.twinkle))

        // Respawn
        if (p.life >= p.maxLife) {
          particles[i] = createParticle(w, h)
          return
        }

        // Draw 3-stop radial gradient smoke puff
        const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size)

        if (p.hue === 210) {
          // Cool blue/mist
          grad.addColorStop(0, `rgba(0, 100, 180, ${p.opacity})`)
          grad.addColorStop(0.5, `rgba(0, 100, 180, ${p.opacity * 0.5})`)
          grad.addColorStop(1, `rgba(0, 100, 180, 0)`)
        } else {
          // Warm gold/smoke — hue 28
          grad.addColorStop(0, `rgba(255, 180, 50, ${p.opacity * 0.7})`)
          grad.addColorStop(0.5, `rgba(255, 180, 50, ${p.opacity * 0.35})`)
          grad.addColorStop(1, `rgba(255, 180, 50, 0)`)
        }

        ctx.fillStyle = grad
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fill()
      })

      rafRef.current = requestAnimationFrame(draw)
    }

    draw()

    // ResizeObserver for precise dimension tracking
    const resizeObserver = new ResizeObserver(() => {
      w = canvas.offsetWidth
      h = canvas.offsetHeight
      canvas.width = w
      canvas.height = h
    })
    resizeObserver.observe(canvas)

    // Pause when tab is hidden, resume when visible
    const handleVisibility = () => {
      if (document.visibilityState === 'hidden') {
        cancelAnimationFrame(rafRef.current)
      } else {
        draw()
      }
    }
    document.addEventListener('visibilitychange', handleVisibility)

    return () => {
      cancelAnimationFrame(rafRef.current)
      resizeObserver.disconnect()
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [count])

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={className}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        opacity: 0.8,
      }}
    />
  )
}
