'use client'

import { useEffect, useRef } from 'react'

interface Particle {
  x: number; y: number; vx: number; vy: number; size: number; opacity: number
}

export default function Background3D() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()

    const PARTICLE_COUNT = 40
    const CONNECTION_DIST = 80
    const particles: Particle[] = Array.from({ length: PARTICLE_COUNT }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      size: Math.random() * 1.5 + 0.5,
      opacity: Math.random() * 0.4 + 0.08,
    }))

    let raf: number
    let frameCount = 0
    const animate = () => {
      raf = requestAnimationFrame(animate)
      frameCount++
      // Run at ~30fps by skipping every other frame
      if (frameCount % 2 !== 0) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.fillStyle = 'rgb(11, 15, 25)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Batch all connection lines into a single path per opacity level
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i]
        for (let j = i + 1; j < particles.length; j++) {
          const q = particles[j]
          const dx = p.x - q.x
          const dy = p.y - q.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < CONNECTION_DIST) {
            ctx.strokeStyle = `rgba(59,130,246,${0.12 * (1 - dist / CONNECTION_DIST)})`
            ctx.lineWidth = 0.5
            ctx.beginPath()
            ctx.moveTo(p.x, p.y)
            ctx.lineTo(q.x, q.y)
            ctx.stroke()
          }
        }
      }

      ctx.fillStyle = 'rgba(99,102,241,1)'
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i]
        p.x += p.vx
        p.y += p.vy
        if (p.x < 0) p.x = canvas.width
        else if (p.x > canvas.width) p.x = 0
        if (p.y < 0) p.y = canvas.height
        else if (p.y > canvas.height) p.y = 0

        ctx.globalAlpha = p.opacity
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fill()
      }
      ctx.globalAlpha = 1
    }
    animate()

    window.addEventListener('resize', resize)
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize) }
  }, [])

  return <canvas ref={canvasRef} className="fixed top-0 left-0 w-full h-full -z-10" />
}
