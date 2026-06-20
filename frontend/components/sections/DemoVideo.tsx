'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, Clock, ChevronRight } from 'lucide-react'

const VIDEO_ID = '' // Replace with your YouTube video ID when ready

export default function DemoVideo() {
  const [playing, setPlaying] = useState(false)

  const handlePlay = () => {
    if (VIDEO_ID) {
      setPlaying(true)
    } else {
      // No video yet — scroll to agents section
      document.getElementById('agents')?.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <section id="demo-video" className="section-padding bg-dark-900/60">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-cyan-500/20 text-cyan-300 mb-4">
            See It In Action
          </span>
          <h2 className="section-heading mb-4">
            Watch Vantro Handle{' '}
            <span className="gradient-text">Real Tasks in 2 Minutes</span>
          </h2>
          <p className="section-sub">
            Atlas qualifies leads. Hermes closes support tickets. Sage builds reports.
            All simultaneously, all autonomously.
          </p>
        </motion.div>

        {/* Video container */}
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.65, delay: 0.1 }}
          className="relative"
        >
          {playing && VIDEO_ID ? (
            /* Real YouTube embed */
            <div className="relative w-full rounded-2xl overflow-hidden shadow-[0_20px_80px_rgba(0,0,0,0.6)]" style={{ paddingTop: '56.25%' }}>
              <iframe
                className="absolute inset-0 w-full h-full"
                src={`https://www.youtube.com/embed/${VIDEO_ID}?autoplay=1&rel=0&modestbranding=1`}
                title="Vantro Demo"
                allow="autoplay; encrypted-media; picture-in-picture"
                allowFullScreen
              />
            </div>
          ) : (
            /* Polished placeholder thumbnail */
            <div
              className="relative w-full rounded-2xl overflow-hidden cursor-pointer group shadow-[0_20px_80px_rgba(0,0,0,0.6)] border border-white/[0.08]"
              style={{ paddingTop: '56.25%' }}
              onClick={handlePlay}
              role="button"
              aria-label="Play demo video"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handlePlay()}
            >
              {/* Background gradient */}
              <div className="absolute inset-0 bg-gradient-to-br from-dark-950 via-[#1a1060] to-dark-900">
                {/* Grid overlay */}
                <div
                  className="absolute inset-0 opacity-[0.07]"
                  style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)', backgroundSize: '40px 40px' }}
                />

                {/* Glow blobs */}
                <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-violet-600/20 rounded-full blur-[80px]" />
                <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-blue-600/15 rounded-full blur-[80px]" />

                {/* Mock UI elements */}
                <div className="absolute inset-6 sm:inset-12 flex items-center justify-center">
                  <div className="w-full max-w-lg space-y-3 opacity-60">
                    {[
                      { color: '#7C3AED', label: 'Atlas', task: 'Qualifying 23 inbound leads...', width: '75%' },
                      { color: '#06B6D4', label: 'Hermes', task: 'Resolving support ticket #4821...', width: '55%' },
                      { color: '#10B981', label: 'Sage', task: 'Generating Q2 pipeline report...', width: '90%' },
                    ].map((item) => (
                      <div key={item.label} className="glass rounded-xl px-4 py-3 flex items-center gap-3 border border-white/[0.06]">
                        <div className="w-2 h-2 rounded-full animate-pulse flex-shrink-0" style={{ background: item.color }} />
                        <span className="text-xs font-semibold flex-shrink-0" style={{ color: item.color }}>{item.label}</span>
                        <span className="text-xs text-white/45 truncate flex-1">{item.task}</span>
                        <div className="w-16 h-1 rounded-full bg-white/10 flex-shrink-0 overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: item.width, background: item.color, opacity: 0.7 }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Play button */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  whileHover={{ scale: 1.08 }}
                  className="relative"
                >
                  {/* Pulse ring */}
                  <div className="absolute inset-0 rounded-full bg-violet-500/30 animate-ping" />
                  <div className="relative w-18 h-18 sm:w-20 sm:h-20 rounded-full flex items-center justify-center bg-white/10 backdrop-blur-md border-2 border-white/30 shadow-[0_0_40px_rgba(124,58,237,0.5)]">
                    <Play className="w-7 h-7 sm:w-8 sm:h-8 text-white fill-white ml-1" />
                  </div>
                </motion.div>
              </div>

              {/* Duration badge */}
              <div className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-black/60 backdrop-blur-sm border border-white/10">
                <Clock className="w-3 h-3 text-white/60" />
                <span className="text-xs text-white/70 font-medium">2:00 min</span>
              </div>

              {/* Hover overlay */}
              <div className="absolute inset-0 bg-violet-600/0 group-hover:bg-violet-600/8 transition-colors duration-300" />
            </div>
          )}

          {/* Caption row */}
          <div className="flex items-center justify-between mt-4 px-1">
            <div className="flex items-center gap-4">
              <div className="flex -space-x-2">
                {['#7C3AED', '#06B6D4', '#10B981'].map((c, i) => (
                  <div key={i} className="w-6 h-6 rounded-full border-2 border-dark-900" style={{ background: c }} />
                ))}
              </div>
              <p className="text-xs text-white/45">Atlas, Hermes & Sage in action</p>
            </div>
            <a
              href="#agents"
              className="inline-flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300 transition-colors font-medium"
            >
              Explore all agents <ChevronRight className="w-3 h-3" />
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
