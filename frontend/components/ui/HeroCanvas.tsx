'use client'

import { useEffect, useRef } from 'react'

interface Particle {
  x: number; y: number; z: number
  vx: number; vy: number
  r: number; g: number; b: number
  alpha: number; size: number
}

const PALETTE = [
  { r: 124, g: 58,  b: 237 }, // violet
  { r: 59,  g: 130, b: 246 }, // blue
  { r: 6,   g: 182, b: 212 }, // cyan
]

export default function HeroCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let raf: number
    let mouseX = 0
    let mouseY = 0
    let targetX = 0
    let targetY = 0

    const particles: Particle[] = []
    const COUNT = 280

    const resize = () => {
      canvas.width  = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
    }
    resize()

    for (let i = 0; i < COUNT; i++) {
      const c = PALETTE[Math.floor(Math.random() * PALETTE.length)]
      particles.push({
        x:     Math.random() * canvas.width,
        y:     Math.random() * canvas.height,
        z:     Math.random(),
        vx:    (Math.random() - 0.5) * 0.18,
        vy:    (Math.random() - 0.5) * 0.18,
        r: c.r, g: c.g, b: c.b,
        alpha: 0.15 + Math.random() * 0.4,
        size:  0.8 + Math.random() * 2,
      })
    }

    const onMove = (e: MouseEvent) => {
      targetX = (e.clientX / window.innerWidth  - 0.5) * 30
      targetY = (e.clientY / window.innerHeight - 0.5) * 30
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('resize', resize)

    const tick = () => {
      mouseX += (targetX - mouseX) * 0.04
      mouseY += (targetY - mouseY) * 0.04

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      for (const p of particles) {
        p.x += p.vx + mouseX * p.z * 0.012
        p.y += p.vy + mouseY * p.z * 0.012

        if (p.x < 0) p.x += canvas.width
        if (p.x > canvas.width) p.x -= canvas.width
        if (p.y < 0) p.y += canvas.height
        if (p.y > canvas.height) p.y -= canvas.height

        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(${p.r},${p.g},${p.b},${p.alpha})`
        ctx.fill()
      }

      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)

    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <div className="absolute inset-0 z-0 pointer-events-none" aria-hidden="true">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ opacity: 0.7 }}
      />
    </div>
  )
}
