'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, Quote, Star } from 'lucide-react'

const TESTIMONIALS = [
  {
    name: 'Sarah Chen',
    role: 'CTO',
    company: 'NovaTech Inc.',
    avatar: 'SC',
    avatarColor: '#7C3AED',
    avatarLight: '#C084FC',
    metric: '340% ROI in 90 days',
    metricColor: '#C084FC',
    quote: "We replaced a 4-person SDR team with Atlas and Hermes. In 90 days we had 340% ROI and our senior reps were actually doing senior work again. Vantro fundamentally changed how we think about headcount.",
  },
  {
    name: 'Marcus Rodriguez',
    role: 'Head of Operations',
    company: 'ScaleUp Labs',
    avatar: 'MR',
    avatarColor: '#06B6D4',
    avatarLight: '#67E8F9',
    metric: '15 hours saved per person / week',
    metricColor: '#67E8F9',
    quote: "Forge automated 23 workflows we had been meaning to build for two years. The setup took an afternoon. Our ops team now spends 15 fewer hours a week on repetitive tasks — and they actually enjoy their jobs now.",
  },
  {
    name: 'Emma Thompson',
    role: 'CEO',
    company: 'Frontier AI',
    avatar: 'ET',
    avatarColor: '#10B981',
    avatarLight: '#6EE7B7',
    metric: '2× faster customer response',
    metricColor: '#6EE7B7',
    quote: "Customer satisfaction jumped 28 points in two months. Hermes handles tier-1 support and escalates with full context, so our human agents only deal with the complex stuff. Response times halved overnight.",
  },
  {
    name: 'David Kim',
    role: 'VP of Sales',
    company: 'Apex Growth',
    avatar: 'DK',
    avatarColor: '#EC4899',
    avatarLight: '#F9A8D4',
    metric: '68% more qualified pipeline',
    metricColor: '#F9A8D4',
    quote: "Atlas qualifies and sequences outbound better than any human SDR I've managed, and it does it at 3 AM on a Sunday. Our pipeline grew 68% in one quarter. The ROI pays for itself in the first week.",
  },
]

export default function Testimonials() {
  const [current, setCurrent] = useState(0)
  const n = TESTIMONIALS.length

  useEffect(() => {
    const id = setInterval(() => setCurrent((c) => (c + 1) % n), 7000)
    return () => clearInterval(id)
  }, [n])

  const prev = () => setCurrent((c) => (c - 1 + n) % n)
  const next = () => setCurrent((c) => (c + 1) % n)
  const t = TESTIMONIALS[current]

  return (
    <section
      id="testimonials"
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #080D1E 0%, #0A1230 100%)' }}
    >
      {/* Background */}
      <div className="absolute inset-0 mesh-grid-fine opacity-30 pointer-events-none" />
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] rounded-full blur-[160px] pointer-events-none transition-all duration-1000"
        style={{ background: `${t.avatarColor}10` }}
      />

      <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="text-center mb-16"
        >
          <span className="section-badge-pink mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-pink-400 animate-pulse" />
            Real Results
          </span>
          <h2 className="section-heading mt-4 mb-4">
            Trusted by <span className="gradient-text">Forward-Thinking Teams</span>
          </h2>
          <p className="section-sub mt-2">Don&apos;t take our word for it — see what our customers have achieved.</p>
        </motion.div>

        {/* Carousel */}
        <div className="relative" style={{ perspective: '1200px' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={current}
              initial={{ opacity: 0, rotateY: 8, scale: 0.96, x: 40 }}
              animate={{ opacity: 1, rotateY: 0, scale: 1, x: 0 }}
              exit={{ opacity: 0, rotateY: -8, scale: 0.96, x: -40 }}
              transition={{ type: 'spring', stiffness: 200, damping: 25 }}
              className="relative glass-ultra rounded-3xl p-8 lg:p-12 overflow-hidden"
              style={{ border: `1px solid ${t.avatarColor}20` }}
            >
              {/* Dynamic gradient background */}
              <div
                className="absolute inset-0 rounded-3xl opacity-40 pointer-events-none transition-all duration-700"
                style={{
                  background: `radial-gradient(ellipse at 80% 20%, ${t.avatarColor}15 0%, transparent 60%)`,
                }}
              />

              {/* Top shine */}
              <div
                className="absolute top-0 left-12 right-12 h-px"
                style={{ background: `linear-gradient(90deg, transparent, ${t.avatarLight}50, transparent)` }}
              />

              {/* Quote icon */}
              <Quote
                className="absolute top-8 right-8 w-12 h-12 opacity-08"
                style={{ color: t.avatarColor }}
              />

              {/* Stars */}
              <div className="flex items-center gap-1 mb-6 relative z-10">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
                ))}
              </div>

              {/* Metric badge */}
              <div
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-bold mb-7 relative z-10"
                style={{
                  background: `${t.avatarColor}15`,
                  color: t.metricColor,
                  border: `1px solid ${t.avatarColor}30`,
                  boxShadow: `0 4px 20px ${t.avatarColor}15`,
                }}
              >
                <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: t.metricColor }} />
                {t.metric}
              </div>

              {/* Quote */}
              <blockquote className="text-xl lg:text-2xl font-light text-white/85 leading-relaxed mb-10 relative z-10">
                &ldquo;{t.quote}&rdquo;
              </blockquote>

              {/* Author */}
              <div className="flex items-center gap-4 relative z-10">
                <div
                  className="w-13 h-13 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0 shadow-lg"
                  style={{
                    background: `linear-gradient(135deg, ${t.avatarColor}, ${t.avatarColor}88)`,
                    width: 52,
                    height: 52,
                    boxShadow: `0 4px 20px ${t.avatarColor}40`,
                  }}
                >
                  {t.avatar}
                </div>
                <div>
                  <p className="font-bold text-white">{t.name}</p>
                  <p className="text-sm text-white/45 font-medium">{t.role} · {t.company}</p>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Controls */}
          <div className="flex items-center justify-between mt-8">
            {/* Progress dots */}
            <div className="flex items-center gap-2">
              {TESTIMONIALS.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrent(i)}
                  aria-label={`Testimonial ${i + 1}`}
                  className="transition-all duration-400 rounded-full focus:outline-none"
                  style={{
                    width: i === current ? 28 : 8,
                    height: 8,
                    background: i === current
                      ? `linear-gradient(90deg, ${TESTIMONIALS[i].avatarColor}, ${TESTIMONIALS[i].avatarLight})`
                      : 'rgba(255,255,255,0.15)',
                    boxShadow: i === current ? `0 0 12px ${TESTIMONIALS[i].avatarColor}60` : 'none',
                  }}
                />
              ))}
            </div>

            {/* Arrow buttons */}
            <div className="flex items-center gap-2">
              <motion.button
                onClick={prev}
                aria-label="Previous"
                whileHover={{ scale: 1.08 }}
                whileTap={{ scale: 0.94 }}
                className="w-11 h-11 rounded-full glass-strong border border-white/10 flex items-center justify-center text-white/50 hover:text-white hover:border-white/30 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </motion.button>
              <motion.button
                onClick={next}
                aria-label="Next"
                whileHover={{ scale: 1.08 }}
                whileTap={{ scale: 0.94 }}
                className="w-11 h-11 rounded-full glass-strong border border-white/10 flex items-center justify-center text-white/50 hover:text-white hover:border-white/30 transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
