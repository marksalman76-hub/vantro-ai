'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { Zap } from 'lucide-react';
import { useToast } from '../context/ToastContext';

export function Toast() {
  const { visible, message } = useToast();

  return (
    <div
      className="fixed z-[300]"
      style={{ bottom: '1.5rem', right: '1.5rem' }}
      aria-live="polite"
      aria-atomic="true"
    >
      <AnimatePresence>
        {visible && (
          <motion.div
            key="toast"
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
            className="glass-card rounded-xl px-4 py-3 flex items-center gap-3 shadow-lg"
            style={{ border: '1px solid rgba(255,255,255,0.20)' }}
          >
            <Zap size={14} style={{ color: 'oklch(0.79 0 0)', flexShrink: 0 }} />
            <span className="text-sm" style={{ color: 'oklch(0.97 0 0)' }}>
              {message}
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
