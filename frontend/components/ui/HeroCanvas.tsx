'use client'

import { useRef, useMemo } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'

function Particles({ count = 1400 }: { count?: number }) {
  const mesh = useRef<THREE.Points>(null!)
  const { mouse, viewport } = useThree()

  const [positions, colors] = useMemo(() => {
    const pos = new Float32Array(count * 3)
    const col = new Float32Array(count * 3)
    const violet = new THREE.Color('#7C3AED')
    const blue   = new THREE.Color('#3B82F6')
    const cyan   = new THREE.Color('#06B6D4')
    const palette = [violet, blue, cyan]

    for (let i = 0; i < count; i++) {
      const r = 4 + Math.random() * 8
      const theta = Math.random() * Math.PI * 2
      const phi   = Math.acos(2 * Math.random() - 1)
      pos[i * 3]     = r * Math.sin(phi) * Math.cos(theta)
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.6
      pos[i * 3 + 2] = r * Math.cos(phi) - 2
      const c = palette[Math.floor(Math.random() * palette.length)]
      col[i * 3]     = c.r
      col[i * 3 + 1] = c.g
      col[i * 3 + 2] = c.b
    }
    return [pos, col]
  }, [count])

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    if (mesh.current) {
      mesh.current.rotation.y = t * 0.04
      mesh.current.rotation.x = Math.sin(t * 0.02) * 0.06
      // Subtle mouse parallax
      mesh.current.position.x = THREE.MathUtils.lerp(
        mesh.current.position.x,
        (mouse.x * viewport.width) / 30,
        0.03
      )
      mesh.current.position.y = THREE.MathUtils.lerp(
        mesh.current.position.y,
        (mouse.y * viewport.height) / 30,
        0.03
      )
    }
  })

  return (
    <points ref={mesh}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.025}
        vertexColors
        transparent
        opacity={0.55}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  )
}

function WireframeSphere() {
  const mesh = useRef<THREE.Mesh>(null!)

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    if (mesh.current) {
      mesh.current.rotation.x = t * 0.06
      mesh.current.rotation.y = t * 0.09
    }
  })

  return (
    <mesh ref={mesh} position={[0, 0, -3]}>
      <icosahedronGeometry args={[1.8, 1]} />
      <meshBasicMaterial
        color="#7C3AED"
        wireframe
        transparent
        opacity={0.08}
      />
    </mesh>
  )
}

export default function HeroCanvas() {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none" aria-hidden="true">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 60 }}
        gl={{ antialias: false, alpha: true }}
        dpr={[1, 1.5]}
        style={{ background: 'transparent' }}
      >
        <Particles />
        <WireframeSphere />
      </Canvas>
    </div>
  )
}
