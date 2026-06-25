import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from 'remotion'

const ORB_SRC =
  'https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/saLNUqZiiYVuufKN.png'

const MASK =
  'radial-gradient(ellipse 90% 90% at 50% 50%, black 22%, rgba(0,0,0,0.55) 52%, transparent 86%)'

export const OrbComposition: React.FC = () => {
  const frame = useCurrentFrame()
  const { durationInFrames } = useVideoConfig()

  const t = (frame / durationInFrames) * (2 * Math.PI)

  // Cinematic floating — GPU: transform only
  const y = 22 * Math.sin(t)
  const x = 10 * Math.cos(t * 0.73)
  const scale = 1 + 0.06 * Math.sin(t * 1.31)

  // Pulsing cobalt glow
  const brightness = 1 + 0.32 * Math.abs(Math.sin(t * 0.5))
  const glowSpread = 30 + 55 * Math.abs(Math.sin(t * 0.5))
  const glowAlpha = 0.18 + 0.38 * Math.abs(Math.sin(t * 0.5))

  // Primary orbiting highlight
  const hx = 50 + 22 * Math.cos(t)
  const hy = 50 + 18 * Math.sin(t * 1.2)

  // Counter-rotating secondary highlight
  const hx2 = 50 + 14 * Math.cos(-t * 0.65 + Math.PI)
  const hy2 = 50 + 11 * Math.sin(-t * 0.65 + Math.PI)

  // Nebula breathing
  const nx = 50 + 6 * Math.cos(t * 0.4)
  const ny = 50 + 6 * Math.sin(t * 0.4)
  const nebulaScale = 1 + 0.08 * Math.sin(t * 0.35)

  return (
    <AbsoluteFill style={{ background: 'transparent', overflow: 'hidden' }}>
      {/* Animated dark nebula */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `scale(${nebulaScale.toFixed(3)})`,
          background: `radial-gradient(circle at ${nx.toFixed(1)}% ${ny.toFixed(1)}%, oklch(0.16 0.12 248 / 0.95) 0%, oklch(0.22 0.08 252 / 0.70) 40%, transparent 72%)`,
          willChange: 'transform',
        }}
      />

      {/* Outer cobalt halo */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(circle, transparent 38%, oklch(0.10 0.06 260 / 0.55) 65%, oklch(0.07 0.04 260 / 0.90) 85%)`,
        }}
      />

      {/* Orb + highlights — single transform layer for 60fps */}
      <AbsoluteFill
        style={{
          transform: `translate(${x.toFixed(2)}px, ${y.toFixed(2)}px) scale(${scale.toFixed(4)})`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          willChange: 'transform',
        }}
      >
        <Img
          src={ORB_SRC}
          style={{
            width: '86%',
            height: 'auto',
            mixBlendMode: 'screen',
            filter: `brightness(${brightness.toFixed(3)}) drop-shadow(0 0 ${Math.round(glowSpread)}px rgba(80,100,230,${glowAlpha.toFixed(2)}))`,
            maskImage: MASK,
            WebkitMaskImage: MASK,
            display: 'block',
          }}
        />

        {/* Primary orbiting highlight */}
        <div
          style={{
            position: 'absolute',
            inset: '7%',
            background: `radial-gradient(circle 110px at ${hx.toFixed(1)}% ${hy.toFixed(1)}%, rgba(255,255,255,0.72) 0%, transparent 60%)`,
            mixBlendMode: 'screen',
            maskImage: MASK,
            WebkitMaskImage: MASK,
          }}
        />

        {/* Secondary counter-rotating highlight */}
        <div
          style={{
            position: 'absolute',
            inset: '7%',
            background: `radial-gradient(circle 70px at ${hx2.toFixed(1)}% ${hy2.toFixed(1)}%, rgba(180,210,255,0.48) 0%, transparent 55%)`,
            mixBlendMode: 'screen',
            maskImage: MASK,
            WebkitMaskImage: MASK,
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  )
}
