'use client';

import { useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Send, UserCheck, RefreshCw, TrendingUp,
  PenTool, Search, Share2,
  MessageCircle, GitMerge, BookOpen, Heart,
  Code2, Bug, Rocket, FileText,
  Receipt, DollarSign, Video, BarChart2,
  LineChart, Eye, Database,
  Plus,
} from 'lucide-react';

interface Agent {
  icon: React.ReactNode;
  name: string;
  category: string;
  description: string;
  integrations: number;
  accentColor: string;
}

const AGENTS: Agent[] = [
  // Sales
  { icon: <Send size={18} />, name: 'Outreach Agent', category: 'Sales', description: 'Personalised email sequences at scale', integrations: 14, accentColor: '#FF6B35' },
  { icon: <UserCheck size={18} />, name: 'Lead Qualifier', category: 'Sales', description: 'Scores and ranks inbound leads automatically', integrations: 9, accentColor: '#FF6B35' },
  { icon: <RefreshCw size={18} />, name: 'Follow-Up Agent', category: 'Sales', description: 'Multi-touch follow-up sequences on autopilot', integrations: 11, accentColor: '#FF6B35' },
  { icon: <TrendingUp size={18} />, name: 'Deal Closer', category: 'Sales', description: 'Surfaces deal risks and next-step prompts', integrations: 7, accentColor: '#FF6B35' },
  // Marketing
  { icon: <PenTool size={18} />, name: 'Content Writer', category: 'Marketing', description: 'Blog posts, ads, and copy on demand', integrations: 12, accentColor: '#00D9FF' },
  { icon: <Search size={18} />, name: 'SEO Optimizer', category: 'Marketing', description: 'Keyword research and on-page optimization', integrations: 8, accentColor: '#00D9FF' },
  { icon: <Share2 size={18} />, name: 'Social Media', category: 'Marketing', description: 'Schedules and publishes across all channels', integrations: 16, accentColor: '#00D9FF' },
  // Support
  { icon: <MessageCircle size={18} />, name: 'Live Chat Agent', category: 'Support', description: 'Resolves tickets and escalates when needed', integrations: 13, accentColor: '#10B981' },
  { icon: <GitMerge size={18} />, name: 'Ticket Router', category: 'Support', description: 'Classifies and routes to the right team', integrations: 10, accentColor: '#10B981' },
  { icon: <BookOpen size={18} />, name: 'Knowledge Base', category: 'Support', description: 'Maintains and updates docs automatically', integrations: 6, accentColor: '#10B981' },
  { icon: <Heart size={18} />, name: 'Customer Success', category: 'Support', description: 'Monitors health scores and triggers interventions', integrations: 9, accentColor: '#10B981' },
  // Engineering
  { icon: <Code2 size={18} />, name: 'Code Review', category: 'Engineering', description: 'Reviews PRs for bugs, style, and security', integrations: 8, accentColor: '#FF6B35' },
  { icon: <Bug size={18} />, name: 'Bug Hunter', category: 'Engineering', description: 'Finds regressions before they ship', integrations: 7, accentColor: '#FF6B35' },
  { icon: <Rocket size={18} />, name: 'Deploy Agent', category: 'Engineering', description: 'Manages CI/CD pipelines and rollbacks', integrations: 11, accentColor: '#FF6B35' },
  { icon: <FileText size={18} />, name: 'Docs Writer', category: 'Engineering', description: 'Auto-generates and updates technical docs', integrations: 6, accentColor: '#FF6B35' },
  // Operations
  { icon: <Receipt size={18} />, name: 'Invoice Agent', category: 'Operations', description: 'Creates, sends, and chases invoices', integrations: 12, accentColor: '#00D9FF' },
  { icon: <DollarSign size={18} />, name: 'Expense Tracker', category: 'Operations', description: 'Categorises and reconciles expenses', integrations: 9, accentColor: '#00D9FF' },
  { icon: <Video size={18} />, name: 'Meeting Summariser', category: 'Operations', description: 'Transcribes and extracts action items', integrations: 14, accentColor: '#00D9FF' },
  { icon: <BarChart2 size={18} />, name: 'Report Generator', category: 'Operations', description: 'Weekly/monthly reports on autopilot', integrations: 10, accentColor: '#00D9FF' },
  // Research
  { icon: <LineChart size={18} />, name: 'Market Research', category: 'Research', description: 'Surfaces trends and opportunity signals', integrations: 8, accentColor: '#10B981' },
  { icon: <Eye size={18} />, name: 'Competitor Monitor', category: 'Research', description: 'Tracks pricing, messaging, and product changes', integrations: 7, accentColor: '#10B981' },
  { icon: <Database size={18} />, name: 'Data Analyst', category: 'Research', description: 'Queries data and explains findings in plain English', integrations: 13, accentColor: '#10B981' },
];

