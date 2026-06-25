'use client';

import { useEffect, useState, useRef } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import {
  Zap, ArrowRight, Send, UserCheck, MessageCircle, BarChart2,
  Search, Code2, CheckCircle, Loader2,
} from 'lucide-react';

// ─── Live Agent Dashboard ────────────────────────────────────────────────────

type AgentStatus = 'active' | 'processing' | 'done';

interface LiveAgent {
  icon: React.ReactNode;
  name: string;
  task: string;
  doneTask: string;
  color: string;
}

const LIVE_AGENTS: LiveAgent[] = [
  { icon: <Send size={14} />, name: 'Outreach', task: 'Sending 47 personalized emails…', doneTask: 'Sent 47 emails ✓', color: '#FF6B35' },
  { icon: <UserCheck size={14} />, name: 'Lead Qualifier', task: 'Scoring 23 inbound leads…', doneTask: 'Qualified 23 leads ✓', color: '#00D9FF' },
  { icon: <MessageCircle size={14} />, name: 'Live Chat', task: 'Handling 5 conversations…', doneTask: 'Resolved 5 chats ✓', color: '#10B981' },
  { icon: <BarChart2 size={14} />, name: 'Report Gen', task: 'Building Q3 summary…', doneTask: 'Report ready ✓', color: '#FF6B35' },
  { icon: <Search size={14} />, name: 'SEO Agent', task: 'Analysing competitor gaps…', doneTask: 'Found 12 gaps ✓', color: '#00D9FF' },
  { icon: <Code2 size={14} />, name: 'Code Review', task: 'Reviewing 3 open PRs…', doneTask: 'Reviewed 3 PRs ✓', color: '#10B981' },
];

function AgentRow({ agent, index, prefersReduced }: { agent: LiveAgent; index: number; prefersReduced: boolean }) {
  const [status, setStatus] = useState<AgentStatus>('active');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (prefersReduced) return;
    const offset = index * 1400;
    let outerTimer: ReturnType<typeof setTimeout>;

    const cycle = () => {
      setStatus('processing');
      setProgress(0);
      let p = 0;
      const tick = setInterval(() => {
        p += 3 + Math.random() * 4;
        if (p >= 100) {
          clearInterval(tick);
          setProgress(100);
          setTimeout(() => {
            setStatus('done');
            setTimeout(() => { setStatus('active'); setProgress(0); }, 1800);
          }, 300);
        } else {
          setProgress(p);
        }
      }, 80);
    };

    outerTimer = setTimeout(() => {
      cycle();
      const interval = setInterval(cycle, 5200 + index * 600);
      return () => clearInterval(interval);
    }, offset);

    return () => clearTimeout(outerTimer);
  }, [index, prefersReduced]);

  const statusColor = status === 'done' ? '#10B981' : status === 'processing' ? agent.color : '#9CA3AF';

  return (
    <motion.div
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.45, delay: 0.3 + index * 0.08, ease: [0.22, 1, 0.36, 1] }}
      style={{
        backgroundColor: '#232936',
        border: '1px solid #2D3748',
        borderLeft: `3px solid ${agent.color}`,
        borderRadius: '0.5rem',
        padding: '0.625rem 0.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.375rem',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ color: agent.color }}>{agent.icon}</span>
          <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, fontSize: '0.8rem', color: '#FFFFFF' }}>
            {agent.name}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
          {status === 'done' ? (
            <CheckCircle size={12} color="#10B981" />
          ) : status === 'processing' ? (
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
              <Loader2 size={12} color={agent.color} />
            </motion.div>
          ) : (
            <motion.div
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#9CA3AF' }}
            />
          )}
          <span style={{ fontSize: '0.65rem', fontFamily: "'JetBrains Mono', monospace", color: statusColor, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {status === 'done' ? 'done' : status === 'processing' ? 'active' : 'idle'}
          </span>
        </div>
      </div>
      <p style={{ fontSize: '0.72rem', color: '#9CA3AF', margin: 0, lineHeight: 1.4 }}>
        {status === 'done' ? agent.doneTask : agent.task}
      </p>
      {status === 'processing' && (
        <div style={{ height: 2, backgroundColor: '#2D3748', borderRadius: 1, overflow: 'hidden' }}>
          <motion.div
            style={{ height: '100%', backgroundColor: agent.color, borderRadius: 1 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.1, ease: 'linear' }}
          />
        </div>
      )}
      {status === 'done' && <div style={{ height: 2, backgroundColor: '#10B981', borderRadius: 1, width: '100%' }} />}
    </motion.div>
  );
}

