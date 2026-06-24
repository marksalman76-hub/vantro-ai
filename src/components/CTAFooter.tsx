'use client';

import { motion, useReducedMotion } from 'framer-motion';

export function CTAFooter() {
  const prefersReduced = useReducedMotion();

  return (
    <section
      className="relative py-40 overflow-hidden"
      style={{ backgroundColor: 'oklch(0.28 0 0)' }}
    >
      {/* Radial glow behind orb */}
      <div
        className="absolute inset-0 flex items-center justify-center pointer-events-none"
        aria-hidden="true"
      >
        <div
          className="w-[600px] h-[600px] rounded-full blur-3xl"
          style={{ background: 'radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%)' }}
        />
      </div>

      {/* Orb image */}
      <div
        className="absolute inset-0 flex items-center justify-center pointer-events-none"
        aria-hidden="true"
      >
        <motion.div
          initial={prefersReduced ? false : { scale: 0.86, opacity: 0 }}
          whileInView={prefersReduced ? {} : { scale: 1, opacity: 1 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
          style={{ position: 'relative', width: '560px' }}
        >
          {!prefersReduced && (
            <motion.div
              animate={{
                background: [
                  'radial-gradient(circle 150px at 30% 28%, rgba(255,255,255,0.65) 0%, transparent 65%)',
                  'radial-gradient(circle 150px at 72% 22%, rgba(255,255,255,0.65) 0%, transparent 65%)',
                  'radial-gradient(circle 150px at 76% 74%, rgba(255,255,255,0.65) 0%, transparent 65%)',
                  'radial-gradient(circle 150px at 28% 78%, rgba(255,255,255,0.65) 0%, transparent 65%)',
                  'radial-gradient(circle 150px at 30% 28%, rgba(255,255,255,0.65) 0%, transparent 65%)',
                ],
              }}
              transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
              style={{
                position: 'absolute', inset: 0,
                mixBlendMode: 'screen',
                pointerEvents: 'none',
                zIndex: 2,
                WebkitMaskImage: 'radial-gradient(circle, black 16%, rgba(0,0,0,0.40) 42%, transparent 76%)',
                maskImage: 'radial-gradient(circle, black 16%, rgba(0,0,0,0.40) 42%, transparent 76%)',
              }}
            />
          )}
          <motion.img
            src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/saLNUqZiiYVuufKN.png"
            alt=""
            className="w-full"
            animate={prefersReduced ? {} : {
              y: [0, -22, -6, -30, -8, 0],
              x: [0, 14, -10, 8, -3, 0],
              scale: [1, 1.06, 0.97, 1.08, 0.99, 1],
            }}
            transition={{ duration: 11, repeat: Infinity, ease: 'easeInOut' }}
            style={{
              mixBlendMode: 'screen',
              opacity: 0.55,
              WebkitMaskImage: 'radial-gradient(circle, black 16%, rgba(0,0,0,0.40) 42%, transparent 76%)',
              maskImage: 'radial-gradient(circle, black 16%, rgba(0,0,0,0.40) 42%, transparent 76%)',
              position: 'relative',
              zIndex: 1,
            }}
          />
        </motion.div>
      </div>

      {/* Content */}
      <motion.div
        className="relative z-10 text-center max-w-3xl mx-auto px-6"
        initial={{ opacity: 0, y: 32 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.7 }}
      >
        <h2
          className="font-bold text-4xl md:text-6xl tracking-tight mb-6"
          style={{ fontFamily: 'Space Grotesk, sans-serif', color: 'oklch(0.97 0 0)' }}
        >
          Your AI workforce is one click away.
        </h2>
        <p
          className="text-lg max-w-lg mx-auto mb-10"
          style={{ color: 'oklch(0.70 0 0)' }}
        >
          Activate your first agents in minutes. No credit card. No integrations team. Just momentum.
        </p>

        <div className="flex justify-center">
          <a
            href="https://app.vantro.ai/signup"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-full px-8 py-4 font-semibold text-lg cursor-pointer"
            style={{
              background: 'linear-gradient(180deg, #ffffff 0%, #d8d8d8 100%)',
              color: 'oklch(0.14 0 0)',
              border: 'none',
              boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.60), 0 4px 16px rgba(0,0,0,0.40)',
              transition: 'opacity 0.2s ease, transform 0.15s ease',
              textDecoration: 'none',
              display: 'inline-block',
            }}
            onMouseEnter={(e) => {
              ;(e.currentTarget as HTMLAnchorElement).style.opacity = '0.88'
              ;(e.currentTarget as HTMLAnchorElement).style.transform = 'scale(1.02)'
            }}
            onMouseLeave={(e) => {
              ;(e.currentTarget as HTMLAnchorElement).style.opacity = '1'
              ;(e.currentTarget as HTMLAnchorElement).style.transform = 'scale(1)'
            }}
          >
            Activate your agents
          </a>
        </div>
      </motion.div>
    </section>
  );
}
