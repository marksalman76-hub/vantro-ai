'use client'

import { motion } from 'framer-motion'
import { ArrowRight, Calendar, Check } from 'lucide-react'
import Button from '@/components/Button'

const BULLETS = [
  '14-day free trial',
  'No credit card required',
  'Setup in under 10 minutes',
  'Cancel anytime',
]

export default function CTASection() {
  return (
    <section className="section-padding bg-dark relative overflow-hidden">
      {/* Background glow */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-violet-600/15 blur-[120px] rounded-full" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[300px] bg-blue-600/10 blur-[80px] rounded-full" />
      </div>

      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-violet-500/25 text-violet-300 mb-6">
            Get Started Today
          </span>

          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 leading-[1.1]">
            Ready to{' '}
            <span className="gradient-text">10× Your Team</span>
            <br />
            with AI Agents?
          </h2>

          <p className="text-lg text-white/55 mb-10 max-w-xl mx-auto">
            Join 500+ teams that have already deployed Vantro. Start free —
            your first agent is live in under 10 minutes.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
            <Button variant="primary" size="lg" arrow className="animate-glow-pulse">
              Start Free Trial
            </Button>
            <button className="inline-flex items-center gap-2 px-8 py-4 rounded-lg text-base font-semibold text-white border border-white/20 hover:border-white/40 hover:bg-white/[0.05] transition-all">
              <Calendar className="w-5 h-5 text-violet-400" />
              Book a Demo
            </button>
          </div>

          {/* Bullet list */}
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
            {BULLETS.map((b) => (
              <div key={b} className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-green-400 flex-shrink-0" />
                <span className="text-sm text-white/50">{b}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Social proof strip */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-16 glass rounded-2xl px-8 py-6 flex flex-col sm:flex-row items-center justify-center gap-8"
        >
          {[
            { value: '500+',  label: 'Active teams'         },
            { value: '4.9/5', label: 'Average rating'       },
            { value: '$2.4B', label: 'In tasks automated'   },
            { value: '99.9%', label: 'Uptime SLA'           },
          ].map(({ value, label }) => (
            <div key={label} className="text-center">
              <p className="text-2xl font-bold gradient-text-purple">{value}</p>
              <p className="text-xs text-white/40 mt-0.5">{label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
