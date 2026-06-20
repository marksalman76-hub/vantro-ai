'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, Quote } from 'lucide-react'

const TESTIMONIALS = [
  {
    name: 'Sarah Chen',
    role: 'CTO',
    company: 'NovaTech Inc.',
    avatar: 'SC',
    avatarColor: '#7C3AED',
    metric: '340% ROI in 90 days',
    metricColor: '#7C3AED',
    quote:
      "We replaced a 4-person SDR team with Atlas and Hermes. In 90 days we had 340% ROI and our senior reps were actually doing senior work again. Vantro fundamentally changed how we think about headcount.",
  },
  {
    name: 'Marcus Rodriguez',
    role: 'Head of Operations',
    company: 'ScaleUp Labs',
    avatar: 'MR',
    avatarColor: '#06B6D4',
    metric: '15 hours saved per person / week',
    metricColor: '#06B6D4',
    quote:
      "Forge automated 23 workflows we had been meaning to build for two years. The setup took an afternoon. Our ops team now spends 15 fewer hours a week on repetitive tasks — and they actually enjoy their jobs now.",
  },
  {
    name: 'Emma Thompson',
    role: 'CEO',
    company: 'Frontier AI',
    avatar: 'ET',
    avatarColor: '#10B981',
    metric: '2× faster customer response',
    metricColor: '#10B981',
    quote:
      "Customer satisfaction jumped 28 points in two months. Hermes handles tier-1 support and escalates with full context, so our human agents only deal with the complex stuff. Response times halved overnight.",
  },
  {
    name: 'David Kim',
    role: 'VP of Sales',
    company: 'Apex Growth',
    avatar: 'DK',
    avatarColor: '#EC4899',
    metric: '68% more qualified pipeline',
    metricColor: '#EC4899',
    quote:
      "Atlas qualifies and sequences outbound better than any human SDR I've managed, and it does it at 3 AM on a Sunday. Our pipeline grew 68% in one quarter. The ROI pays for itself in the first week.",
  },
]

export default function Testimonials() {
  const [current, setCurrent] = useState(0)
  const n = TESTIMONIALS.length

  useEffect(() => {
    const id = setInterval(() => setCurrent((c) => (c + 1) % n), 6000)
    return () => clearInterval(id)
  }, [n])

  const prev = () => setCurrent((c) => (c - 1 + n) % n)
  const next = () => setCurrent((c) => (c + 1) % n)
  const t = TESTIMONIALS[current]

  return (
    <section id="testimonials" className="section-padding bg-dark-900/60">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-pink-500/20 text-pink-300 mb-4">
            Real Results
          </span>
          <h2 className="section-heading mb-4">Trusted by Forward-Thinking Teams</h2>
          <p className="section-sub">Don&apos;t take our word for it — see what our customers have achieved.</p>
        </motion.div>

        {/* Carousel card */}
        <div className="relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={current}
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.45, ease: [0.25, 0.1, 0.25, 1] }}
              className="glass rounded-3xl p-8 lg:p-12 relative"
            >
              {/* Quote icon */}
              <Quote
                className="absolute top-8 right-8 w-10 h-10 opacity-10"
                style={{ color: t.avatarColor }}
              />

              {/* Metric badge */}
              <div
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-sm font-bold mb-8"
                style={{ background: `${t.metricColor}18`, color: t.metricColor, border: `1px solid ${t.metricColor}35` }}
              >
                <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: t.metricColor }} />
                {t.metric}
              </div>

              {/* Quote text */}
              <blockquote className="text-xl lg:text-2xl font-light text-white/85 leading-relaxed mb-10">
                &ldquo;{t.quote}&rdquo;
              </blockquote>

              {/* Author */}
              <div className="flex items-center gap-4">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
                  style={{ background: `linear-gradient(135deg, ${t.avatarColor}, ${t.avatarColor}88)` }}
                >
                  {t.avatar}
                </div>
                <div>
                  <p className="font-semibold text-white">{t.name}</p>
                  <p className="text-sm text-white/45">{t.role} · {t.company}</p>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8">
            {/* Dots */}
            <div className="flex items-center gap-2">
              {TESTIMONIALS.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrent(i)}
                  aria-label={`Testimonial ${i + 1}`}
                  className="transition-all duration-300 rounded-full"
                  style={{
                    width: i === current ? '24px' : '8px',
                    height: '8px',
                    background: i === current ? '#7C3AED' : 'rgba(255,255,255,0.2)',
                  }}
                />
              ))}
            </div>

            {/* Arrows */}
            <div className="flex items-center gap-2">
              <button
                onClick={prev}
                aria-label="Previous"
                className="w-10 h-10 rounded-full glass border border-white/10 flex items-center justify-center text-white/50 hover:text-white hover:border-white/30 transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={next}
                aria-label="Next"
                className="w-10 h-10 rounded-full glass border border-white/10 flex items-center justify-center text-white/50 hover:text-white hover:border-white/30 transition-all"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
