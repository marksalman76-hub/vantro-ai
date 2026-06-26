import { ImageResponse } from 'next/og'

export const size = { width: 32, height: 32 }
export const contentType = 'image/png'

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: 32,
          height: 32,
          background: '#0F1419',
          borderRadius: 8,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <span
          style={{
            fontSize: 20,
            fontWeight: 800,
            color: '#FF6B35',
            fontFamily: 'sans-serif',
            lineHeight: 1,
            letterSpacing: '-0.03em',
          }}
        >
          V
        </span>
      </div>
    ),
    { ...size }
  )
}
