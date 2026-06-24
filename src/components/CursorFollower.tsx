import { useEffect } from 'react'
import { motion, useMotionValue, useSpring } from 'framer-motion'

export function CursorFollower() {
  const x = useMotionValue(-200)
  const y = useMotionValue(-200)
  const sx = useSpring(x, { stiffness: 140, damping: 18, mass: 0.8 })
  const sy = useSpring(y, { stiffness: 140, damping: 18, mass: 0.8 })

  useEffect(() => {
    const move = (e: MouseEvent) => {
      x.set(e.clientX)
      y.set(e.clientY)
    }
    window.addEventListener('mousemove', move)
    return () => window.removeEventListener('mousemove', move)
  }, [x, y])

  // Only show on non-touch devices
  if (typeof window !== 'undefined' && window.matchMedia('(hover: none)').matches) {
    return null
  }

  return (
    <motion.div
      aria-hidden="true"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        x: sx,
        y: sy,
        translateX: '-50%',
        translateY: '-50%',
        width: '10px',
        height: '10px',
        borderRadius: '50%',
        background: 'oklch(0.97 0 0 / 0.55)',
        pointerEvents: 'none',
        zIndex: 9999,
        mixBlendMode: 'difference' as const,
        boxShadow: '0 0 14px 2px oklch(0.97 0 0 / 0.12)',
      }}
    />
  )
}
