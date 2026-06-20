'use client'

import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { DollarSign, Clock, TrendingUp, ArrowRight } from 'lucide-react'
import Button from '@/components/Button'

function Slider({
  label, value, min, max, step, format, onChange,
}: {
  label: string; value: number; min: number; max: number; step: number
  format: (v: number) => string; onChange: (v: number) => void
}) {
  const pct = ((value - min) / (max - min)) * 100
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-baseline">
        <label className="text-sm text-white/55">{label}</label>
        <span className="text-lg font-bold text-white">{format(value)}</span>
      </div>
      <div className="relative">
        <div className="h-1.5 rounded-full bg-white/10">
          <div
            className="h-1.5 rounded-full bg-gradient-to-r from-violet-500 to-blue-500 transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
        <input
          type="range" min={min} max={max} step={step} value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="absolute inset-0 w-full opacity-0 cursor-pointer h-5 -top-1.5"
          aria-label={label}
        />
        <div
          className="absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-white border-2 border-violet-500 shadow-[0_0_10px_rgba(124,58,237,0.5)] transition-all"
          style={{ left: `calc(${pct}% - 8px)` }}
        />
      </div>
    </div>
  )
}

const VANTRO_COST_PER_AGENT = 99

export default function ROICalculator() {
  const [teamSize,      setTeamSize]      = useState(10)
  const [hoursPerWeek,  setHoursPerWeek]  = useState(15)
  const [hourlyRate,    setHourlyRate]    = useState(75)
  const [agentCount,    setAgentCount]    = useState(3)

  const results = useMemo(() => {
    const hoursSavedPerYear   = teamSize * hoursPerWeek * 0.72 * 52
    const annualSavings       = hoursSavedPerYear * hourlyRate
    const annualVantroCost    = agentCount * VANTRO_COST_PER_AGENT * 12
    const netSavings          = annualSavings - annualVantroCost
    const roi                 = annualVantroCost > 0 ? ((annualSavings - annualVantroCost) / annualVantroCost) * 100 : 0
    const paybackDays         = annualVantroCost > 0 ? Math.round((annualVantroCost / annualSavings) * 365) : 0
    return { hoursSavedPerYear: Math.round(hoursSavedPerYear), annualSavings, netSavings, roi, paybackDays }
  }, [teamSize, hoursPerWeek, hourlyRate, agentCount])

  const fmt  = (n: number) => `$${n >= 1_000_000 ? (n / 1_000_000).toFixed(1) + 'M' : n >= 1000 ? (n / 1000).toFixed(0) + 'k' : n.toFixed(0)}`
  const fmtH = (n: number) => n >= 1000 ? `${(n / 1000).toFixed(1)}k` : `${n}`

  return (
    <section id="roi-calculator" className="section-padding bg-dark-900/70">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-14"
        >
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-green-500/20 text-green-300 mb-4">
            ROI Calculator
          </span>
          <h2 className="section-heading mb-4">See Your Return Before You Commit</h2>
          <p className="section-sub">Adjust the sliders to match your team — watch the savings add up in real time.</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="grid lg:grid-cols-2 gap-6 items-start"
        >
          {/* Inputs */}
          <div className="glass rounded-2xl p-7 space-y-7">
            <Slider
              label="Team size (people)"
              value={teamSize} min={1} max={200} step={1}
              format={(v) => `${v} people`}
              onChange={setTeamSize}
            />
            <Slider
              label="Hours per week on manual tasks (per person)"
              value={hoursPerWeek} min={1} max={40} step={1}
              format={(v) => `${v} hrs`}
              onChange={setHoursPerWeek}
            />
            <Slider
              label="Average hourly rate"
              value={hourlyRate} min={20} max={500} step={5}
              format={(v) => `$${v}/hr`}
              onChange={setHourlyRate}
            />
            <Slider
              label="Number of Vantro agents"
              value={agentCount} min={1} max={6} step={1}
              format={(v) => `${v} agent${v > 1 ? 's' : ''}`}
              onChange={setAgentCount}
            />
          </div>

          {/* Results */}
          <div className="space-y-4">
            {[
              {
                icon: Clock,
                label: 'Hours reclaimed per year',
                value: `${fmtH(results.hoursSavedPerYear)} hrs`,
                sub: `${Math.round(results.hoursSavedPerYear / teamSize)} hrs per person`,
                color: '#7C3AED',
              },
              {
                icon: DollarSign,
                label: 'Estimated annual savings',
                value: fmt(results.annualSavings),
                sub: `Vantro cost: ${fmt(agentCount * VANTRO_COST_PER_AGENT * 12)}/yr`,
                color: '#3B82F6',
              },
              {
                icon: TrendingUp,
                label: 'Projected ROI',
                value: `${Math.round(results.roi)}%`,
                sub: `Payback in ~${results.paybackDays} days`,
                color: '#10B981',
              },
            ].map(({ icon: Icon, label, value, sub, color }) => (
              <motion.div
                key={label}
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
                className="glass rounded-2xl p-6 flex items-center gap-5"
              >
                <div
                  className="w-12 h-12 rounded-xl flex-shrink-0 flex items-center justify-center"
                  style={{ background: `${color}20`, border: `1px solid ${color}45` }}
                >
                  <Icon className="w-5 h-5" style={{ color }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-white/45 mb-0.5">{label}</p>
                  <p
                    className="text-3xl font-bold tabular-nums"
                    style={{ color }}
                  >
                    {value}
                  </p>
                  <p className="text-xs text-white/35 mt-0.5">{sub}</p>
                </div>
              </motion.div>
            ))}

            <div className="glass rounded-2xl p-5 border border-green-500/20">
              <p className="text-xs text-green-300 font-semibold mb-1">Net savings after Vantro cost</p>
              <p className="text-4xl font-bold text-green-400 tabular-nums">
                {fmt(results.netSavings)}/yr
              </p>
            </div>

            <Button variant="primary" size="lg" className="w-full" arrow>
              Get My Custom ROI Report
            </Button>
            <p className="text-xs text-center text-white/30">Free report · No commitment · Sent to your inbox</p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
