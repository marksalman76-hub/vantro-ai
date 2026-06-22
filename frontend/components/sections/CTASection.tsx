'use client'

import { motion } from 'framer-motion'
import { ArrowRight, Calendar, Check, Sparkles } from 'lucide-react'
import Button from '@/components/Button'

const BULLETS = [
  '14-day free trial',
  'No credit card required',
  'Setup in under 10 minutes',
  'Cancel anytime',
]

const SOCIAL_PROOF = [
  { value: '500+',  label: 'Active teams'       },
  { value: '4.9/5', label: 'Average rating'     },
  { value: '$2.4B', label: 'Tasks automated'    },
  { value: '99.9%', label: 'Uptime SLA'         },
]

export default function CTASection() {
  return (
    <section
      className="section-padding relative overflow-hidden"
      style={{ background: 'linear-gradient(180deg, #0A1230 0%, #070D1F 100%)' }}
    >
      {/* Background mesh */}
      <div className="absolute inset-0 mesh-grid opacity-40 pointer-events-none" />

      {/* Dramatic ambient glows */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-violet-600/15 blur-[150px] rounded-full" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[300px] bg-blue-600/10 blur-[100px] rounded-full" />
        <div className="absolute top-0 left-1/4 w-[200px] h-[200px] bg-cyan-500/08 blur-[80px] rounded-full" />
        <div className="absolute bottom-0 right-1/4 w-[200px] h-[200px] bg-pink-500/06 blur-[80px] rounded-full" />
      </div>

      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 36 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 180, damping: 22 }}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ type: 'spring', stiffness: 260, damping: 20, delay: 0.1 }}
          >
            <span className="section-badge-violet mb-7 inline-flex">
              <Sparkles className="w-3 h-3" />
              Get Started Today
            </span>
          </motion.div>

          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 leading-[1.08] tracking-tight mt-4">
            Ready to{' '}
            <span className="gradient-text">10× Your Team</span>
            <br />
            with AI Agents?
          </h2>

          <p className="text-lg text-white/50 mb-10 max-w-xl mx-auto leading-relaxed">
            Join 500+ teams that have already deployed Vantro. Start free —
            your first agent is live in under 10 minutes.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
            <motion.div
              whileHover={{ scale: 1.04, y: -2 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
            >
              <Button variant="primary" size="lg" arrow>
                Start Free Trial
              </Button>
            </motion.div>

            <motion.button
              whileHover={{ scale: 1.04, y: -2 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              className="inline-flex items-center gap-2 px-7 py-4 rounded-xl text-base font-semibold text-white glass-strong border border-white/20 hover:border-violet-400/40 transition-colors duration-200"
            >
              <Calendar className="w-4 h-4 text-violet-300" />
              Book a Demo
            </motion.button>
          </div>

          {/* Bullets */}
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 mb-16">
            {BULLETS.map((b) => (
              <div key={b} className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span className="text-sm text-white/45 font-medium">{b}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Social proof strip */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, damping: 22, delay: 0.2 }}
          className="glass-iridescent rounded-2xl px-8 py-7 flex flex-col sm:flex-row items-center justify-center gap-8 sm:gap-12"
        >
          {SOCIAL_PROOF.map(({ value, label }) => (
            <div key={label} className="text-center">
              <p className="text-2xl font-black gradient-text-purple">{value}</p>
              <p className="text-xs text-white/40 mt-1 font-medium tracking-wide">{label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
