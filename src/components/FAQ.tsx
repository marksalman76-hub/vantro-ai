'use client';

import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Plus } from 'lucide-react';

const FAQS = [
  {
    q: 'What exactly is a Vantro agent?',
    a: 'Each agent is an autonomous AI worker specialized for a role - support, finance, engineering, and more. They plan, take actions in your connected tools, verify results, and hand off to other agents through a shared memory layer.',
  },
  {
    q: 'Do I need to write code?',
    a: 'No. You brief agents in plain language and connect tools with a few clicks. Developers can go deeper with our API and custom-agent builder, but it is entirely optional.',
  },
  {
    q: 'How do you keep my data secure?',
    a: 'Vantro is SOC 2 Type II compliant with SSO, granular permissions, full audit logs, and per-workspace data isolation. You can place human-approval gates on any sensitive action.',
  },
  {
    q: 'Which tools can agents connect to?',
    a: 'Over 200 native integrations across CRM, support desks, finance, code hosting, messaging, and storage - with webhooks and an open API for everything else.',
  },
  {
    q: 'Can I control what agents are allowed to do?',
    a: 'Yes. Every agent runs inside guardrails you define, and you can require explicit approval before any action executes. You stay in command.',
  },
  {
    q: 'What happens if I outgrow my plan?',
    a: 'Plans scale with you. Upgrade anytime for more agents and actions, or move to Enterprise for unlimited potential and dedicated support.',
  },
];

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section id="faq" className="py-32" style={{ backgroundColor: 'oklch(0.09 0.04 260)' }}>
      <h2
        className="text-center mb-4 font-bold text-4xl md:text-5xl"
        style={{ fontFamily: 'Space Grotesk, sans-serif', color: 'oklch(0.97 0 0)' }}
      >
        Questions, answered.
      </h2>
      <p
        className="text-center mb-12 text-base"
        style={{ color: 'oklch(0.70 0 0)' }}
      >
        Everything you need to know before deploying your first agent.
      </p>

      <div className="max-w-2xl mx-auto px-6">
        {FAQS.map((item, i) => {
          const isOpen = openIndex === i;
          return (
            <div
              key={i}
              className={`${i < FAQS.length - 1 ? 'border-b' : ''}`}
              style={{ borderColor: 'rgba(255,255,255,0.08)' }}
            >
              <button
                className="w-full py-5 flex items-center justify-between text-left gap-4 cursor-pointer"
                onClick={() => setOpenIndex(isOpen ? null : i)}
                aria-expanded={isOpen}
              >
                <span
                  className="font-medium text-base"
                  style={{ color: 'oklch(0.97 0 0)' }}
                >
                  {item.q}
                </span>
                <motion.div
                  animate={{ rotate: isOpen ? 45 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex-shrink-0"
                >
                  <Plus size={18} style={{ color: 'oklch(0.70 0 0)' }} />
                </motion.div>
              </button>

              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    key="answer"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                    style={{ overflow: 'hidden' }}
                  >
                    <p
                      className="text-sm leading-relaxed pb-5"
                      style={{ color: 'oklch(0.70 0 0)' }}
                    >
                      {item.a}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </section>
  );
}
