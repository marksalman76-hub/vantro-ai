'use client'

/*
 * WISA-pattern GSAP word-by-word ScrollReveal.
 * Wraps each word in a span, then uses ScrollTrigger to stagger them in.
 */

import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

interface ScrollRevealProps {
  children: string
  className?: string
  tag?: 'h1' | 'h2' | 'h3' | 'p' | 'span'
  stagger?: number
  duration?: number
  start?: string
  /** When true, only opacity (no y-slide) */
  fade?: boolean
}

export default function ScrollReveal({
  children,
  className = '',
  tag: Tag = 'p',
  stagger = 0.055,
  duration = 0.7,
  start = 'top 80%',
  fade = false,
}: ScrollRevealProps) {
  const wrapperRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const el = wrapperRef.current
    if (!el) return

    /* Split text into word spans */
    const words = children.trim().split(/\s+/)
    el.innerHTML = words
      .map((w) => `<span class="_word" style="display:inline-block; overflow:hidden; vertical-align:bottom; margin-right:0.28em;"><span class="_inner" style="display:inline-block;">${w}</span></span>`)
      .join('')

    const inners = el.querySelectorAll<HTMLElement>('._inner')

    gsap.set(inners, { opacity: 0, y: fade ? 0 : '100%' })

    const tween = gsap.to(inners, {
      opacity: 1,
      y: '0%',
      duration,
      ease: 'power3.out',
      stagger,
      scrollTrigger: {
        trigger: el,
        start,
        toggleActions: 'play none none none',
      },
    })

    return () => {
      tween.kill()
      ScrollTrigger.getAll().forEach((st) => {
        if (st.trigger === el) st.kill()
      })
    }
  }, [children, stagger, duration, start, fade])

  return (
    <Tag
      ref={wrapperRef as React.RefObject<HTMLParagraphElement & HTMLHeadingElement>}
      className={className}
    >
      {children}
    </Tag>
  )
}
