'use client'

import { useState, useEffect, useCallback } from 'react'
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
    metric: '15 hours saved / person / week',
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

function FullCard({ t }: { t: typeof TESTIMONIALS[0] }) {
  return (
    <div
      className="relative glass-ultra rounded-3xl p-8 lg:p-10 overflow-hidden h-full"
      style={{ border: `1px solid ${t.avatarColor}20` }}
    >
      <div className="absolute inset-0 rounded-3xl opacity-40 pointer-events-none"
        style={{ background: `radial-gradient(ellipse at 80% 20%, ${t.avatarColor}15 0%, transparent 60%)` }} />
      <div className="absolute top-0 left-12 right-12 h-px"
        style={{ background: `linear-gradient(90deg, transparent, ${t.avatarLight}50, transparent)` }} />

      <Quote className="absolute top-6 right-6 w-10 h-10 opacity-[0.08]" style={{ color: t.avatarColor }} />

      <div className="flex items-center gap-1 mb-5 relative z-10">
        {Array.from({ length: 5 }).map((_, i) => (
          <Star key={i} className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
        ))}
      </div>

      <div
        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold mb-6 relative z-10"
        style={{
          background: `${t.avatarColor}15`,
          color: t.metricColor,
          border: `1px solid ${t.avatarColor}30`,
          boxShadow: `0 4px 16px ${t.avatarColor}15`,
        }}
      >
        <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: t.metricColor }} />
        {t.metric}
      </div>

      <blockquote className="text-base lg:text-lg font-light text-white/85 leading-relaxed mb-8 relative z-10">
        &ldquo;{t.quote}&rdquo;
      </blockquote>

      <div className="flex items-center gap-3 relative z-10">
        <div
          className="w-11 h-11 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
          style={{
            background: `linear-gradient(135deg, ${t.avatarColor}, ${t.avatarColor}88)`,
            boxShadow: `0 4px 16px ${t.avatarColor}40`,
          }}
        >
          {t.avatar}
        </div>
        <div>
          <p className="font-bold text-white text-sm">{t.name}</p>
          <p className="text-xs text-white/40">{t.role} · {t.company}</p>
        </div>
      </div>
    </div>
  )
}

function MiniCard({ t, onClick }: { t: typeof TESTIMONIALS[0]; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="relative glass rounded-2xl p-5 overflow-hidden w-full h-full text-left cursor-pointer hover:bg-white/[0.07] transition-colors"
      style={{ border: `1px solid ${t.avatarColor}12` }}
    >
      <div
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold mb-4"
        style={{ background: `${t.avatarColor}12`, color: t.metricColor, border: `1px solid ${t.avatarColor}20` }}
      >
        <span className="w-1.5 h-1.5 rounded-full" style={{ background: t.metricColor }} />
        {t.metric}
      </div>
      <p className="text-xs text-white/50 leading-relaxed mb-4 line-clamp-3">
        &ldquo;{t.quote.slice(0, 100)}...&rdquo;
      </p>
      <div className="flex items-center gap-2">
        <div
          className="w-7 h-7 rounded-full flex items-center justify-center text-[9px] font-bold text-white flex-shrink-0"
          style={{ background: `linear-gradient(135deg, ${t.avatarColor}, ${t.avatarColor}88)` }}
        >
          {t.avatar}
        </div>
        <div>
          <p className="text-xs font-semibold text-white/70">{t.name}</p>
          <p className="text-[10px] text-white/30">{t.company}</p>
        </div>
      </div>
    </button>
  )
}

export default function Testimonials() {
  const [current, setCurrent] = useState(0)
  const n = TESTIMONIALS.length

  const prev = useCallback(() => setCurrent((c) => (c - 1 + n) % n), [n])
  const next = useCallback(() => setCurrent((c) => (c + 1) % n), [n])

  useEffect(() => {
    const id = setInterval(next, 10000)
    return () => clearInterval(id)
  }, [next])

  const prevIdx = (current - 1 + n) % n
  const nextIdx = (current + 1) % n
  const t = TESTIMONIALS[current]

  return (
    <section
      id="testimonials"
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #080D1E 0%, #0A1230 100%)' }}
    >
      <div className="absolute inset-0 mesh-grid-fine opacity-30 pointer-events-none" />
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] rounded-full blur-[160px] pointer-events-none transition-all duration-1000"
        style={{ background: `${t.avatarColor}10` }}
      />

      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          className="text-center mb-14"
        >
          <span className="section-badge-pink mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-pink-400 animate-pulse" />
            Real Results
          </span>
          <h2 className="section-heading mt-4 mb-4">
            Teams That Replaced Headcount{' '}
            <span className="gradient-text">With Vantro</span>
          </h2>
          <p className="section-sub mt-2">See what our customers have achieved in their first 90 days.</p>
        </motion.div>

        {/* Desktop: 3-up layout */}
        <div className="hidden lg:grid grid-cols-12 gap-5 items-stretch" style={{ perspective: '1200px' }}>
          {/* Prev card */}
          <motion.div
            key={`prev-${prevIdx}`}
            className="col-span-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.45, scale: 0.95 }}
            transition={{ duration: 0.4 }}
          >
            <MiniCard t={TESTIMONIALS[prevIdx]} onClick={prev} />
          </motion.div>

          {/* Active center card */}
          <div className="col-span-6 relative" style={{ perspective: '1200px' }}>
            <AnimatePresence mode="wait">
              <motion.div
                key={current}
                initial={{ opacity: 0, rotateY: 8, scale: 0.96 }}
                animate={{ opacity: 1, rotateY: 0, scale: 1 }}
                exit={{ opacity: 0, rotateY: -8, scale: 0.96 }}
                transition={{ type: 'spring', stiffness: 200, damping: 25 }}
                className="h-full"
              >
                <FullCard t={t} />
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Next card */}
          <motion.div
            key={`next-${nextIdx}`}
            className="col-span-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.45, scale: 0.95 }}
            transition={{ duration: 0.4 }}
          >
            <MiniCard t={TESTIMONIALS[nextIdx]} onClick={next} />
          </motion.div>
        </div>

        {/* Mobile: single card */}
        <div className="lg:hidden relative" style={{ perspective: '1200px' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={current}
              initial={{ opacity: 0, rotateY: 8, scale: 0.96, x: 40 }}
              animate={{ opacity: 1, rotateY: 0, scale: 1, x: 0 }}
              exit={{ opacity: 0, rotateY: -8, scale: 0.96, x: -40 }}
              transition={{ type: 'spring', stiffness: 200, damping: 25 }}
            >
              <FullCard t={t} />
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between mt-8">
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
          <div className="flex items-center gap-2">
            <motion.button onClick={prev} aria-label="Previous"
              whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.94 }}
              className="w-10 h-10 rounded-full glass-strong border border-white/10 flex items-center justify-center text-white/50 hover:text-white hover:border-white/30 transition-colors">
              <ChevronLeft className="w-4 h-4" />
            </motion.button>
            <motion.button onClick={next} aria-label="Next"
              whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.94 }}
              className="w-10 h-10 rounded-full glass-strong border border-white/10 flex items-center justify-center text-white/50 hover:text-white hover:border-white/30 transition-colors">
              <ChevronRight className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </div>
    </section>
  )
}
