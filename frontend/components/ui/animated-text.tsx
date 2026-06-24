'use client'

import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface AnimatedTextProps {
  children: ReactNode
  className?: string
  delay?: number
  stagger?: boolean
}

export default function AnimatedText({ children, className = '', delay = 0, stagger = false }: AnimatedTextProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: stagger ? 0.03 : 0, delayChildren: delay } },
  }
  const letterVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  }

  return (
    <motion.span variants={containerVariants} initial="hidden" whileInView="visible" viewport={{ once: true }} className={className}>
      {typeof children === 'string'
        ? children.split('').map((char, i) => (
            <motion.span key={i} variants={stagger ? letterVariants : {}}>
              {char === ' ' ? ' ' : char}
            </motion.span>
          ))
        : children}
    </motion.span>
  )
}
