'use client'

import { useState, useRef } from 'react'
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion'
import { PhoneCall, TrendingUp, Clock, Zap, Sparkles } from 'lucide-react'
import Button from '@/components/Button'
import { SplineScene } from '@/components/ui/splite'
import { Spotlight } from '@/components/ui/spotlight'
import { AvatarGroupWithTooltips } from '@/components/ui/avatar-group-with-tooltip'

const STATS = [
  { icon: PhoneCall,  value: '500+', label: 'Teams Deployed', color: '#7C3AED' },
  { icon: TrendingUp, value: '340%', label: 'Average ROI',    color: '#3B82F6' },
  { icon: Clock,      value: '100h', label: 'Saved / Week',   color: '#06B6D4' },
  { icon: Zap,        value: '24/7', label: 'Always On',      color: '#10B981' },
]

const DIFFERENTIATORS = [
  { label: 'Any industry',        color: '#C084FC', border: 'rgba(192,132,252,0.25)' },
  { label: 'Single or full team', color: '#93C5FD', border: 'rgba(147,197,253,0.25)' },
  { label: 'Learns daily',        color: '#67E8F9', border: 'rgba(103,232,249,0.25)' },
  { label: 'Your brand voice',    color: '#F9A8D4', border: 'rgba(249,168,212,0.25)' },
]

function StatCard({ icon: Icon, value, label, color, index }: typeof STATS[0] & { index: number }) {
  const ref = useRef<HTMLDivElement>(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [5, -5]), { stiffness: 300, damping: 30 })
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-5, 5]), { stiffness: 300, damping: 30 })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.7 + index * 0.08, ease: [0.22, 1, 0.36, 1] }}
      onMouseMove={(e) => {
        const rect = ref.current?.getBoundingClientRect()
        if (!rect) return
        x.set((e.clientX - rect.left) / rect.width - 0.5)
        y.set((e.clientY - rect.top) / rect.height - 0.5)
      }}
      onMouseLeave={() => { x.set(0); y.set(0) }}
      style={{ rotateX, rotateY, transformPerspective: 600 }}
      className="glass-ultra rounded-2xl p-4 text-center group cursor-default relative overflow-hidden"
    >
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none rounded-2xl"
        style={{ background: `radial-gradient(circle at 50% 0%, ${color}18, transparent 70%)` }}
      />
      <div
        className="w-9 h-9 rounded-xl mx-auto flex items-center justify-center mb-2.5"
        style={{ background: `${color}18`, border: `1px solid ${color}30` }}
      >
        <Icon className="w-4 h-4" style={{ color }} />
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-[11px] text-white/45 mt-0.5 font-medium">{label}</p>
    </motion.div>
  )
}