function AgentDashboard({ prefersReduced }: { prefersReduced: boolean }) {
  const [taskCount, setTaskCount] = useState(1247);

  useEffect(() => {
    if (prefersReduced) return;
    const interval = setInterval(() => setTaskCount(c => c + Math.floor(Math.random() * 3 + 1)), 2200);
    return () => clearInterval(interval);
  }, [prefersReduced]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
      style={{
        backgroundColor: '#1A1F2E',
        border: '1px solid #2D3748',
        borderRadius: '0.75rem',
        overflow: 'hidden',
        boxShadow: '0 24px 80px rgba(0,0,0,0.50)',
        willChange: 'transform, opacity',
      }}
    >
      {/* Header bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.875rem 1rem', borderBottom: '1px solid #2D3748', backgroundColor: '#161B27' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <motion.div
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1.2, repeat: Infinity }}
            style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#10B981' }}
          />
          <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, fontSize: '0.8rem', color: '#FFFFFF' }}>
            Agent Command Center
          </span>
        </div>
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.65rem', color: '#00D9FF', letterSpacing: '0.08em' }}>
          LIVE
        </span>
      </div>

      {/* Agents */}
      <div style={{ padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {LIVE_AGENTS.map((agent, i) => (
          <AgentRow key={agent.name} agent={agent} index={i} prefersReduced={prefersReduced} />
        ))}
      </div>

      {/* Footer counter */}
      <div style={{ padding: '0.75rem 1rem', borderTop: '1px solid #2D3748', backgroundColor: '#161B27', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.7rem', color: '#9CA3AF' }}>
          Tasks completed today
        </span>
        <motion.span
          key={taskCount}
          initial={{ y: 6, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.25 }}
          style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '0.9rem', color: '#FF6B35' }}
        >
          {taskCount.toLocaleString()}
        </motion.span>
      </div>
    </motion.div>
  );
}

// ─── Hero ────────────────────────────────────────────────────────────────────

const STATS = [
  { value: '1,000+', label: 'Teams deployed' },
  { value: '50M+', label: 'Tasks automated' },
  { value: '99.9%', label: 'Uptime SLA' },
];

export function Hero() {
  const prefersReduced = useReducedMotion() ?? false;
  const ref = useRef<HTMLElement>(null);

  return (
    <section
      ref={ref}
      style={{
        minHeight: '100dvh',
        background: 'linear-gradient(135deg, #0F1419 0%, #1A1F2E 100%)',
        display: 'flex',
        alignItems: 'center',
        paddingTop: '4rem',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Ambient glows */}
      <div aria-hidden="true" style={{ position: 'absolute', top: '25%', left: '10%', width: '35vw', height: '35vw', borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,107,53,0.07) 0%, transparent 70%)', pointerEvents: 'none' }} />
      <div aria-hidden="true" style={{ position: 'absolute', top: '15%', right: '8%', width: '28vw', height: '28vw', borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,217,255,0.06) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '4rem 1.5rem', width: '100%' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 26rem), 1fr))', gap: '4rem', alignItems: 'center' }}>

          {/* Left: copy */}
          <div>
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'rgba(255,107,53,0.12)', border: '1px solid rgba(255,107,53,0.28)', borderRadius: '2rem', padding: '0.375rem 0.875rem', marginBottom: '1.5rem' }}
            >
              <motion.div
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ duration: 1.4, repeat: Infinity }}
                style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#FF6B35' }}
              />
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.7rem', color: '#FF6B35', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                22 Specialized AI Agents
              </span>
            </motion.div>

            {/* H1 */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
              style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 800, fontSize: 'clamp(2rem, 5vw, 3.5rem)', lineHeight: 1.08, letterSpacing: '-0.03em', color: '#FFFFFF', marginBottom: '1.25rem' }}
            >
              Deploy 22 Specialized{' '}
              <span style={{ color: '#FF6B35' }}>AI Agents.</span>
              <br />
              Live in <span style={{ color: '#00D9FF' }}>5 Minutes.</span>
            </motion.h1>

            {/* Subtext */}
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
              style={{ color: '#9CA3AF', fontSize: '1.05rem', lineHeight: 1.65, marginBottom: '2rem', maxWidth: '30rem' }}
            >
              Replace fragmented tools and manual ops with an autonomous AI workforce —
              agents that sell, support, write, build, and report, around the clock.
            </motion.p>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
              style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '2.5rem' }}
            >
              <a
                href="/#pricing"
                className="btn-orange"
                style={{ padding: '0.875rem 1.75rem', borderRadius: '0.5rem', fontSize: '1rem', fontWeight: 700, textDecoration: 'none', boxShadow: '0 0 40px rgba(255,107,53,0.35), 0 4px 20px rgba(255,107,53,0.40), inset 0 1px 0 rgba(255,255,255,0.20)' }}
              >
                <Zap size={18} />
                Deploy now
              </a>
              <a
                href="#agents"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.375rem', color: '#E5E7EB', fontSize: '0.95rem', fontWeight: 500, textDecoration: 'none', transition: 'color 0.15s ease' }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#FFFFFF'; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#E5E7EB'; }}
              >
                See all 22 agents <ArrowRight size={16} />
              </a>
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.45 }}
              style={{ display: 'flex', gap: '2.5rem', flexWrap: 'wrap' }}
            >
              {STATS.map((stat) => (
                <div key={stat.label}>
                  <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1.3rem', color: '#FFFFFF' }}>
                    {stat.value}
                  </div>
                  <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.68rem', color: '#9CA3AF', letterSpacing: '0.06em', textTransform: 'uppercase', marginTop: '0.2rem' }}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Right: live dashboard */}
          <AgentDashboard prefersReduced={prefersReduced} />
        </div>
      </div>
    </section>
  );
}
