'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AGENTS, CATEGORY_COLORS, type Agent } from '@/lib/agents'

const RADIUS = 380
const PLANE_W = 180
const PLANE_H = 216
const CAMERA_Z = 700
const AGENT_COUNT = 22

interface AgentCarouselProps {
  agents?: Agent[]
  onSelectAgent?: (agent: Agent) => void
}

export default function AgentCarousel({ onSelectAgent }: AgentCarouselProps = {}) {
  const mountRef = useRef<HTMLDivElement>(null)
  const rendererRef = useRef<any>(null)
  const cameraRef = useRef<any>(null)
  const groupRef = useRef<any>(null)
  const frameRef = useRef<number>(0)
  const meshesRef = useRef<any[]>([])
  const meshScalesRef = useRef<number[]>(new Array(AGENT_COUNT).fill(0.85))

  const isDragging = useRef(false)
  const lastX = useRef(0)
  const targetRotation = useRef(0)
  const currentRotation = useRef(0)
  const clickStartX = useRef(0)

  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [frontIdx, setFrontIdx] = useState(0)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    if (!mountRef.current) return

    let THREE: any
    let cancelled = false
    let sceneLocal: any
    let rendererLocal: any
    let cleanupFn: (() => void) | null = null

    async function init() {
      try {
        THREE = await import('three')
        if (cancelled || !mountRef.current) return

        const W = 500
        const H = 520

        // Scene
        sceneLocal = new THREE.Scene()

        // Camera
        const camera = new THREE.PerspectiveCamera(55, W / H, 1, 6000)
        camera.position.set(0, 0, CAMERA_Z)
        camera.lookAt(0, 0, 0)
        cameraRef.current = camera

        // Renderer
        rendererLocal = new THREE.WebGLRenderer({ antialias: true, alpha: true })
        rendererLocal.setSize(W, H)
        rendererLocal.setPixelRatio(Math.min(window.devicePixelRatio, 2))
        rendererLocal.setClearColor(0x000000, 0)
        // Fix: set sRGB color space so textures render with correct colors
        rendererLocal.outputColorSpace = THREE.SRGBColorSpace
        mountRef.current.appendChild(rendererLocal.domElement)
        rendererRef.current = rendererLocal

        // Lights
        const ambient = new THREE.AmbientLight(0xffffff, 0.8)
        sceneLocal.add(ambient)

        const dirLight = new THREE.DirectionalLight(0xffe5b4, 1.2)
        dirLight.position.set(-400, 400, 600)
        sceneLocal.add(dirLight)

        const pointLight = new THREE.PointLight(0xff6b35, 1.0, 2000)
        pointLight.position.set(0, 0, -600)
        sceneLocal.add(pointLight)

        // Group
        const group = new THREE.Group()
        sceneLocal.add(group)
        groupRef.current = group

        // Proxy randomuser.me through our API to bypass CORS block on WebGL canvas
        const proxyUrl = (url: string) =>
          `/api/portrait?url=${encodeURIComponent(url)}`

        const loader = new THREE.TextureLoader()

        const meshes: any[] = []
        const agents = AGENTS.slice(0, AGENT_COUNT)

        agents.forEach((agent, i) => {
          const angle = (i / agents.length) * Math.PI * 2
          const x = RADIUS * Math.sin(angle)
          const z = RADIUS * Math.cos(angle)

          const geometry = new THREE.PlaneGeometry(PLANE_W, PLANE_H)

          // Fix: MeshBasicMaterial — renders texture without needing lights
          const material = new THREE.MeshBasicMaterial({
            side: THREE.DoubleSide,
            transparent: false,
            color: 0xcccccc, // fallback gray until texture loads
          })

          loader.load(
            proxyUrl(agent.avatar),
            (texture: any) => {
              texture.colorSpace = THREE.SRGBColorSpace
              material.map = texture
              material.color.set(0xffffff) // reset so texture shows correctly
              material.needsUpdate = true
            },
            undefined,
            () => {
              // On error: show category-colored placeholder
              const catColor = CATEGORY_COLORS[agent.category] || '#888888'
              material.color.set(catColor)
            }
          )

          const mesh = new THREE.Mesh(geometry, material)
          mesh.position.set(x, 0, z)
          // Make each plane face outward from center (toward camera when at front)
          mesh.lookAt(0, 0, CAMERA_Z * 10)
          mesh.userData = { agent, index: i }

          group.add(mesh)
          meshes.push(mesh)
        })

        meshesRef.current = meshes
        meshScalesRef.current = new Array(agents.length).fill(0.85)

        // Animate loop
        const animate = () => {
          if (cancelled) return
          frameRef.current = requestAnimationFrame(animate)

          // Auto-rotate
          if (!isDragging.current) {
            targetRotation.current += 0.003
          }

          // Lerp rotation
          currentRotation.current += (targetRotation.current - currentRotation.current) * 0.06
          group.rotation.y = currentRotation.current

          // Find front agent and update scales
          let maxZ = -Infinity
          let frontI = 0

          meshes.forEach((mesh, i) => {
            const worldPos = new THREE.Vector3()
            mesh.getWorldPosition(worldPos)

            if (worldPos.z > maxZ) {
              maxZ = worldPos.z
              frontI = i
            }

            // Normalized depth: 0=back, 1=front
            const zNorm = (worldPos.z + RADIUS) / (RADIUS * 2)
            const clamped = Math.max(0, Math.min(1, zNorm))

            // Target scale: front=1.2, back=0.85
            const targetScale = 0.85 + clamped * (1.2 - 0.85)
            // Lerp current scale
            const prev = meshScalesRef.current[i]
            const next = prev + (targetScale - prev) * 0.08
            meshScalesRef.current[i] = next
            mesh.scale.setScalar(next)
          })

          setFrontIdx(frontI)
          rendererLocal.render(sceneLocal, camera)
        }

        animate()
        setLoaded(true)

        const onResize = () => {
          if (!mountRef.current || !rendererLocal || !camera) return
          // Keep fixed 500x520
          camera.updateProjectionMatrix()
        }
        window.addEventListener('resize', onResize)

        cleanupFn = () => {
          window.removeEventListener('resize', onResize)
        }
      } catch (err) {
        console.error('[AgentCarousel] Three.js init error:', err)
      }
    }

    init()

    return () => {
      cancelled = true
      cancelAnimationFrame(frameRef.current)
      if (cleanupFn) cleanupFn()
      if (rendererLocal) {
        rendererLocal.dispose()
        if (mountRef.current && rendererLocal.domElement.parentNode === mountRef.current) {
          mountRef.current.removeChild(rendererLocal.domElement)
        }
      }
    }
  }, [])

  // Pointer handlers for drag-to-rotate
  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    isDragging.current = true
    lastX.current = e.clientX
    clickStartX.current = e.clientX
    ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
  }, [])

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!isDragging.current) return
    const delta = (e.clientX - lastX.current) / 220
    targetRotation.current += delta
    lastX.current = e.clientX
  }, [])

  const handlePointerUp = useCallback((e: React.PointerEvent) => {
    isDragging.current = false
    ;(e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId)
  }, [])

  const handleClick = useCallback((e: React.MouseEvent) => {
    // Ignore drag clicks (moved more than 5px)
    if (Math.abs(e.clientX - clickStartX.current) > 5) return
    if (!rendererRef.current || !cameraRef.current || !mountRef.current) return

    const rect = mountRef.current.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 2 - 1
    const y = -((e.clientY - rect.top) / rect.height) * 2 + 1

    import('three').then((THREE) => {
      const raycaster = new THREE.Raycaster()
      raycaster.setFromCamera(new THREE.Vector2(x, y), cameraRef.current)
      const intersects = raycaster.intersectObjects(meshesRef.current)
      if (intersects.length > 0) {
        const agent = intersects[0].object.userData.agent as Agent
        if (agent) {
          setSelectedAgent(agent)
          onSelectAgent?.(agent)
        }
      }
    })
  }, [onSelectAgent])

  const frontAgent = AGENTS[frontIdx] ?? AGENTS[0]
  const frontColor = CATEGORY_COLORS[frontAgent?.category] ?? '#FF6B35'

  return (
    <div
      style={{
        position: 'relative',
        width: 500,
        height: 520,
        margin: '0 auto',
        userSelect: 'none',
      }}
    >
      {/* Three.js canvas mount */}
      <div
        ref={mountRef}
        style={{
          position: 'absolute',
          inset: 0,
          cursor: isDragging.current ? 'grabbing' : 'grab',
          borderRadius: 24,
          overflow: 'hidden',
        }}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        onClick={handleClick}
      />

      {/* Radial vignette overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          borderRadius: 24,
          background:
            'radial-gradient(ellipse 80% 70% at 50% 50%, transparent 25%, rgba(10,13,18,0.55) 100%)',
        }}
      />

      {/* Drag hint */}
      {loaded && !selectedAgent && (
        <div
          style={{
            position: 'absolute',
            bottom: 80,
            left: '50%',
            transform: 'translateX(-50%)',
            pointerEvents: 'none',
            color: 'rgba(255,255,255,0.28)',
            fontSize: 11,
            fontWeight: 500,
            letterSpacing: '0.04em',
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            whiteSpace: 'nowrap',
          }}
        >
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
            <path
              d="M1.5 5.5H9.5M6.5 2.5L9.5 5.5L6.5 8.5"
              stroke="currentColor"
              strokeWidth="1.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          Drag to explore · Click to meet
        </div>
      )}

      {/* Front-agent info bar — always visible */}
      {loaded && frontAgent && (
        <motion.div
          key={frontAgent.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            background: 'rgba(15,20,25,0.92)',
            borderTop: `1px solid rgba(255,255,255,0.08)`,
            backdropFilter: 'blur(16px)',
            borderRadius: '0 0 24px 24px',
            padding: '12px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            pointerEvents: 'none',
          }}
        >
          <div>
            <p
              style={{
                color: '#fff',
                fontWeight: 700,
                fontSize: 14,
                margin: 0,
                lineHeight: 1.2,
              }}
            >
              {frontAgent.name}
            </p>
            <p
              style={{
                color: frontColor,
                fontWeight: 600,
                fontSize: 11,
                margin: '2px 0 0',
                lineHeight: 1,
              }}
            >
              {frontAgent.role}
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                background: `${frontColor}22`,
                border: `1px solid ${frontColor}44`,
                color: frontColor,
                fontSize: 10,
                fontWeight: 700,
                padding: '3px 9px',
                borderRadius: 20,
                letterSpacing: '0.04em',
              }}
            >
              {frontAgent.category}
            </span>
            <span
              style={{
                color: 'rgba(255,255,255,0.28)',
                fontSize: 10,
                whiteSpace: 'nowrap',
              }}
            >
              Drag to explore →
            </span>
          </div>
        </motion.div>
      )}

      {/* Selected agent overlay (AnimatePresence full-screen modal) */}
      <AnimatePresence>
        {selectedAgent && (
          <motion.div
            key="overlay-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(5,8,12,0.82)',
              backdropFilter: 'blur(8px)',
              zIndex: 9998,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            onClick={() => setSelectedAgent(null)}
          >
            <motion.div
              key="overlay-card"
              initial={{ opacity: 0, scale: 0.92, y: 32 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.92, y: 32 }}
              transition={{ duration: 0.32, ease: [0.23, 1, 0.32, 1] }}
              onClick={(e) => e.stopPropagation()}
              style={{
                position: 'relative',
                width: 480,
                maxWidth: '95vw',
                background: 'rgba(15,20,25,0.92)',
                border: '1px solid rgba(255,255,255,0.12)',
                backdropFilter: 'blur(16px)',
                borderRadius: 20,
                padding: 36,
                boxShadow: `0 0 80px ${CATEGORY_COLORS[selectedAgent.category] ?? '#FF6B35'}28`,
                zIndex: 9999,
              }}
            >
              {/* Close button */}
              <button
                onClick={() => setSelectedAgent(null)}
                style={{
                  position: 'absolute',
                  top: 16,
                  right: 16,
                  width: 34,
                  height: 34,
                  borderRadius: '50%',
                  background: 'rgba(255,255,255,0.08)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  color: '#9CA3AF',
                  fontSize: 18,
                  lineHeight: '34px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={(e) => {
                  ;(e.currentTarget as HTMLElement).style.background =
                    'rgba(255,255,255,0.15)'
                }}
                onMouseLeave={(e) => {
                  ;(e.currentTarget as HTMLElement).style.background =
                    'rgba(255,255,255,0.08)'
                }}
              >
                ×
              </button>

              {/* Avatar */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 24 }}>
                <div
                  style={{
                    width: 140,
                    height: 140,
                    borderRadius: '50%',
                    padding: 3,
                    background: `linear-gradient(135deg, ${CATEGORY_COLORS[selectedAgent.category] ?? '#FF6B35'}, transparent)`,
                    boxShadow: `0 0 40px ${CATEGORY_COLORS[selectedAgent.category] ?? '#FF6B35'}55`,
                    marginBottom: 16,
                  }}
                >
                  <img
                    src={selectedAgent.avatar}
                    alt={selectedAgent.name}
                    style={{
                      width: '100%',
                      height: '100%',
                      borderRadius: '50%',
                      objectFit: 'cover',
                      display: 'block',
                      border: '2px solid rgba(15,20,25,0.9)',
                    }}
                    crossOrigin="anonymous"
                  />
                </div>

                <h2
                  style={{
                    color: '#fff',
                    fontWeight: 700,
                    fontSize: 28,
                    margin: 0,
                    textAlign: 'center',
                    lineHeight: 1.2,
                  }}
                >
                  {selectedAgent.name}
                </h2>
                <p
                  style={{
                    color: CATEGORY_COLORS[selectedAgent.category] ?? '#FF6B35',
                    fontWeight: 600,
                    fontSize: 16,
                    margin: '6px 0 10px',
                    textAlign: 'center',
                  }}
                >
                  {selectedAgent.role}
                </p>
                <span
                  style={{
                    display: 'inline-block',
                    background: `${CATEGORY_COLORS[selectedAgent.category] ?? '#FF6B35'}22`,
                    border: `1px solid ${CATEGORY_COLORS[selectedAgent.category] ?? '#FF6B35'}55`,
                    color: CATEGORY_COLORS[selectedAgent.category] ?? '#FF6B35',
                    fontSize: 11,
                    fontWeight: 700,
                    padding: '4px 14px',
                    borderRadius: 20,
                    letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                  }}
                >
                  {selectedAgent.category}
                </span>
              </div>

              {/* Bio */}
              <p
                style={{
                  color: '#9CA3AF',
                  fontSize: 14,
                  lineHeight: 1.75,
                  margin: '0 0 24px',
                  textAlign: 'center',
                }}
              >
                {selectedAgent.bio}
              </p>

              {/* Stats grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr 1fr',
                  gap: 12,
                  marginBottom: 24,
                }}
              >
                {[
                  { label: 'Success Rate', value: `${selectedAgent.stats.successRate}%` },
                  { label: 'Response Time', value: selectedAgent.stats.responseTime },
                  { label: 'Languages', value: `${selectedAgent.stats.languages}` },
                ].map((stat) => (
                  <div
                    key={stat.label}
                    style={{
                      background: 'rgba(255,255,255,0.04)',
                      border: '1px solid rgba(255,255,255,0.08)',
                      borderRadius: 12,
                      padding: '14px 10px',
                      textAlign: 'center',
                    }}
                  >
                    <p
                      style={{
                        color: '#fff',
                        fontWeight: 700,
                        fontSize: 20,
                        margin: 0,
                        lineHeight: 1,
                      }}
                    >
                      {stat.value}
                    </p>
                    <p
                      style={{
                        color: '#6B7280',
                        fontSize: 10,
                        fontWeight: 600,
                        margin: '5px 0 0',
                        textTransform: 'uppercase',
                        letterSpacing: '0.06em',
                      }}
                    >
                      {stat.label}
                    </p>
                  </div>
                ))}
              </div>

              {/* Deploy CTA */}
              <button
                onClick={() => setSelectedAgent(null)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '100%',
                  padding: '14px',
                  borderRadius: 12,
                  background: 'linear-gradient(135deg, #FF6B35 0%, #FFD700 100%)',
                  color: '#0F1419',
                  fontWeight: 700,
                  fontSize: 15,
                  border: 'none',
                  cursor: 'pointer',
                  boxShadow: '0 0 36px rgba(255,107,53,0.45)',
                  transition: 'transform 0.18s, box-shadow 0.18s',
                  letterSpacing: '0.02em',
                }}
                onMouseEnter={(e) => {
                  const el = e.currentTarget as HTMLElement
                  el.style.transform = 'scale(1.025)'
                  el.style.boxShadow = '0 0 52px rgba(255,107,53,0.6)'
                }}
                onMouseLeave={(e) => {
                  const el = e.currentTarget as HTMLElement
                  el.style.transform = 'scale(1)'
                  el.style.boxShadow = '0 0 36px rgba(255,107,53,0.45)'
                }}
              >
                Deploy This Agent
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
