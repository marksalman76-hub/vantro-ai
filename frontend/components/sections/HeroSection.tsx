'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRight, PhoneCall, TrendingUp, Clock, Zap } from 'lucide-react'
import Button from '@/components/Button'
import { SplineScene } from '@/components/ui/splite'
import { Spotlight } from '@/components/ui/spotlight'
import { AvatarGroupWithTooltips } from '@/components/ui/avatar-group-with-tooltip'

const STATS = [
  { icon: PhoneCall,  value: '500+',  label: 'Teams Deployed'    },
  { icon: TrendingUp, value: '340%',  label: 'Average ROI'       },
  { icon: Clock,      value: '100h',  label: 'Saved / Week'      },
  { icon: Zap,        value: '24/7',  label: 'Always On'         },
]

const DIFFERENTIATORS = [
  { label: 'Any industry',       color: '#7C3AED' },
  { label: 'Single or full team',color: '#3B82F6' },
  { label: 'Learns daily',       color: '#06B6D4' },
  { label: 'Your brand voice',   color: '#EC4899' },
]

const fadeUp = (delay = 0) => ({
  initial:  { opacity: 0, y: 24 },
  animate:  { opacity: 1, y: 0  },
  transition: { duration: 0.6, delay, ease: 'easeOut' as const },
})

export default function HeroSection() {
  const [sceneLoaded, setSceneLoaded] = useState(false)

  return (
    <section
      id="hero"
      className="relative min-h-screen flex flex-col justify-center overflow-hidden bg-gradient-hero bg-dark pt-20"
    >
      {/* Background blobs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full bg-violet-600/10 blur-[100px] animate-blob" />
        <div className="absolute -bottom-40 -left-20 w-[400px] h-[400px] rounded-full bg-blue-600/10 blur-[100px] animate-blob" style={{ animationDelay: '3s' }} />
        <div className="absolute top-1/3 left-1/2 w-[300px] h-[300px] rounded-full bg-cyan-600/8 blur-[80px] animate-blob" style={{ animationDelay: '5s' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center py-16 lg:py-24">
          {/* Left — text */}
          <div className="flex flex-col items-start">
            <motion.div {...fadeUp(0.1)} className="mb-5">
              <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold glass border border-violet-500/25 text-violet-300">
                <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
                AI That Adapts to YOUR Business
              </span>
            </motion.div>

            <motion.h1 {...fadeUp(0.2)} className="text-4xl sm:text-5xl xl:text-6xl font-bold text-white leading-[1.1] mb-6">
              AI Agents That{' '}
              <span className="gradient-text">Adapt to You</span>
              <br />
              <span className="text-white/70 text-3xl sm:text-4xl xl:text-5xl font-medium">
                Not the Other Way Around
              </span>
            </motion.h1>

            <motion.p {...fadeUp(0.3)} className="text-base sm:text-lg text-white/60 leading-relaxed mb-6 max-w-lg">
              Deploy autonomous AI agents that learn your industry, adopt your brand voice, and improve every day —
              handling sales, support, research, and operations around the clock.
            </motion.p>

            {/* Differentiator tags */}
            <motion.div {...fadeUp(0.35)} className="flex flex-wrap gap-2 mb-8">
              {DIFFERENTIATORS.map((d) => (
                <span
                  key={d.label}
                  className="px-3 py-1 rounded-full text-xs font-semibold"
                  style={{ background: `${d.color}18`, color: d.color, border: `1px solid ${d.color}35` }}
                >
                  ✓ {d.label}
                </span>
              ))}
            </motion.div>

            <motion.div {...fadeUp(0.4)} className="flex flex-col sm:flex-row gap-3 mb-12">
              <Button variant="primary" size="lg" arrow>
                Deploy to Any Industry
              </Button>
              <Button variant="secondary" size="lg">
                See It Adapt to Your Business
              </Button>
            </motion.div>

            {/* Trust badges */}
            <motion.div {...fadeUp(0.5)} className="flex items-center gap-3">
              <AvatarGroupWithTooltips />
              <p className="text-xs text-white/35">
                Trusted by teams at{' '}
                {['Stripe', 'Notion', 'Linear', 'Vercel'].map((co, i) => (
                  <span key={co}>
                    <span className="text-white/55 font-medium">{co}</span>
                    {i < 3 && <span className="mx-1.5">·</span>}
                  </span>
                ))}
              </p>
            </motion.div>
          </div>

          {/* Right — Spline 3-D visualization */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.9, delay: 0.3 }}
            className="relative h-[420px] lg:h-[540px] rounded-2xl overflow-hidden"
          >
            {/* Spotlight sweep */}
            <Spotlight className="-top-40 left-0 md:left-40 md:-top-20" fill="#a78bfa" />

            <SplineScene
              scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
              className="w-full h-full"
              onLoad={() => setSceneLoaded(true)}
            />

            {/* Loading overlay — fades out once scene is ready */}
            <AnimatePresence>
              {!sceneLoaded && (
                <motion.div
                  key="loading"
                  initial={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.5 }}
                  className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-dark-950/80 backdrop-blur-sm"
                >
                  <div className="w-9 h-9 rounded-full border-2 border-violet-500/30 border-t-violet-400 animate-spin mb-3" />
                  <p className="text-xs text-white/40">Loading 3D scene…</p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Floating agent label cards */}
            <motion.div
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
              className="absolute top-6 right-4 glass rounded-xl p-3 shadow-lg text-xs"
            >
              <p className="text-white/50 mb-0.5">Agent Online</p>
              <p className="text-white font-semibold">Atlas · Sales</p>
              <p className="text-green-400 text-[10px] mt-0.5">● Processing 23 leads</p>
            </motion.div>

            <motion.div
              animate={{ y: [0, 6, 0] }}
              transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
              className="absolute bottom-10 left-4 glass rounded-xl p-3 shadow-lg text-xs"
            >
              <p className="text-white/50 mb-0.5">Just completed</p>
              <p className="text-white font-semibold">Hermes · Support</p>
              <p className="text-cyan-400 text-[10px] mt-0.5">↗ 47 tickets resolved</p>
            </motion.div>
          </motion.div>
        </div>

        {/* Stats bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="grid grid-cols-2 sm:grid-cols-4 gap-4 pb-12"
        >
          {STATS.map(({ icon: Icon, value, label }) => (
            <div key={label} className="glass rounded-xl p-4 text-center">
              <Icon className="w-5 h-5 text-violet-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-white">{value}</p>
              <p className="text-xs text-white/50 mt-0.5">{label}</p>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.4 }}
        className="absolute bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 pointer-events-none"
        aria-hidden="true"
      >
        <span className="text-[10px] uppercase tracking-widest text-white/25 font-medium">Scroll</span>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
          className="w-5 h-8 border border-white/15 rounded-full flex items-start justify-center pt-1.5"
        >
          <div className="w-1 h-1.5 bg-white/35 rounded-full" />
        </motion.div>
      </motion.div>
    </section>
  )
}