function AgentCard({ agent, index }: { agent: Agent; index: number }) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [hovered, setHovered] = React.useState(false);

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const el = cardRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    el.style.setProperty('--mx', `${e.clientX - rect.left}px`);
    el.style.setProperty('--my', `${e.clientY - rect.top}px`);
  }

  return (
    <motion.div
      ref={cardRef}
      className="agent-card-cyan"
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.4, delay: (index % 6) * 0.05, ease: [0.22, 1, 0.36, 1] }}
      style={{ borderRadius: '0.625rem', padding: '1.125rem', cursor: 'default' }}
    >
      <div className="spotlight" />
      <div className="sheen" />

      {/* Icon + category */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem', position: 'relative', zIndex: 1 }}>
        <div style={{ width: 36, height: 36, borderRadius: '0.5rem', backgroundColor: `${agent.accentColor}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: agent.accentColor, flexShrink: 0 }}>
          {agent.icon}
        </div>
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.62rem', color: agent.accentColor, textTransform: 'uppercase', letterSpacing: '0.08em', backgroundColor: `${agent.accentColor}14`, padding: '0.2rem 0.5rem', borderRadius: '2rem' }}>
          {agent.category}
        </span>
      </div>

      {/* Name */}
      <h3 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, fontSize: '0.875rem', color: '#FFFFFF', marginBottom: '0.375rem', lineHeight: 1.3, position: 'relative', zIndex: 1 }}>
        {agent.name}
      </h3>

      {/* Description */}
      <p style={{ fontSize: '0.78rem', color: '#9CA3AF', lineHeight: 1.5, margin: 0, position: 'relative', zIndex: 1 }}>
        {agent.description}
      </p>

      {/* Integration count — shows on hover */}
      {hovered && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.375rem', position: 'relative', zIndex: 1 }}
        >
          <div style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#00D9FF' }} />
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.65rem', color: '#00D9FF' }}>
            {agent.integrations} integrations
          </span>
        </motion.div>
      )}
    </motion.div>
  );
}

// React import needed for useState inside component
import React from 'react';

export function Features() {
  return (
    <section
      id="agents"
      style={{ backgroundColor: '#0F1419', paddingTop: '6rem', paddingBottom: '6rem' }}
    >
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0 1.5rem' }}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          style={{ textAlign: 'center', marginBottom: '3.5rem' }}
        >
          <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 800, fontSize: 'clamp(1.75rem, 4vw, 2.75rem)', letterSpacing: '-0.025em', color: '#FFFFFF', marginBottom: '0.875rem', lineHeight: 1.1 }}>
            22 Agents.{' '}
            <span style={{ color: '#FF6B35' }}>Every Role Covered.</span>
          </h2>
          <p style={{ color: '#9CA3AF', fontSize: '1.05rem', maxWidth: '34rem', margin: '0 auto', lineHeight: 1.6 }}>
            Deploy the right specialist for every workflow. Each agent ships with deep integrations and runs autonomously from day one.
          </p>
        </motion.div>

        {/* 6-column grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 13rem), 1fr))', gap: '0.875rem' }}>
          {AGENTS.map((agent, i) => (
            <AgentCard key={agent.name} agent={agent} index={i} />
          ))}

          {/* +2 coming soon cards */}
          {[1, 2].map((n) => (
            <div
              key={n}
              style={{ borderRadius: '0.625rem', padding: '1.125rem', backgroundColor: '#1A1F2E', border: '1px dashed #2D3748', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', color: '#9CA3AF' }}
            >
              <Plus size={14} />
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.7rem', letterSpacing: '0.06em' }}>Coming soon</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