export default function HeroSection() {
  const [sceneLoaded, setSceneLoaded] = useState(false)

  return (
    <section
      id="hero"
      className="relative min-h-screen flex flex-col justify-center overflow-hidden pt-20"
      style={{
        background: [
          'radial-gradient(ellipse 90% 65% at 50% -10%, rgba(124,58,237,0.20) 0%, transparent 60%)',
          'radial-gradient(ellipse 60% 55% at 85% 55%, rgba(59,130,246,0.10) 0%, transparent 60%)',
          '#070D1F',
        ].join(', '),
      }}
    >
      {/* Mesh grid overlay */}
      <div className="pointer-events-none absolute inset-0 mesh-grid opacity-50" />

      {/* Ambient blobs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-32 -right-32 w-[500px] h-[500px] rounded-full bg-violet-600/10 blur-[120px] animate-blob [will-change:transform]" />
        <div className="absolute -bottom-40 -left-20 w-[400px] h-[400px] rounded-full bg-blue-600/08 blur-[100px] animate-blob [will-change:transform]" style={{ animationDelay: '3s' }} />
        <div className="absolute top-1/2 left-1/3 w-[300px] h-[300px] rounded-full bg-cyan-500/06 blur-[80px] animate-blob [will-change:transform]" style={{ animationDelay: '6s' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-10 items-center py-16 lg:py-20">

          {/* ── Left: copy ─────────────────────────────────────────── */}
          <div className="flex flex-col items-start">

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
              className="mb-5"
            >
              <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold glass border border-violet-500/25 text-violet-300">
                <Sparkles className="w-3 h-3" />
                AI That Adapts to YOUR Business
              </span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.18, ease: [0.22, 1, 0.36, 1] }}
              className="text-4xl sm:text-5xl xl:text-[3.6rem] font-bold text-white leading-[1.1] mb-6 tracking-tight"
            >
              AI Agents That{' '}
              <span className="gradient-text">Adapt to You</span>
              <br />
              <span className="text-white/55 text-3xl sm:text-4xl xl:text-[2.8rem] font-medium leading-[1.25]">
                Not the Other Way Around
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.28, ease: [0.22, 1, 0.36, 1] }}
              className="text-base sm:text-lg text-white/55 leading-relaxed mb-7 max-w-lg"
            >
              Deploy autonomous AI agents that learn your industry, adopt your brand voice,
              and improve every day — handling sales, support, research, and operations
              around the clock.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.36, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-wrap gap-2 mb-8"
            >
              {DIFFERENTIATORS.map((d) => (
                <span
                  key={d.label}
                  className="px-3 py-1.5 rounded-full text-xs font-semibold"
                  style={{
                    background: `${d.color}12`,
                    color: d.color,
                    border: `1px solid ${d.border}`,
                  }}
                >
                  ✓ {d.label}
                </span>
              ))}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.44, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col sm:flex-row gap-3 mb-12"
            >
              <Button variant="primary" size="lg" arrow>Deploy to Any Industry</Button>
              <Button variant="secondary" size="lg">See It Adapt Live</Button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.52, ease: [0.22, 1, 0.36, 1] }}
              className="flex items-center gap-3"
            >
              <AvatarGroupWithTooltips />
              <p className="text-xs text-white/30">
                Trusted by{' '}
                {['Stripe', 'Notion', 'Linear', 'Vercel'].map((co, i) => (
                  <span key={co}>
                    <span className="text-white/55 font-semibold">{co}</span>
                    {i < 3 && <span className="mx-1.5 text-white/15">·</span>}
                  </span>
                ))}
              </p>
            </motion.div>
          </div>

          {/* ── Right: 3D scene ─────────────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, scale: 0.94 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
            className="relative h-[400px] lg:h-[540px]"
          >
            <div className="relative h-full rounded-3xl overflow-hidden glass-iridescent">
              <Spotlight className="-top-40 left-0 md:left-40 md:-top-20" fill="#a78bfa" />

              <div className="pointer-events-none w-full h-full">
                <SplineScene
                  scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
                  className="w-full h-full"
                  onLoad={() => setSceneLoaded(true)}
                />
              </div>

              <AnimatePresence>
                {!sceneLoaded && (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5 }}
                    className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#070D1F]/90 backdrop-blur-sm"
                  >
                    <div className="w-10 h-10 rounded-full border-2 border-violet-500/20 border-t-violet-400 animate-spin mb-3" />
                    <p className="text-xs text-white/35 font-medium">Loading 3D scene…</p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Floating agent cards */}
              <motion.div
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 1.0, ease: [0.22, 1, 0.36, 1] }}
                className="absolute top-5 right-4 glass-ultra rounded-2xl p-3 text-xs"
              >
                <div className="flex items-center gap-1.5 mb-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                  <p className="text-white/40 text-[10px] font-semibold tracking-wide">AGENT ONLINE</p>
                </div>
                <p className="text-white font-bold">Atlas · Sales</p>
                <p className="text-green-400 text-[10px] mt-0.5">Processing 23 leads</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 1.2, ease: [0.22, 1, 0.36, 1] }}
                className="absolute bottom-10 left-4 glass-ultra rounded-2xl p-3 text-xs animate-float [will-change:transform]"
                style={{ animationDelay: '1s', animationDuration: '3.5s' }}
              >
                <div className="flex items-center gap-1.5 mb-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                  <p className="text-white/40 text-[10px] font-semibold tracking-wide">JUST COMPLETED</p>
                </div>
                <p className="text-white font-bold">Hermes · Support</p>
                <p className="text-cyan-400 text-[10px] mt-0.5">↗ 47 tickets resolved</p>
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pb-14">
          {STATS.map((s, i) => (
            <StatCard key={s.label} {...s} index={i} />
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.4 }}
        className="absolute bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 pointer-events-none"
        aria-hidden="true"
      >
        <span className="text-[9px] uppercase tracking-[0.2em] text-white/20 font-semibold">Scroll</span>
        <div className="w-5 h-8 border border-white/12 rounded-full flex items-start justify-center pt-1.5">
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
            className="w-1 h-2 bg-violet-400/50 rounded-full"
          />
        </div>
      </motion.div>
    </section>
  )
}
