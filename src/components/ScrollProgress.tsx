import { useScroll, motion } from 'framer-motion'

export function ScrollProgress() {
  const { scrollYProgress } = useScroll()
  return (
    <motion.div
      className="fixed top-0 left-0 right-0 h-[2px] bg-snow z-[200] origin-left"
      style={{ scaleX: scrollYProgress }}
    />
  )
}
