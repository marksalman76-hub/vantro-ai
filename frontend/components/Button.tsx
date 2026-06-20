'use client'

import React from 'react'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  href?: string
  arrow?: boolean
  children: React.ReactNode
}

const SIZE_CLASSES = {
  sm: 'px-4 py-2 text-sm',
  md: 'px-6 py-3 text-sm',
  lg: 'px-8 py-4 text-base',
}

const VARIANT_CLASSES = {
  primary: [
    'text-white font-semibold rounded-lg',
    'bg-gradient-to-r from-violet-600 to-blue-600',
    'hover:from-violet-500 hover:to-blue-500',
    'shadow-[0_4px_20px_rgba(124,58,237,0.35)] hover:shadow-[0_4px_35px_rgba(124,58,237,0.55)]',
    'focus:outline-none focus:ring-2 focus:ring-violet-500/50',
    'transition-all duration-200',
  ].join(' '),
  secondary: [
    'text-white font-semibold rounded-lg',
    'bg-white/[0.06] border border-white/20',
    'hover:bg-white/[0.10] hover:border-white/40',
    'focus:outline-none focus:ring-2 focus:ring-white/20',
    'transition-all duration-200',
  ].join(' '),
  ghost: [
    'text-white/70 font-medium rounded-lg',
    'hover:text-white hover:bg-white/[0.06]',
    'focus:outline-none focus:ring-2 focus:ring-white/20',
    'transition-all duration-200',
  ].join(' '),
}

export default function Button({
  variant = 'primary',
  size = 'md',
  href,
  arrow = false,
  className = '',
  children,
  ...props
}: ButtonProps) {
  const classes = `inline-flex items-center justify-center gap-2 ${SIZE_CLASSES[size]} ${VARIANT_CLASSES[variant]} ${className}`

  const content = (
    <>
      {children}
      {arrow && <ArrowRight className="w-4 h-4" />}
    </>
  )

  if (href) {
    return (
      <Link href={href} className={classes}>
        {content}
      </Link>
    )
  }

  return (
    <button className={classes} {...props}>
      {content}
    </button>
  )
}
