'use client'

import { useRef, useMemo, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

// ─── Constants ────────────────────────────────────────────────────────────────
const ORBIT_R = 3.6

const AGENTS = [
  { color: '#7C3AED', angle: 0,   name: 'Atlas'  },
  { color: '#06B6D4', angle: 60,  name: 'Hermes' },
  { color: '#3B82F6', angle: 120, name: 'Oracle' },
  { color: '#EC4899', angle: 180, name: 'Muse'   },
  { color: '#10B981', angle: 240, name: 'Sage'   },
  { color: '#F59E0B', angle: 300, name: 'Forge'  },
]

function toRad(d: number) { return (d * Math.PI) / 180 }

// ─── Hub ──────────────────────────────────────────────────────────────────────
function Hub() {
  const ref = useRef<THREE.Mesh>(null!)
  useFrame((_, dt) => { ref.current.rotation.y += dt * 0.35 })
  return (
    <>
      <mesh ref={ref}>
        <sphereGeometry args={[0.72, 48, 48]} />
        <meshStandardMaterial
          color="#7C3AED"
          emissive="#5B21B6"
          emissiveIntensity={0.65}
          roughness={0.2}
          metalness={0.9}
        />
      </mesh>
      <pointLight position={[0, 0, 0]} intensity={2.2} color="#7C3AED" distance={7} decay={2} />
    </>
  )
}

// ─── Connection line (primitive, memoised) ────────────────────────────────────
function ConnLine({ pos, color }: { pos: [number, number, number]; color: string }) {
  const obj = useMemo(() => {
    const geo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(...pos),
    ])
    const mat = new THREE.LineBasicMaterial({ color, opacity: 0.22, transparent: true })
    return new THREE.Line(geo, mat)
  }, [pos, color])

  return <primitive object={obj} />
}

// ─── Agent sphere ─────────────────────────────────────────────────────────────
function AgentSphere({
  angle,
  color,
  timeOffset,
}: {
  angle: number
  color: string
  timeOffset: number
}) {
  const meshRef = useRef<THREE.Mesh>(null!)
  const t = useRef(timeOffset)
  const bx = Math.cos(toRad(angle)) * ORBIT_R
  const bz = Math.sin(toRad(angle)) * ORBIT_R

  useFrame((_, dt) => {
    t.current += dt
    meshRef.current.position.y = Math.sin(t.current * 0.75) * 0.25
  })

  return (
    <>
      <mesh ref={meshRef} position={[bx, 0, bz]}>
        <sphereGeometry args={[0.28, 24, 24]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
          roughness={0.3}
          metalness={0.7}
        />
      </mesh>
      <pointLight position={[bx, 0, bz]} intensity={0.55} color={color} distance={2.8} decay={2} />
    </>
  )
}

// ─── Orbit ring ───────────────────────────────────────────────────────────────
function OrbitRing() {
  const obj = useMemo(() => {
    const geo = new THREE.TorusGeometry(ORBIT_R, 0.018, 8, 80)
    const mat = new THREE.MeshBasicMaterial({ color: '#7C3AED', opacity: 0.12, transparent: true })
    const mesh = new THREE.Mesh(geo, mat)
    mesh.rotation.x = Math.PI / 2
    return mesh
  }, [])
  return <primitive object={obj} />
}

// ─── Orbiting group ───────────────────────────────────────────────────────────
function OrbitGroup() {
  const ref = useRef<THREE.Group>(null!)
  useFrame((_, dt) => { ref.current.rotation.y += dt * 0.17 })

  return (
    <group ref={ref}>
      <OrbitRing />
      {AGENTS.map((a, i) => {
        const bx = Math.cos(toRad(a.angle)) * ORBIT_R
        const bz = Math.sin(toRad(a.angle)) * ORBIT_R
        return (
          <group key={a.name}>
            <AgentSphere angle={a.angle} color={a.color} timeOffset={i * 1.05} />
            <ConnLine pos={[bx, 0, bz]} color={a.color} />
          </group>
        )
      })}
    </group>
  )
}

// ─── Scene ────────────────────────────────────────────────────────────────────
function Scene() {
  return (
    <>
      <ambientLight intensity={0.18} />
      <pointLight position={[8, 8, 4]} intensity={0.45} color="#fff" />
      <Hub />
      <OrbitGroup />
      <fog attach="fog" args={['#0F1A3F', 14, 30]} />
      <OrbitControls
        enableZoom={false}
        enablePan={false}
        minPolarAngle={Math.PI / 4}
        maxPolarAngle={(Math.PI * 3) / 4}
        autoRotate={false}
      />
    </>
  )
}

// ─── Export ───────────────────────────────────────────────────────────────────
export default function TeamVisualization3D() {
  return (
    <div className="w-full h-full" aria-hidden="true">
      <Canvas
        camera={{ position: [0, 4, 13], fov: 52 }}
        gl={{ antialias: true, alpha: true }}
        dpr={[1, 1.5]}
      >
        <Suspense fallback={null}>
          <Scene />
        </Suspense>
      </Canvas>
    </div>
  )
}
