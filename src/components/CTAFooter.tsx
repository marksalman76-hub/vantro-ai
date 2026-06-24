'use client';

import { motion } from 'framer-motion';
import { useToast } from '../context/ToastContext';

export function CTAFooter() {
  const { showToast } = useToast();

  return (
    <section
      className="relative py-40 overflow-hidden"
      style={{ backgroundColor: 'oklch(0.19 0 0)' }}
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
        <img
          src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/saLNUqZiiYVuufKN.png"
          alt=""
          className="w-[560px] max-w-none"
          style={{
            mixBlendMode: 'screen',
            opacity: 0.4,
            WebkitMaskImage: 'radial-gradient(circle, black 30%, transparent 70%)',
            maskImage: 'radial-gradient(circle, black 30%, transparent 70%)',
            animation: 'float 10s ease-in-out infinite',
          }}
        />
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

        <div className="flex gap-4 justify-center flex-wrap">
          <button
            onClick={() => showToast()}
            className="rounded-full px-8 py-4 font-semibold text-lg cursor-pointer"
            style={{
              background: 'linear-gradient(180deg, #ffffff 0%, #d8d8d8 100%)',
              color: 'oklch(0.14 0 0)',
              border: 'none',
              boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.60), 0 4px 16px rgba(0,0,0,0.40)',
              transition: 'opacity 0.2s ease, transform 0.15s ease',
            }}
            onMouseEnter={(e) => {
              ;(e.currentTarget as HTMLButtonElement).style.opacity = '0.88'
              ;(e.currentTarget as HTMLButtonElement).style.transform = 'scale(1.02)'
            }}
            onMouseLeave={(e) => {
              ;(e.currentTarget as HTMLButtonElement).style.opacity = '1'
              ;(e.currentTarget as HTMLButtonElement).style.transform = 'scale(1)'
            }}
          >
            Activate your agents
          </button>
          <button
            onClick={() => showToast()}
            className="rounded-full px-8 py-4 font-semibold text-lg transition-all duration-200 cursor-pointer"
            style={{
              border: '1px solid rgba(255,255,255,0.20)',
              color: 'oklch(0.97 0 0)',
              background: 'transparent',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.40)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.20)';
            }}
          >
            Book a demo
          </button>
        </div>
      </motion.div>
    </section>
  );
}
