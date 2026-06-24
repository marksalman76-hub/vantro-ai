'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface GlassCardProps {
  children: ReactNode
  hover?: boolean
  gradient?: boolean
  className?: string
}

export default function GlassCard({ children, hover = true, gradient = false, className = '' }: GlassCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={hover ? { y: -5, boxShadow: '0 20px 40px rgba(0,0,0,0.3)' } : {}}
      transition={{ duration: 0.3 }}
      viewport={{ once: true }}
      className={`glass rounded-2xl p-6 backdrop-blur-md border border-white/20 shadow-glass ${gradient ? 'bg-gradient-to-br from-white/10 to-white/5' : ''} ${hover ? 'cursor-pointer transition-all duration-300' : ''} ${className}`}
    >
      {children}
    </motion.div>
  )
}
