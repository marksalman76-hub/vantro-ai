'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Agent } from '@/lib/agents'
import { CATEGORY_COLORS } from '@/lib/agents'

interface Props {
  agents: Agent[]
}

const ORBIT_RADIUS = 220
const AVATAR_SIZE = 80
const TOTAL_AGENTS = 22

function getCategoryColor(category: Agent['category']): string {
  return CATEGORY_COLORS[category] ?? '#ffffff'
}

export default function AgentOrbit({ agents }: Props) {
  const ringRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const [hoveredAgent, setHoveredAgent] = useState<Agent | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isHovering, setIsHovering] = useState(false)

  // Drag rotation state (using a ref so mousemove doesn't trigger re-renders)
  const isDragging = useRef(false)
  const dragStartX = useRef(0)
  const manualOffset = useRef(0)
  const lastOffset = useRef(0)

  // Apply manual rotation offset directly to the element style without re-rendering
  const applyRotation = useCallback((offset: number) => {
    if (!ringRef.current) return
    ringRef.current.style.transform = `rotateY(${offset}deg)`
  }, [])

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('[data-agent-avatar]')) return
    isDragging.current = true
    dragStartX.current = e.clientX
    lastOffset.current = manualOffset.current
    if (ringRef.current) {
      ringRef.current.style.animationPlayState = 'paused'
      ringRef.current.style.animation = 'none'
    }
  }, [])

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging.current) return
    const delta = e.clientX - dragStartX.current
    manualOffset.current = lastOffset.current + delta * 0.3
    applyRotation(manualOffset.current)
  }, [applyRotation])

  const handleMouseUp = useCallback(() => {
    isDragging.current = false
  }, [])

  // Pause orbit on container hover (when not dragging)
  const handleContainerMouseEnter = useCallback(() => {
    setIsHovering(true)
    if (ringRef.current && !isDragging.current) {
      ringRef.current.style.animationPlayState = 'paused'
    }
  }, [])

  const handleContainerMouseLeave = useCallback(() => {
    setIsHovering(false)
    isDragging.current = false
    if (ringRef.current && ringRef.current.style.animation === 'none') return
    if (ringRef.current) {
      ringRef.current.style.animationPlayState = 'running'
    }
  }, [])

  // Resume orbit when no agent is selected/hovered
  useEffect(() => {
    if (!ringRef.current) return
    if (!isHovering && !selectedAgent) {
      // Only resume if we haven't switched to manual mode
      if (ringRef.current.style.animation !== 'none') {
        ringRef.current.style.animationPlayState = 'running'
      }
    }
  }, [isHovering, selectedAgent])

  const handleAvatarClick = useCallback((agent: Agent, e: React.MouseEvent) => {
    e.stopPropagation()
    setSelectedAgent(prev => (prev?.id === agent.id ? null : agent))
  }, [])

  const handleAvatarMouseEnter = useCallback((agent: Agent) => {
    setHoveredAgent(agent)
  }, [])

  const handleAvatarMouseLeave = useCallback(() => {
    setHoveredAgent(null)
  }, [])

  const dismissCard = useCallback(() => {
    setSelectedAgent(null)
  }, [])

  const displayAgent = selectedAgent ?? hoveredAgent

  return (
    <>
      {/* Inject keyframe animation via a style tag */}
      <style>{`
        @keyframes orbit {
          from { transform: rotateY(0deg); }
          to   { transform: rotateY(360deg); }
        }
        @keyframes pulse-glow {
          0%, 100% { opacity: 0.35; transform: scale(1); }
          50%       { opacity: 0.60; transform: scale(1.08); }
        }
        @keyframes avatar-float {
          0%, 100% { transform: translateY(0px); }
          50%       { transform: translateY(-4px); }
        }
      `}</style>

      {/* Outer wrapper — responsive: 500px desktop, full-width mobile */}
      <div
        className="relative mx-auto select-none"
        style={{ width: '100%', maxWidth: 500, aspectRatio: '1 / 1' }}
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onMouseEnter={handleContainerMouseEnter}
      >
        {/* Perspective wrapper */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: '100%',
            perspective: '1000px',
          }}
          onMouseLeave={handleContainerMouseLeave}
        >
          {/* Central pulsing glow */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              width: 120,
              height: 120,
              marginTop: -60,
              marginLeft: -60,
              borderRadius: '50%',
              background:
                'radial-gradient(circle, rgba(255,107,53,0.55) 0%, rgba(255,215,0,0.25) 50%, transparent 75%)',
              animation: 'pulse-glow 2.5s ease-in-out infinite',
              zIndex: 10,
              pointerEvents: 'none',
            }}
          />
          {/* Inner label */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 11,
              pointerEvents: 'none',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
              22 Agents
            </div>
            <div style={{ fontSize: 9, color: 'rgba(255,107,53,0.8)', fontWeight: 500, marginTop: 2 }}>
              Active
            </div>
          </div>

          {/* Orbit ring */}
          <div
            ref={ringRef}
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
              transformStyle: 'preserve-3d',
              animation: 'orbit 30s linear infinite',
            }}
          >
            {agents.slice(0, TOTAL_AGENTS).map((agent, i) => {
              const angleY = (i * 360) / TOTAL_AGENTS
              const isActive = displayAgent?.id === agent.id
              const color = getCategoryColor(agent.category)

              return (
                <div
                  key={agent.id}
                  data-agent-avatar="true"
                  style={{
                    position: 'absolute',
                    left: '50%',
                    top: '50%',
                    width: AVATAR_SIZE,
                    height: AVATAR_SIZE,
                    marginLeft: -(AVATAR_SIZE / 2),
                    marginTop: -(AVATAR_SIZE / 2),
                    transform: `rotateY(${angleY}deg) translateZ(${ORBIT_RADIUS}px) rotateY(${-angleY}deg)`,
                    cursor: 'pointer',
                    zIndex: isActive ? 20 : 5,
                  }}
                  onClick={(e) => handleAvatarClick(agent, e)}
                  onMouseEnter={() => handleAvatarMouseEnter(agent)}
                  onMouseLeave={handleAvatarMouseLeave}
                >
                  {/* Avatar circle */}
                  <div
                    style={{
                      width: '100%',
                      height: '100%',
                      borderRadius: '50%',
                      overflow: 'hidden',
                      border: `2.5px solid ${isActive ? color : 'rgba(255,255,255,0.15)'}`,
                      boxShadow: isActive
                        ? `0 0 18px ${color}88, 0 0 40px ${color}44`
                        : '0 2px 12px rgba(0,0,0,0.5)',
                      background: '#1A1F2E',
                      transition: 'border-color 0.25s ease, box-shadow 0.25s ease',
                      animation: isActive ? 'avatar-float 2s ease-in-out infinite' : 'none',
                    }}
                  >
                    <img
                      src={agent.avatar}
                      alt={agent.name}
                      width={AVATAR_SIZE}
                      height={AVATAR_SIZE}
                      style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                      draggable={false}
                    />
                  </div>

                  {/* Name label below avatar */}
                  <div
                    style={{
                      position: 'absolute',
                      top: AVATAR_SIZE + 6,
                      left: '50%',
                      transform: 'translateX(-50%)',
                      whiteSpace: 'nowrap',
                      textAlign: 'center',
                      pointerEvents: 'none',
                    }}
                  >
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 600,
                        color: isActive ? color : 'rgba(255,255,255,0.55)',
                        transition: 'color 0.2s ease',
                        textShadow: isActive ? `0 0 8px ${color}` : 'none',
                      }}
                    >
                      {agent.name.split(' ')[0]}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Faint orbit ring lines (decorative) */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              width: ORBIT_RADIUS * 2 + AVATAR_SIZE,
              height: ORBIT_RADIUS * 2 + AVATAR_SIZE,
              marginTop: -(ORBIT_RADIUS + AVATAR_SIZE / 2),
              marginLeft: -(ORBIT_RADIUS + AVATAR_SIZE / 2),
              borderRadius: '50%',
              border: '1px solid rgba(255,255,255,0.04)',
              pointerEvents: 'none',
            }}
          />
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              width: ORBIT_RADIUS * 2 - 30,
              height: ORBIT_RADIUS * 2 - 30,
              marginTop: -(ORBIT_RADIUS - 15),
              marginLeft: -(ORBIT_RADIUS - 15),
              borderRadius: '50%',
              border: '1px dashed rgba(255,107,53,0.08)',
              pointerEvents: 'none',
            }}
          />
        </div>

        {/* Agent card overlay — outside the 3D perspective to render flat */}
        <AnimatePresence>
          {displayAgent && (
            <motion.div
              key={displayAgent.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.97 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
              style={{
                position: 'absolute',
                bottom: -20,
                left: '50%',
                transform: 'translateX(-50%)',
                width: 'min(340px, 95vw)',
                background: 'rgba(15,20,30,0.92)',
                backdropFilter: 'blur(24px)',
                border: `1px solid ${getCategoryColor(displayAgent.category)}44`,
                borderRadius: 16,
                padding: '18px 20px',
                zIndex: 50,
                boxShadow: `0 8px 32px rgba(0,0,0,0.6), 0 0 0 1px ${getCategoryColor(displayAgent.category)}22`,
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Card header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: '50%',
                    overflow: 'hidden',
                    border: `2px solid ${getCategoryColor(displayAgent.category)}`,
                    flexShrink: 0,
                  }}
                >
                  <img
                    src={displayAgent.avatar}
                    alt={displayAgent.name}
                    width={44}
                    height={44}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 16, fontWeight: 700, color: '#ffffff', lineHeight: 1.2 }}>
                    {displayAgent.name}
                  </div>
                  <div style={{ fontSize: 12, color: '#00D9FF', marginTop: 2, fontWeight: 500 }}>
                    {displayAgent.role}
                  </div>
                </div>
                {/* Category badge */}
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    color: getCategoryColor(displayAgent.category),
                    background: `${getCategoryColor(displayAgent.category)}18`,
                    border: `1px solid ${getCategoryColor(displayAgent.category)}40`,
                    borderRadius: 20,
                    padding: '3px 10px',
                    letterSpacing: '0.05em',
                    textTransform: 'uppercase',
                    flexShrink: 0,
                  }}
                >
                  {displayAgent.category}
                </span>
              </div>

              {/* Description */}
              <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', marginBottom: 14, lineHeight: 1.5 }}>
                {displayAgent.description}
              </p>

              {/* Stats row */}
              <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: '#1FFFD6' }}>
                    {displayAgent.stats.successRate}%
                  </div>
                  <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', marginTop: 1 }}>
                    Success
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: '#FFD700' }}>
                    {displayAgent.stats.responseTime}
                  </div>
                  <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', marginTop: 1 }}>
                    Response
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: '#B4D7FF' }}>
                    {displayAgent.stats.languages}
                  </div>
                  <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', marginTop: 1 }}>
                    Languages
                  </div>
                </div>
              </div>

              {/* CTA button */}
              <a
                href="#pricing"
                style={{
                  display: 'block',
                  width: '100%',
                  textAlign: 'center',
                  padding: '10px 0',
                  background: 'linear-gradient(135deg, #FF6B35, #FFD700)',
                  color: '#0F1419',
                  fontWeight: 700,
                  fontSize: 13,
                  borderRadius: 10,
                  textDecoration: 'none',
                  letterSpacing: '0.02em',
                  transition: 'opacity 0.15s ease',
                  boxShadow: '0 4px 16px rgba(255,107,53,0.35)',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.88')}
                onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
              >
                Deploy This Agent
              </a>

              {/* Dismiss hint if card is pinned via click */}
              {selectedAgent && (
                <button
                  onClick={dismissCard}
                  style={{
                    display: 'block',
                    width: '100%',
                    marginTop: 8,
                    textAlign: 'center',
                    fontSize: 11,
                    color: 'rgba(255,255,255,0.3)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: '4px 0',
                  }}
                >
                  Click to dismiss
                </button>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  )
}
