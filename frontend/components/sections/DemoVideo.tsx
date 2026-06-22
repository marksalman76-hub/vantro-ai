'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, Clock, ChevronRight } from 'lucide-react'

const VIDEO_ID = ''

export default function DemoVideo() {
  const [playing, setPlaying] = useState(false)

  const handlePlay = () => {
    if (VIDEO_ID) {
      setPlaying(true)
    } else {
      document.getElementById('agents')?.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <section
      id="demo-video"
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #0A1230 0%, #080D1E 100%)' }}
    >
      <div className="absolute inset-0 mesh-grid-fine opacity-40 pointer-events-none" />
      <div className="absolute top-0 right-1/4 w-[400px] h-[300px] bg-violet-600/08 blur-[100px] rounded-full pointer-events-none" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="text-center mb-12"
        >
          <span className="section-badge-cyan mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            See It In Action
          </span>
          <h2 className="section-heading mt-4 mb-4">
            Watch Vantro Handle{' '}
            <span className="gradient-text">Real Tasks in 2 Minutes</span>
          </h2>
          <p className="section-sub mt-2">
            Atlas qualifies leads. Hermes closes support tickets. Sage builds reports.
            All simultaneously, all autonomously.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 36, scale: 0.97 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 160, damping: 22, delay: 0.1 }}
          className="relative"
          style={{ perspective: '1200px' }}
        >
          {playing && VIDEO_ID ? (
            <div className="relative w-full rounded-2xl overflow-hidden shadow-[0_24px_80px_rgba(0,0,0,0.7)] glass-iridescent" style={{ paddingTop: '56.25%' }}>
              <iframe
                className="absolute inset-0 w-full h-full"
                src={`https://www.youtube.com/embed/${VIDEO_ID}?autoplay=1&rel=0&modestbranding=1`}
                title="Vantro Demo"
                allow="autoplay; encrypted-media; picture-in-picture"
                allowFullScreen
              />
            </div>
          ) : (
            <motion.div
              whileHover={{ rotateX: -1, scale: 1.01 }}
              transition={{ type: 'spring', stiffness: 200, damping: 25 }}
              className="relative w-full rounded-3xl overflow-hidden cursor-pointer group glass-iridescent"
              style={{ paddingTop: '56.25%', boxShadow: '0 32px 100px rgba(0,0,0,0.6), 0 0 0 1px rgba(124,58,237,0.2)' }}
              onClick={handlePlay}
              role="button"
              aria-label="Play demo video"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handlePlay()}
            >
              {/* Background */}
              <div className="absolute inset-0 bg-gradient-to-br from-[#08082A] via-[#12105A] to-[#080820]">
                {/* Grid */}
                <div
                  className="absolute inset-0 opacity-[0.06]"
                  style={{
                    backgroundImage: 'linear-gradient(rgba(124,58,237,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(124,58,237,0.8) 1px, transparent 1px)',
                    backgroundSize: '40px 40px',
                  }}
                />

                {/* Blobs */}
                <div className="absolute top-1/3 left-1/4 w-64 h-64 bg-violet-600/25 rounded-full blur-[80px]" />
                <div className="absolute bottom-1/3 right-1/4 w-48 h-48 bg-blue-600/20 rounded-full blur-[60px]" />
                <div className="absolute top-1/2 right-1/3 w-40 h-40 bg-cyan-500/15 rounded-full blur-[60px]" />

                {/* Mock agent UI */}
                <div className="absolute inset-8 sm:inset-16 flex items-center justify-center">
                  <div className="w-full max-w-md space-y-3 opacity-70">
                    {[
                      { color: '#7C3AED', light: '#C084FC', label: 'Atlas', task: 'Qualifying 23 inbound leads...', pct: '75%' },
                      { color: '#06B6D4', light: '#67E8F9', label: 'Hermes', task: 'Resolving support ticket #4821...', pct: '55%' },
                      { color: '#10B981', light: '#6EE7B7', label: 'Sage', task: 'Generating Q2 pipeline report...', pct: '90%' },
                    ].map((item) => (
                      <div key={item.label} className="glass-strong rounded-xl px-4 py-3 flex items-center gap-3" style={{ border: `1px solid ${item.color}25` }}>
                        <div className="w-2 h-2 rounded-full animate-pulse flex-shrink-0" style={{ background: item.light }} />
                        <span className="text-xs font-bold flex-shrink-0 w-14" style={{ color: item.light }}>{item.label}</span>
                        <span className="text-xs text-white/45 truncate flex-1">{item.task}</span>
                        <div className="w-16 h-1.5 rounded-full bg-white/10 flex-shrink-0 overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: item.pct }}
                            transition={{ duration: 1.5, delay: 0.5, ease: 'easeOut' }}
                            className="h-full rounded-full"
                            style={{ background: `linear-gradient(90deg, ${item.color}, ${item.light})` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Play button */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  whileHover={{ scale: 1.12 }}
                  whileTap={{ scale: 0.95 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                  className="relative"
                >
                  <div className="absolute inset-0 rounded-full bg-violet-500/30 animate-ping" style={{ animationDuration: '2s' }} />
                  <div className="relative w-20 h-20 rounded-full flex items-center justify-center glass-ultra border border-white/25 shadow-[0_0_50px_rgba(124,58,237,0.6)]">
                    <Play className="w-8 h-8 text-white fill-white ml-1" />
                  </div>
                </motion.div>
              </div>

              {/* Duration badge */}
              <div className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10">
                <Clock className="w-3 h-3 text-white/50" />
                <span className="text-xs text-white/65 font-semibold">2:00</span>
              </div>

              {/* Hover overlay */}
              <div className="absolute inset-0 bg-violet-600/0 group-hover:bg-violet-600/06 transition-colors duration-400 rounded-3xl" />
            </motion.div>
          )}

          {/* Caption */}
          <div className="flex items-center justify-between mt-5 px-1">
            <div className="flex items-center gap-3">
              <div className="flex -space-x-1.5">
                {['#7C3AED', '#06B6D4', '#10B981'].map((c, i) => (
                  <div key={i} className="w-6 h-6 rounded-full border-2 border-dark" style={{ background: c }} />
                ))}
              </div>
              <p className="text-xs text-white/40 font-medium">Atlas, Hermes & Sage in action</p>
            </div>
            <a
              href="#agents"
              className="inline-flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300 transition-colors font-semibold"
            >
              Explore all agents <ChevronRight className="w-3 h-3" />
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
