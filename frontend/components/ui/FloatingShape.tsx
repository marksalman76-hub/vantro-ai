'use client'

import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

type ShapeType = 'torus' | 'icosahedron' | 'octahedron' | 'torusKnot'

function Shape({ type, color, speed = 1 }: { type: ShapeType; color: string; speed?: number }) {
  const mesh = useRef<THREE.Mesh>(null!)

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    if (mesh.current) {
      mesh.current.rotation.x = t * 0.3 * speed
      mesh.current.rotation.y = t * 0.5 * speed
      mesh.current.position.y = Math.sin(t * 0.4 * speed) * 0.15
    }
  })

  const mat = (
    <meshBasicMaterial
      color={color}
      wireframe
      transparent
      opacity={0.12}
    />
  )

  return (
    <mesh ref={mesh}>
      {type === 'torus'       && <torusGeometry       args={[1, 0.3, 8, 24]}   />}
      {type === 'icosahedron' && <icosahedronGeometry  args={[1.2, 0]}          />}
      {type === 'octahedron'  && <octahedronGeometry   args={[1.2]}             />}
      {type === 'torusKnot'   && <torusKnotGeometry    args={[0.8, 0.2, 80, 8]} />}
      {mat}
    </mesh>
  )
}

interface FloatingShapeProps {
  type?: ShapeType
  color?: string
  size?: number
  speed?: number
  className?: string
}

export default function FloatingShape({
  type = 'icosahedron',
  color = '#7C3AED',
  size = 120,
  speed = 0.8,
  className = '',
}: FloatingShapeProps) {
  return (
    <div
      className={`pointer-events-none select-none ${className}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <Canvas
        camera={{ position: [0, 0, 3.5], fov: 50 }}
        gl={{ antialias: false, alpha: true }}
        dpr={[1, 1.2]}
        style={{ background: 'transparent' }}
      >
        <Shape type={type} color={color} speed={speed} />
      </Canvas>
    </div>
  )
}
