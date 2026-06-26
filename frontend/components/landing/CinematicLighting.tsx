'use client'

import { useState, useEffect, useId } from 'react'

export interface CinematicLightingProps {
  followMouse?: boolean
  goldSpotlight?: boolean
  showGrain?: boolean
}

export default function CinematicLighting({
  followMouse = true,
  goldSpotlight = true,
  showGrain = true,
}: CinematicLightingProps) {
  const [mousePos, setMousePos] = useState({ x: -9999, y: -9999 })
  const uid = useId().replace(/:/g, '')

  useEffect(() => {
    if (!followMouse || !goldSpotlight) return

    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('mousemove', handleMouseMove, { passive: true })
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [followMouse, goldSpotlight])

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 0,
        overflow: 'hidden',
      }}
    >
      {/* Layer 1 – Key light: top-left warm gold */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          background:
            'radial-gradient(ellipse 600px 500px at -5% -10%, rgba(255,215,0,0.09) 0%, transparent 65%)',
        }}
      />

      {/* Layer 2 – Fill light: right cool blue */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          background:
            'radial-gradient(ellipse 500px 700px at 105% 40%, rgba(180,215,255,0.07) 0%, transparent 60%)',
        }}
      />

      {/* Layer 3 – Rim light: bottom orange */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          background:
            'radial-gradient(ellipse 800px 300px at 50% 110%, rgba(255,107,53,0.08) 0%, transparent 55%)',
        }}
      />

      {/* Layer 4 – Mouse-following gold spotlight (absolute pixel coords) */}
      {followMouse && goldSpotlight && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
            background: `radial-gradient(circle 280px at ${mousePos.x}px ${mousePos.y}px, rgba(255,215,0,0.055) 0%, transparent 70%)`,
          }}
        />
      )}

      {/* Layer 5 – Vignette: dark edges */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          background:
            'radial-gradient(ellipse 90% 85% at 50% 50%, transparent 60%, rgba(10,13,17,0.7) 100%)',
        }}
      />

      {/* Layer 6 – SVG grain texture */}
      {showGrain && (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
            opacity: 0.025,
          }}
        >
          <defs>
            <filter
              id={`cl-grain-${uid}`}
              x="0%"
              y="0%"
              width="100%"
              height="100%"
              colorInterpolationFilters="linearRGB"
            >
              <feTurbulence
                type="fractalNoise"
                baseFrequency="0.65"
                numOctaves={3}
                stitchTiles="stitch"
                result="turbulence"
              />
              <feColorMatrix
                type="saturate"
                values="0"
                in="turbulence"
                result="grayNoise"
              />
              <feBlend in="SourceGraphic" in2="grayNoise" mode="overlay" result="blended" />
            </filter>
          </defs>
          <rect
            width="100%"
            height="100%"
            filter={`url(#cl-grain-${uid})`}
            fill="white"
          />
        </svg>
      )}
    </div>
  )
}
