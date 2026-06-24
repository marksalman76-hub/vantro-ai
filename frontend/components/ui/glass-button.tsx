'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface GlassButtonProps {
  children: ReactNode
  onClick?: () => void
  variant?: 'glass' | 'solid' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  className?: string
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

export default function GlassButton({
  children, onClick, variant = 'glass', size = 'md', className = '', disabled = false, type = 'button',
}: GlassButtonProps) {
  const base = 'font-semibold rounded-xl transition-all duration-300 flex items-center gap-2'
  const variants = {
    glass: 'glass text-white hover:bg-white/20',
    solid: 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-400 hover:to-purple-500 shadow-lg hover:shadow-blue-500/25',
    outline: 'border-2 border-white/30 text-white hover:bg-white/10',
  }
  const sizes = { sm: 'px-4 py-2 text-sm', md: 'px-6 py-3 text-base', lg: 'px-8 py-4 text-lg' }

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      onClick={onClick}
      disabled={disabled}
      type={type}
      className={`${base} ${variants[variant]} ${sizes[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      {children}
    </motion.button>
  )
}
