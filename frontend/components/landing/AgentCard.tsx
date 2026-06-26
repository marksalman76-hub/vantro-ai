'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'

interface Agent {
  id: number
  name: string
  role: string
  category: string
  description: string
  bio: string
  avatar: string
  stats: {
    successRate: number
    responseTime: string
    languages: number
  }
}

const CATEGORY_COLORS: Record<string, string> = {
  Sales: '#FF6B35',
  Operations: '#00D9FF',
  Engineering: '#1FFFD6',
  Support: '#FFD700',
  Executive: '#B084FF',
}

interface AgentCardProps {
  agent: Agent
  featured?: boolean
}

export default function AgentCard({ agent, featured = false }: AgentCardProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const catColor = CATEGORY_COLORS[agent.category] || '#FF6B35'

  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: `0 20px 60px ${catColor}20` }}
      transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
      style={{
        background: 'rgba(255,255,255,0.07)',
        border: `1px solid ${featured ? catColor + '40' : 'rgba(255,255,255,0.10)'}`,
        borderRadius: 20,
        padding: 24,
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        boxShadow: featured ? `0 0 40px ${catColor}15` : '0 8px 32px rgba(0,0,0,0.3)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Cinematic glow top */}
      <div style={{
        position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)',
        width: '80%', height: 1,
        background: `linear-gradient(90deg, transparent, ${catColor}60, transparent)`,
      }} />

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
        <div style={{ position: 'relative', flexShrink: 0 }}>
          <img
            src={agent.avatar}
            alt={agent.name}
            style={{
              width: 56, height: 56, borderRadius: '50%',
              objectFit: 'cover',
              border: `2px solid ${catColor}60`,
            }}
          />
          {/* Live indicator */}
          <span style={{
            position: 'absolute', bottom: 2, right: 2,
            width: 10, height: 10, borderRadius: '50%',
            background: '#22C55E',
            border: '2px solid #0F1419',
            boxShadow: '0 0 6px #22C55E',
          }} />
        </div>
        <div>
          <h4 style={{ color: '#fff', fontWeight: 700, fontSize: 16, margin: 0, textWrap: 'balance' as any }}>{agent.name}</h4>
          <p style={{ color: catColor, fontSize: 12, margin: '3px 0 0', fontWeight: 600 }}>{agent.role}</p>
        </div>
        <span style={{
          marginLeft: 'auto',
          background: `${catColor}18`,
          color: catColor,
          fontSize: 11, fontWeight: 700,
          padding: '3px 10px', borderRadius: 20,
          whiteSpace: 'nowrap',
        }}>{agent.category}</span>
      </div>

      <p style={{ color: '#9CA3AF', fontSize: 13, lineHeight: 1.65, marginBottom: 16 }}>{agent.description}</p>

      {/* Stats */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {[
          { v: `${agent.stats.successRate}%`, l: 'Success' },
          { v: agent.stats.responseTime, l: 'Response' },
          { v: `${agent.stats.languages} lang`, l: 'Multilingual' },
        ].map(s => (
          <div key={s.l} style={{
            flex: 1, background: 'rgba(255,255,255,0.05)',
            borderRadius: 8, padding: '8px 6px', textAlign: 'center',
          }}>
            <p style={{ color: '#fff', fontWeight: 700, fontSize: 13, margin: 0, fontVariantNumeric: 'tabular-nums' }}>{s.v}</p>
            <p style={{ color: '#6B7280', fontSize: 10, margin: '2px 0 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{s.l}</p>
          </div>
        ))}
      </div>

      {/* Voice preview */}
      <button
        onClick={() => setIsPlaying(!isPlaying)}
        style={{
          width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
          background: isPlaying ? 'rgba(0,217,255,0.15)' : 'rgba(255,255,255,0.05)',
          border: `1px solid ${isPlaying ? 'rgba(0,217,255,0.4)' : 'rgba(255,255,255,0.1)'}`,
          borderRadius: 10, padding: '10px',
          color: isPlaying ? '#00D9FF' : '#9CA3AF',
          cursor: 'pointer', fontSize: 13, fontWeight: 600,
          transition: 'all 0.2s',
        }}
      >
        {isPlaying ? (
          <>
            {/* Equalizer animation */}
            <span style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 16 }}>
              {[4, 8, 6, 10, 5, 9, 7].map((h, i) => (
                <span key={i} style={{
                  width: 3, height: h, background: '#00D9FF', borderRadius: 2,
                  animation: `eq ${0.4 + i * 0.1}s ease-in-out ${i * 0.05}s infinite alternate`,
                }} />
              ))}
            </span>
            Playing...
          </>
        ) : (
          <>
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <circle cx="7" cy="7" r="6" stroke="currentColor" strokeWidth="1.2"/>
              <path d="M5.5 4.5L9.5 7L5.5 9.5V4.5Z" fill="currentColor"/>
            </svg>
            Listen to {agent.name.split(' ')[0]}
          </>
        )}
      </button>

      <style>{`
        @keyframes eq {
          from { transform: scaleY(0.4); }
          to { transform: scaleY(1); }
        }
      `}</style>
    </motion.div>
  )
}
