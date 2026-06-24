// Shared motion tokens — import these instead of hardcoding curves

export const EASE_OUT = [0.22, 1, 0.36, 1] as const

export const SPRING_POP = {
  type: 'spring',
  stiffness: 295,
  damping: 28,
} as const

export const SPRING_HOVER = {
  type: 'spring',
  stiffness: 400,
  damping: 30,
} as const

export const EASE_STANDARD = [0.25, 0.46, 0.45, 0.94] as const

export const DURATION_FAST = 0.2
export const DURATION_MED = 0.45
export const DURATION_SLOW = 0.7
