'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, X, Send, Minimize2 } from 'lucide-react'

interface Msg {
  id: number
  role: 'user' | 'bot'
  text: string
}

const WELCOME: Msg = {
  id: 0,
  role: 'bot',
  text: "Hey there! 👋 I'm Nexus, your Vantro AI guide. Ask me anything about our agents, pricing, integrations, or how Vantro adapts to your business.",
}

function respond(input: string): string {
  const lc = input.toLowerCase()
  if (/price|cost|plan|how much|subscription/.test(lc))
    return "Our plans start at $99/month for a single agent. Starter ($99/mo), Professional ($299/mo), Enterprise (custom). Every plan comes with a 14-day free trial — no card needed. Want me to walk you through what each includes?"
  if (/demo|show me|see it|watch|showcase/.test(lc))
    return "Absolutely! A 15-min personalised demo is the fastest way to see Vantro in action for your exact industry. Want me to help you book one? Just share your email and I'll set it up."
  if (/agent|atlas|hermes|oracle|muse|sage|forge/.test(lc))
    return "Vantro has 6 specialist agents: Atlas (Sales), Hermes (Support), Oracle (Research), Muse (Marketing), Sage (Data), and Forge (Operations). Each learns your brand and adapts to your industry. Which role interests you most?"
  if (/integrat|salesforce|hubspot|slack|notion|zapier/.test(lc))
    return "We connect with 1,000+ tools out of the box — Salesforce, HubSpot, Slack, Shopify, Stripe, and many more. No custom connector? Our team builds it within 5 business days. What stack are you running?"
  if (/industr|healthcare|finance|saas|ecommerce|retail|real estate|education/.test(lc))
    return "Vantro works across 50+ industries with zero reconfiguration! The agents automatically recognise your sector's language, workflows, and norms. What industry are you in? I'll show you the exact ROI numbers."
  if (/brand|voice|tone|sound like|personality/.test(lc))
    return "Brand voice learning is a Vantro superpower. By Day 7, your agents will sound indistinguishable from your best team member. They study your docs, past conversations, and communication style from day one."
  if (/learn|improve|smart|get better|evolve|adapt/.test(lc))
    return "Unlike static AI, Vantro agents learn from every interaction. By Month 1 they're performing 40% better than Day 1 — and they compound daily. The longer you use them, the smarter they get."
  if (/team|how many|scale|grow|multiple/.test(lc))
    return "Totally up to you! Start with one specialist (from $99/mo) and add more as you grow. Agents share context with each other, so a full team coordinates seamlessly. Most customers start solo and scale within 60 days."
  if (/hi|hello|hey|sup|yo/.test(lc))
    return "Hey! 👋 Great to meet you. I'm Nexus — here to help you figure out if Vantro is a good fit. What's your biggest operational challenge right now?"
  if (/thank|thanks|cheers|appreciate/.test(lc))
    return "You're very welcome! 😊 If you have more questions, I'm here 24/7. Want to kick off a free trial or book a demo? Both take under 5 minutes."
  if (/bye|goodbye|ciao|later/.test(lc))
    return "Take care! 👋 If you ever want to explore Vantro further, just come back — I'll be right here. Good luck with your business!"
  return "Great question! Vantro's agents are built to adapt to your exact situation. For a tailored answer, I'd suggest a quick 15-min demo with our team — they'll show you exactly how it works for your industry. Want me to help arrange that?"
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 px-3 py-2.5 rounded-2xl rounded-tl-sm bg-white/[0.06] w-fit">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-white/45"
          animate={{ y: [0, -4, 0] }}
          transition={{ duration: 0.6, delay: i * 0.15, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}
    </div>
  )
}

export default function AIChatbot() {
  const [isOpen,    setIsOpen]    = useState(false)
  const [messages,  setMessages]  = useState<Msg[]>([WELCOME])
  const [input,     setInput]     = useState('')
  const [isTyping,  setIsTyping]  = useState(false)
  const [msgId,     setMsgId]     = useState(1)
  const chatRef  = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight
    }
  }, [messages, isTyping])

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 350)
    }
  }, [isOpen])

  const send = () => {
    const text = input.trim()
    if (!text) return
    const id = msgId

    setMessages((prev) => [...prev, { id, role: 'user', text }])
    setMsgId((n) => n + 1)
    setInput('')
    setIsTyping(true)

    setTimeout(() => {
      const reply = respond(text)
      setIsTyping(false)
      setMessages((prev) => [...prev, { id: id + 1, role: 'bot', text: reply }])
      setMsgId((n) => n + 2)
    }, 1200 + Math.random() * 600)
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="w-80 h-[460px] flex flex-col rounded-2xl overflow-hidden border border-white/[0.10] shadow-[0_20px_60px_rgba(0,0,0,0.6)]"
            style={{ background: 'rgba(20, 29, 51, 0.96)', backdropFilter: 'blur(16px)' }}
          >
            {/* Header */}
            <div className="flex items-center gap-3 px-4 py-3 border-b border-white/[0.08] bg-violet-600/10">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-[0_0_15px_rgba(124,58,237,0.5)]">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white">Nexus</p>
                <p className="text-[10px] text-green-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
                  by Vantro · Online
                </p>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => { setMessages([WELCOME]); setMsgId(1) }}
                  className="p-1.5 rounded-lg text-white/35 hover:text-white/70 hover:bg-white/[0.06] transition-all"
                  aria-label="Clear conversation"
                  title="Clear chat"
                >
                  <Minimize2 className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-lg text-white/35 hover:text-white/70 hover:bg-white/[0.06] transition-all"
                  aria-label="Close chat"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div ref={chatRef} className="flex-1 overflow-y-auto p-4 space-y-3 scroll-smooth">
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-violet-600/80 text-white rounded-tr-sm'
                        : 'bg-white/[0.07] text-white/85 rounded-tl-sm border border-white/[0.07]'
                    }`}
                  >
                    {msg.text}
                  </div>
                </motion.div>
              ))}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <TypingDots />
                </motion.div>
              )}
            </div>

            {/* Input */}
            <div className="p-3 border-t border-white/[0.07] flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKey}
                placeholder="Ask me anything..."
                className="flex-1 bg-white/[0.05] border border-white/10 rounded-xl px-3.5 py-2 text-sm text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50 transition-colors min-w-0"
                aria-label="Chat message"
              />
              <button
                onClick={send}
                disabled={!input.trim() || isTyping}
                className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all bg-violet-600 hover:bg-violet-500 disabled:opacity-35 disabled:cursor-not-allowed"
                aria-label="Send message"
              >
                <Send className="w-3.5 h-3.5 text-white" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Launcher button */}
      <motion.button
        onClick={() => setIsOpen((v) => !v)}
        whileTap={{ scale: 0.92 }}
        className="w-14 h-14 rounded-full flex items-center justify-center shadow-[0_8px_30px_rgba(124,58,237,0.5)] bg-gradient-to-br from-violet-600 to-blue-600 transition-all hover:shadow-[0_8px_40px_rgba(124,58,237,0.7)]"
        aria-label="Open chat"
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.15 }}>
              <X className="w-5 h-5 text-white" />
            </motion.div>
          ) : (
            <motion.div key="open" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.15 }}>
              <Bot className="w-5 h-5 text-white" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    </div>
  )
}
