'use client'

import { useEffect, useRef } from 'react'

type ShapeType = 'torus' | 'icosahedron' | 'octahedron' | 'torusKnot'

interface FloatingShapeProps {
  type?: ShapeType
  color?: string
  size?: number
  speed?: number
  className?: string
}

const SHAPE_PATHS: Record<ShapeType, string> = {
  icosahedron: 'M12 2 L22 8.5 L22 15.5 L12 22 L2 15.5 L2 8.5 Z M12 2 L12 22 M2 8.5 L22 8.5 M2 15.5 L22 15.5 M12 2 L2 15.5 M12 2 L22 15.5 M2 8.5 L12 22 M22 8.5 L12 22',
  octahedron:  'M12 2 L22 12 L12 22 L2 12 Z M12 2 L2 12 M12 2 L22 12 M2 12 L12 22 M22 12 L12 22 M2 12 L22 12',
  torus:       'M12 4 A8 8 0 1 1 11.999 4 Z M12 7 A5 5 0 1 1 11.999 7 Z M4 12 L7 12 M17 12 L20 12 M12 4 L12 7 M12 17 L12 20',
  torusKnot:   'M6 12 C6 6 10 3 12 6 C14 9 18 9 18 12 C18 15 14 18 12 15 C10 12 6 12 6 12 Z M6 12 C6 15 8 18 12 18 C16 18 18 15 18 12',
}

export default function FloatingShape({
  type = 'icosahedron',
  color = '#7C3AED',
  size = 120,
  speed = 0.8,
  className = '',
}: FloatingShapeProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    let raf: number
    const start = performance.now()
    const animate = (now: number) => {
      const t = ((now - start) / 1000) * speed
      const bobY = Math.sin(t * 0.4) * 6
      const rotZ = Math.sin(t * 0.3) * 12
      if (svgRef.current) {
        svgRef.current.style.transform = `translateY(${bobY}px) rotate(${rotZ}deg)`
      }
      raf = requestAnimationFrame(animate)
    }
    raf = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(raf)
  }, [speed])

  return (
    <div
      className={`pointer-events-none select-none ${className}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg
        ref={svgRef}
        viewBox="0 0 24 24"
        width={size}
        height={size}
        fill="none"
        stroke={color}
        strokeWidth="0.4"
        strokeOpacity="0.25"
        style={{ transition: 'transform 0.05s linear' }}
      >
        {(SHAPE_PATHS[type] || SHAPE_PATHS.icosahedron).split(' M').map((d, i) => (
          <path key={i} d={i === 0 ? d : 'M' + d} />
        ))}
      </svg>
    </div>
  )
}
