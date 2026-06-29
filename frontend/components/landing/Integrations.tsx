'use client';

import { useState, useRef, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// ─── Data ─────────────────────────────────────────────────────────────────────

const INTEGRATIONS = [
  { name: 'Salesforce',   abbr: 'SF', category: 'Sales',       color: '#00A1E0' },
  { name: 'HubSpot',      abbr: 'HS', category: 'Sales',       color: '#FF7A59' },
  { name: 'Pipedrive',    abbr: 'PD', category: 'Sales',       color: '#A855F7' },
  { name: 'Outreach',     abbr: 'OR', category: 'Sales',       color: '#5951FF' },
  { name: 'LinkedIn',     abbr: 'LI', category: 'Sales',       color: '#0A66C2' },
  { name: 'Mailchimp',    abbr: 'MC', category: 'Creatives',   color: '#FFD700' },
  { name: 'Zendesk',      abbr: 'ZD', category: 'Support',     color: '#00D9FF' },
  { name: 'Intercom',     abbr: 'IC', category: 'Support',     color: '#1F8DED' },
  { name: 'Freshdesk',    abbr: 'FD', category: 'Support',     color: '#35AC47' },
  { name: 'Twilio',       abbr: 'TW', category: 'Support',     color: '#F22F46' },
  { name: 'Stripe',       abbr: 'ST', category: 'Ecommerce',   color: '#635BFF' },
  { name: 'QuickBooks',   abbr: 'QB', category: 'Ecommerce',   color: '#2CA01C' },
  { name: 'Xero',         abbr: 'XE', category: 'Operations',  color: '#13B5EA' },
  { name: 'Asana',        abbr: 'AS', category: 'Automation',  color: '#F06A6A' },
  { name: 'Monday.com',   abbr: 'MO', category: 'Automation',  color: '#FF3D57' },
  { name: 'Zapier',       abbr: 'ZP', category: 'Automation',  color: '#FF6B35' },
  { name: 'Jira',         abbr: 'JI', category: 'Engineering', color: '#0052CC' },
  { name: 'GitHub',       abbr: 'GH', category: 'Engineering', color: '#B084FF' },
  { name: 'Slack',        abbr: 'SL', category: 'Engineering', color: '#E01E5A' },
  { name: 'Notion',       abbr: 'NO', category: 'Creatives',   color: '#9CA3AF' },
  { name: 'Canva',        abbr: 'CV', category: 'Creatives',   color: '#7ED321' },
  { name: 'Segment',      abbr: 'SG', category: 'Creatives',   color: '#52BD95' },
  { name: 'Mixpanel',     abbr: 'MP', category: 'Automation',  color: '#7856FF' },
  { name: 'PostgreSQL',   abbr: 'PG', category: 'Engineering', color: '#336791' },
] as const;

type IntegrationName = typeof INTEGRATIONS[number]['name'];
type Category = 'All' | 'Sales' | 'Operations' | 'Engineering' | 'Support' | 'Automation' | 'Creatives' | 'Ecommerce';
const CATEGORIES: Category[] = ['All', 'Sales', 'Operations', 'Engineering', 'Support', 'Automation', 'Creatives', 'Ecommerce'];

const DESCRIPTIONS: Record<string, string> = {
  'Salesforce':   'CRM pipeline sync & lead qualification',
  'HubSpot':      'Marketing automation & contact scoring',
  'Pipedrive':    'Deal tracking & sales stage updates',
  'Outreach':     'Sequence automation & call analytics',
  'LinkedIn':     'Prospect enrichment & social signals',
  'Mailchimp':    'Email design automation & audience sync',
  'Zendesk':      'Ticket routing & resolution tracking',
  'Intercom':     'Live chat escalation & user messaging',
  'Freshdesk':    'Support ticket classification & SLA tracking',
  'Twilio':       'SMS & voice call automation',
  'Stripe':       'Checkout flows, payment events & subscription lifecycle',
  'QuickBooks':   'Order invoicing, revenue sync & financial reconciliation',
  'Xero':         'Accounting data & expense automation',
  'Asana':        'Task creation & project milestone alerts',
  'Monday.com':   'Workflow boards & team status sync',
  'Zapier':       'Cross-app automation & webhook routing',
  'Jira':         'Issue tracking & sprint progress sync',
  'GitHub':       'Code activity, PR reviews & CI signals',
  'Slack':        'Team notifications & channel automation',
  'Notion':       'Content creation & collaborative docs',
  'Canva':        'Design asset generation & brand templates',
  'Segment':      'Audience segmentation & creative targeting',
  'Mixpanel':     'Automated funnel triggers & event routing',
  'PostgreSQL':   'Direct database queries & data exports',
};

// ─── Node position math ───────────────────────────────────────────────────────

const CX = 450;
const CY = 360;
const RING_RADII = [155, 255, 350] as const;
const RING_OFFSETS = [0, Math.PI / 8, 0] as const;
const NODES_PER_RING = 8;

interface NodeData {
  x: number;
  y: number;
  integration: typeof INTEGRATIONS[number];
  index: number;
}

function computeNodes(): NodeData[] {
  const nodes: NodeData[] = [];
  let globalIndex = 0;
  for (let ring = 0; ring < 3; ring++) {
    const r = RING_RADII[ring];
    const offset = RING_OFFSETS[ring];
    for (let i = 0; i < NODES_PER_RING; i++) {
      const angle = (2 * Math.PI / NODES_PER_RING) * i + offset;
      nodes.push({
        x: CX + r * Math.cos(angle),
        y: CY + r * Math.sin(angle),
        integration: INTEGRATIONS[globalIndex],
        index: globalIndex,
      });
      globalIndex++;
    }
  }
  return nodes;
}

const ALL_NODES = computeNodes();

// ─── Tooltip ──────────────────────────────────────────────────────────────────

interface TooltipState {
  name: IntegrationName;
  x: number;
  y: number;
  color: string;
  category: string;
}

// ─── Particle ─────────────────────────────────────────────────────────────────

interface ParticleData {
  id: number;
  cx: number;
  cy: number;
  angle: number;
  color: string;
}

// ─── Category color map ───────────────────────────────────────────────────────

const CATEGORY_LINE_COLOR: Record<string, string> = {
  Sales:       '#FF6B35',
  Support:     '#00D9FF',
  Operations:  '#1FFFD6',
  Engineering: '#B084FF',
  Automation:  '#FFD700',
  Creatives:   '#FF9BCD',
  Ecommerce:   '#4ADE80',
};

// ─── Section ──────────────────────────────────────────────────────────────────

export default function Integrations() {
  const [activeCategory, setActiveCategory] = useState<Category>('All');
  const [hoveredPill, setHoveredPill] = useState<Category | null>(null);
  const [pressedPill, setPressedPill] = useState<Category | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const [clickedNode, setClickedNode] = useState<NodeData | null>(null);
  const [particles, setParticles] = useState<ParticleData[]>([]);

  const sectionRef = useRef<HTMLElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const constellationRef = useRef<HTMLDivElement>(null);
  const nodeGroupRefs = useRef<(SVGGElement | null)[]>([]);
  const nodeCircleRefs = useRef<(SVGCircleElement | null)[]>([]);
  const lineRefs = useRef<(SVGLineElement | null)[]>([]);
  const particleRefs = useRef<(SVGCircleElement | null)[]>([]);
  const particleIdCounter = useRef(0);

  // Memoize line lengths for dash animation
  const lineLengths = useMemo(() => {
    return ALL_NODES.map((node) => {
      const dx = node.x - CX;
      const dy = node.y - CY;
      return Math.sqrt(dx * dx + dy * dy);
    });
  }, []);

  // GSAP ScrollTrigger: stagger nodes and lines in on scroll
  useGSAP(
    () => {
      if (!sectionRef.current || !svgRef.current) return;

      const nodeElements = svgRef.current.querySelectorAll<SVGElement>('[data-node-group]');
      const lineElements = svgRef.current.querySelectorAll<SVGElement>('[data-connection-line]');
      const hubElement = svgRef.current.querySelector<SVGElement>('[data-hub]');

      // Set initial states
      gsap.set(nodeElements, { opacity: 0, scale: 0.5, transformOrigin: 'center center' });
      gsap.set(lineElements, { strokeDashoffset: (i: number) => lineLengths[i] ?? 200, opacity: 0 });
      if (hubElement) gsap.set(hubElement, { opacity: 0, scale: 0.3, transformOrigin: `${CX}px ${CY}px` });

      ScrollTrigger.create({
        trigger: sectionRef.current,
        start: 'top 70%',
        once: true,
        onEnter: () => {
          // Hub animates in first
          if (hubElement) {
            gsap.to(hubElement, {
              opacity: 1,
              scale: 1,
              duration: 0.6,
              ease: 'back.out(1.7)',
              transformOrigin: `${CX}px ${CY}px`,
            });
          }

          // Lines draw in with stagger
          gsap.to(lineElements, {
            strokeDashoffset: 0,
            opacity: 0.35,
            duration: 0.8,
            ease: 'power2.out',
            stagger: 0.04,
            delay: 0.3,
          });

          // Nodes pop in with stagger
          gsap.to(nodeElements, {
            opacity: 1,
            scale: 1,
            duration: 0.5,
            ease: 'back.out(1.4)',
            stagger: 0.04,
            delay: 0.35,
            transformOrigin: 'center center',
          });
        },
      });
    },
    { scope: sectionRef, dependencies: [] }
  );

  const isNodeActive = (node: NodeData): boolean => {
    if (activeCategory === 'All') return true;
    return node.integration.category === activeCategory;
  };

  const handleNodeEnter = (node: NodeData, e: React.MouseEvent<SVGGElement>) => {
    if (clickedNode) return;
    setHoveredIndex(node.index);
    const svgEl = svgRef.current;
    if (!svgEl) return;
    const svgRect = svgEl.getBoundingClientRect();
    const svgWidth = svgRect.width;
    const svgHeight = svgRect.height;
    const domX = (node.x / 720) * svgWidth + svgRect.left;
    const domY = (node.y / 720) * svgHeight + svgRect.top;
    setTooltip({
      name: node.integration.name,
      x: domX,
      y: domY,
      color: node.integration.color,
      category: node.integration.category,
    });
  };

  const handleNodeLeave = () => {
    if (clickedNode) return;
    setHoveredIndex(null);
    setTooltip(null);
  };

  const handleNodeClick = useCallback((node: NodeData) => {
    if (clickedNode) return;

    setTooltip(null);
    setHoveredIndex(null);

    const clickedCircle = nodeCircleRefs.current[node.index];
    if (!clickedCircle) return;

    // Fade other nodes
    ALL_NODES.forEach((n, i) => {
      if (i !== node.index) {
        const groupEl = nodeGroupRefs.current[i];
        if (groupEl) {
          gsap.to(groupEl, { opacity: 0.1, duration: 0.2, ease: 'power1.out' });
        }
      }
    });

    // Flash active connection line
    const activeLine = lineRefs.current[node.index];
    if (activeLine) {
      gsap.timeline()
        .to(activeLine, {
          opacity: 1,
          attr: { strokeWidth: 2 },
          duration: 0.15,
          ease: 'power2.out',
        })
        .to(activeLine, {
          opacity: 0.7,
          attr: { strokeWidth: 1.2 },
          duration: 0.3,
          ease: 'power1.inOut',
        });
    }

    // Explosion timeline on the node circle
    const tl = gsap.timeline();
    tl.to(clickedCircle, {
      scale: 3.5,
      svgOrigin: `${node.x} ${node.y}`,
      strokeWidth: 0,
      duration: 0.12,
      ease: 'power4.out',
    }).to(clickedCircle, {
      scale: 0.85,
      svgOrigin: `${node.x} ${node.y}`,
      strokeWidth: 1,
      duration: 0.25,
      ease: 'back.out(2)',
    });

    // Spawn 8 particles
    const newParticles: ParticleData[] = Array.from({ length: 8 }, (_, i) => ({
      id: particleIdCounter.current++,
      cx: node.x,
      cy: node.y,
      angle: i * 45,
      color: node.integration.color,
    }));
    setParticles(newParticles);

    // Animate particles after they are rendered — use a short rAF delay
    setTimeout(() => {
      newParticles.forEach((p, i) => {
        const el = particleRefs.current[i];
        if (!el) return;
        const rad = (p.angle * Math.PI) / 180;
        const dist = 45 + Math.random() * 25;
        const tx = Math.cos(rad) * dist;
        const ty = Math.sin(rad) * dist;
        gsap.fromTo(
          el,
          { opacity: 0.9, x: 0, y: 0 },
          {
            opacity: 0,
            x: tx,
            y: ty,
            duration: 0.5,
            ease: 'power2.out',
            delay: i * 0.02,
          }
        );
      });
      // Clear particles after animation
      setTimeout(() => {
        setParticles([]);
        particleRefs.current = [];
      }, 600);
    }, 16);

    // Show overlay after explosion settles
    setTimeout(() => {
      setClickedNode(node);
    }, 350);
  }, [clickedNode]);

  const handleCloseOverlay = useCallback(() => {
    if (!clickedNode) return;

    // Restore all nodes
    ALL_NODES.forEach((n, i) => {
      const groupEl = nodeGroupRefs.current[i];
      if (groupEl) {
        const targetOpacity = isNodeActive(n) ? 1 : 0.15;
        gsap.to(groupEl, { opacity: targetOpacity, duration: 0.3, ease: 'power1.out' });
      }
    });

    // Restore clicked node circle
    const clickedCircle = nodeCircleRefs.current[clickedNode.index];
    if (clickedCircle) {
      gsap.to(clickedCircle, {
        scale: 1,
        svgOrigin: `${clickedNode.x} ${clickedNode.y}`,
        strokeWidth: 1,
        duration: 0.35,
        ease: 'back.out(1.5)',
      });
    }

    // Restore active line
    const activeLine = lineRefs.current[clickedNode.index];
    if (activeLine) {
      gsap.to(activeLine, {
        opacity: 0.35,
        attr: { strokeWidth: 0.8 },
        duration: 0.3,
        ease: 'power1.out',
      });
    }

    setClickedNode(null);
  }, [clickedNode, activeCategory]);

  // Escape key to close overlay
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Escape') {
      handleCloseOverlay();
    }
  }, [handleCloseOverlay]);

  return (
    <>
      {/* Global pulse keyframes */}
      <style>{`
        @keyframes vantro-hub-pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.12); opacity: 0.85; }
        }
        @keyframes vantro-ring-pulse {
          0%, 100% { transform: scale(1); opacity: 0.18; }
          50% { transform: scale(1.08); opacity: 0.08; }
        }
      `}</style>

      <section
        id="integrations"
        ref={sectionRef}
        style={{ background: '#0F1419', paddingTop: 120, paddingBottom: 120 }}
      >
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px' }}>

          {/* ── Header ── */}
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <p
              style={{
                color: '#00D9FF',
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: '0.2em',
                textTransform: 'uppercase',
                marginBottom: 16,
                margin: '0 0 16px 0',
              }}
            >
              YOUR ENTIRE STACK
            </p>
            <h2
              style={{
                color: '#fff',
                fontSize: 'clamp(2rem, 3.5vw, 3.2rem)',
                fontWeight: 800,
                letterSpacing: '-0.025em',
                lineHeight: 1.1,
                margin: '0 0 16px 0',
                textWrap: 'balance',
              } as React.CSSProperties}
            >
              Connected to Everything
            </h2>
            <p
              style={{
                color: 'rgba(255,255,255,0.45)',
                fontSize: 18,
                margin: 0,
                lineHeight: 1.5,
              }}
            >
              One platform. Every tool you already use.
            </p>
          </div>

          {/* ── Category filter tabs ── */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              marginBottom: 48,
            }}
          >
            {CATEGORIES.map((cat) => {
              const isActive = activeCategory === cat;
              const isHoveredPill = hoveredPill === cat;
              const isPressedPill = pressedPill === cat;
              return (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setActiveCategory(cat)}
                  onMouseEnter={() => setHoveredPill(cat)}
                  onMouseLeave={() => { setHoveredPill(null); setPressedPill(null); }}
                  onMouseDown={() => setPressedPill(cat)}
                  onMouseUp={() => setPressedPill(null)}
                  style={{
                    position: 'relative',
                    padding: '8px 20px',
                    borderRadius: 20,
                    fontSize: 14,
                    fontWeight: 500,
                    background: isActive
                      ? 'transparent'
                      : isHoveredPill
                        ? 'rgba(255,255,255,0.08)'
                        : 'transparent',
                    border: isActive ? 'none' : '1px solid rgba(255,255,255,0.10)',
                    cursor: 'pointer',
                    outline: 'none',
                    color: isActive ? '#fff' : '#9CA3AF',
                    transform: isPressedPill
                      ? 'scale(0.97)'
                      : isHoveredPill && !isActive
                        ? 'scale(1.03)'
                        : 'scale(1)',
                    transition: 'background 200ms ease, transform 150ms ease-out, box-shadow 200ms ease',
                    boxShadow: isActive && isHoveredPill
                      ? '0 0 12px rgba(255,107,53,0.25)'
                      : 'none',
                  }}
                >
                  {isActive && (
                    <motion.span
                      layoutId="integration-tab-pill"
                      style={{
                        position: 'absolute',
                        inset: 0,
                        borderRadius: 20,
                        background: '#FF6B35',
                      }}
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}
                  <span style={{ position: 'relative', zIndex: 1 }}>
                    {cat}
                  </span>
                </button>
              );
            })}
          </div>

          {/* ── SVG Constellation ── */}
          <div
            ref={constellationRef}
            style={{
              display: 'flex',
              justifyContent: 'center',
              position: 'relative',
            }}
          >
            {/* Ambient background glows */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                pointerEvents: 'none',
                background:
                  'radial-gradient(ellipse 60% 60% at 50% 50%, rgba(0,217,255,0.06) 0%, transparent 70%)',
              }}
            />
            <div
              style={{
                position: 'absolute',
                inset: 0,
                pointerEvents: 'none',
                background:
                  'radial-gradient(ellipse 40% 40% at 50% 50%, rgba(255,107,53,0.04) 0%, transparent 60%)',
              }}
            />

            <svg
              ref={svgRef}
              viewBox="0 0 900 720"
              style={{
                width: '100%',
                maxWidth: 600,
                aspectRatio: '1',
                overflow: 'visible',
              }}
              aria-label="Vantro integration network"
            >
              <defs>
                {/* Hub glow filter */}
                <filter id="hub-glow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="8" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                {/* Node glow filter */}
                <filter id="node-glow" x="-80%" y="-80%" width="260%" height="260%">
                  <feGaussianBlur stdDeviation="4" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                {/* Line glow */}
                <filter id="line-glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                {/* Explosion glow filter */}
                <filter id="explosion-glow" x="-100%" y="-100%" width="300%" height="300%">
                  <feGaussianBlur stdDeviation="6" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                {/* Radial gradient for hub */}
                <radialGradient id="hub-gradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#00D9FF" stopOpacity="0.9" />
                  <stop offset="60%" stopColor="#FF6B35" stopOpacity="0.7" />
                  <stop offset="100%" stopColor="#B084FF" stopOpacity="0.3" />
                </radialGradient>
              </defs>

              {/* ── Connection lines (behind nodes) ── */}
              {ALL_NODES.map((node, i) => {
                const active = isNodeActive(node);
                const lineColor = CATEGORY_LINE_COLOR[node.integration.category] ?? '#fff';
                const isHovered = hoveredIndex === i;
                const length = lineLengths[i] ?? 200;
                return (
                  <line
                    key={`line-${i}`}
                    ref={(el) => { lineRefs.current[i] = el; }}
                    data-connection-line
                    x1={CX}
                    y1={CY}
                    x2={node.x}
                    y2={node.y}
                    stroke={lineColor}
                    strokeWidth={isHovered ? 1.5 : 0.8}
                    strokeDasharray={`${length}`}
                    strokeLinecap="round"
                    filter={isHovered ? 'url(#line-glow)' : undefined}
                    style={{
                      opacity: active ? (isHovered ? 0.9 : 0.35) : 0.05,
                      transition: 'opacity 0.3s ease, stroke-width 0.2s ease',
                    }}
                  />
                );
              })}

              {/* ── Subtle ring guides ── */}
              {RING_RADII.map((r, i) => (
                <circle
                  key={`ring-guide-${i}`}
                  cx={CX}
                  cy={CY}
                  r={r}
                  fill="none"
                  stroke="rgba(255,255,255,0.04)"
                  strokeWidth={0.5}
                  strokeDasharray="4 8"
                />
              ))}

              {/* ── Center hub ── */}
              <g data-hub>
                {/* Outer pulse ring */}
                <circle
                  cx={CX}
                  cy={CY}
                  r={44}
                  fill="none"
                  stroke="#00D9FF"
                  strokeWidth={0.6}
                  strokeOpacity={0.18}
                  style={{
                    animation: 'vantro-ring-pulse 3s ease-in-out infinite',
                    transformOrigin: `${CX}px ${CY}px`,
                  }}
                />
                {/* Hub circle */}
                <circle
                  cx={CX}
                  cy={CY}
                  r={28}
                  fill="url(#hub-gradient)"
                  filter="url(#hub-glow)"
                  style={{
                    animation: 'vantro-hub-pulse 3s ease-in-out infinite',
                    transformOrigin: `${CX}px ${CY}px`,
                  }}
                />
                {/* Hub border */}
                <circle
                  cx={CX}
                  cy={CY}
                  r={28}
                  fill="none"
                  stroke="#00D9FF"
                  strokeWidth={1.2}
                  strokeOpacity={0.7}
                  style={{
                    animation: 'vantro-hub-pulse 3s ease-in-out infinite',
                    transformOrigin: `${CX}px ${CY}px`,
                  }}
                />
                {/* Hub label */}
                <text
                  x={CX}
                  y={CY + 1}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="#fff"
                  fontSize={10}
                  fontWeight={800}
                  letterSpacing="0.04em"
                  style={{ userSelect: 'none' }}
                >
                  VANTRO
                </text>
              </g>

              {/* ── Integration nodes ── */}
              {ALL_NODES.map((node, i) => {
                const active = isNodeActive(node);
                const isHovered = hoveredIndex === i;
                const { color, abbr } = node.integration;
                const r = 36;

                return (
                  <motion.g
                    key={`node-${i}`}
                    ref={(el) => { nodeGroupRefs.current[i] = el as SVGGElement | null; }}
                    data-node-group
                    style={{ cursor: 'pointer' }}
                    animate={{
                      opacity: active ? 1 : 0.15,
                    }}
                    transition={{ duration: 0.3, ease: 'easeOut' }}
                    onMouseEnter={(e) => handleNodeEnter(node, e as unknown as React.MouseEvent<SVGGElement>)}
                    onMouseLeave={handleNodeLeave}
                    onClick={() => handleNodeClick(node)}
                  >
                    {/* Hover glow ring */}
                    {isHovered && (
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={r + 8}
                        fill="none"
                        stroke={color}
                        strokeWidth={1}
                        strokeOpacity={0.4}
                        filter="url(#node-glow)"
                      />
                    )}

                    {/* Node background circle */}
                    <circle
                      ref={(el) => { nodeCircleRefs.current[i] = el; }}
                      cx={node.x}
                      cy={node.y}
                      r={r}
                      fill={isHovered ? `${color}28` : `${color}12`}
                      stroke={color}
                      strokeWidth={isHovered ? 1.5 : 1}
                      strokeOpacity={isHovered ? 0.9 : 0.5}
                      filter={isHovered ? 'url(#node-glow)' : undefined}
                      style={{
                        transform: isHovered ? `scale(1.2)` : 'scale(1)',
                        transformOrigin: `${node.x}px ${node.y}px`,
                        transition: 'transform 0.2s cubic-bezier(0.34,1.56,0.64,1)',
                        filter: isHovered ? `drop-shadow(0 0 8px ${color})` : undefined,
                      }}
                    />

                    {/* Abbr text */}
                    <text
                      x={node.x}
                      y={node.y + 0.5}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill={color}
                      fontSize={isHovered ? 15.5 : 15}
                      fontWeight={800}
                      letterSpacing="0.02em"
                      style={{
                        userSelect: 'none',
                        transform: isHovered ? `scale(1.2)` : 'scale(1)',
                        transformOrigin: `${node.x}px ${node.y}px`,
                        transition: 'transform 0.2s cubic-bezier(0.34,1.56,0.64,1), font-size 0.2s ease',
                      }}
                    >
                      {abbr}
                    </text>

                    {/* Label below node */}
                    <text
                      x={node.x}
                      y={node.y + r + 12}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill={isHovered ? 'rgba(255,255,255,0.9)' : 'rgba(255,255,255,0.4)'}
                      fontSize={6.5}
                      fontWeight={500}
                      style={{
                        userSelect: 'none',
                        transition: 'fill 0.2s ease',
                      }}
                    >
                      {node.integration.name}
                    </text>

                    {/* Invisible larger hit area */}
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={r + 14}
                      fill="transparent"
                    />
                  </motion.g>
                );
              })}

              {/* ── Particle layer ── */}
              <g aria-hidden="true">
                {particles.map((p, i) => (
                  <circle
                    key={p.id}
                    ref={(el) => { particleRefs.current[i] = el; }}
                    cx={p.cx}
                    cy={p.cy}
                    r={3}
                    fill={p.color}
                    filter="url(#explosion-glow)"
                  />
                ))}
              </g>
            </svg>
          </div>

          {/* ── Bottom note ── */}
          <motion.p
            style={{
              textAlign: 'center',
              color: 'rgba(255,255,255,0.30)',
              fontSize: 14,
              marginTop: 32,
            }}
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            + 176 more integrations
          </motion.p>

        </div>

        {/* ── Floating tooltip ── */}
        {tooltip && !clickedNode && (
          <div
            style={{
              position: 'fixed',
              left: tooltip.x,
              top: tooltip.y - 52,
              transform: 'translateX(-50%)',
              background: 'rgba(15,20,25,0.95)',
              border: `1px solid ${tooltip.color}55`,
              borderRadius: 8,
              padding: '6px 12px',
              pointerEvents: 'none',
              zIndex: 9999,
              backdropFilter: 'blur(8px)',
              WebkitBackdropFilter: 'blur(8px)',
              boxShadow: `0 0 16px ${tooltip.color}22`,
              whiteSpace: 'nowrap',
            }}
          >
            <p
              style={{
                margin: 0,
                color: '#fff',
                fontSize: 13,
                fontWeight: 700,
              }}
            >
              {tooltip.name}
            </p>
            <p
              style={{
                margin: 0,
                color: tooltip.color,
                fontSize: 11,
                fontWeight: 500,
              }}
            >
              {tooltip.category}
            </p>
          </div>
        )}

        {/* ── Integration info overlay ── */}
        <AnimatePresence mode="wait">
          {clickedNode && (
            <motion.div
              key={`overlay-${clickedNode.integration.name}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={handleCloseOverlay}
              onKeyDown={handleKeyDown}
              role="dialog"
              aria-modal="true"
              aria-label={`${clickedNode.integration.name} integration details`}
              tabIndex={-1}
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(15,20,25,0.88)',
                backdropFilter: 'blur(12px)',
                WebkitBackdropFilter: 'blur(12px)',
                zIndex: 9998,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '24px',
              }}
            >
              <motion.div
                key={`card-${clickedNode.integration.name}`}
                initial={{ opacity: 0, scale: 0.85, y: 24 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 12 }}
                transition={{ type: 'spring', stiffness: 280, damping: 22 }}
                onClick={(e) => e.stopPropagation()}
                style={{
                  position: 'relative',
                  background: 'rgba(255,255,255,0.04)',
                  border: `1.5px solid ${clickedNode.integration.color}55`,
                  boxShadow: `0 0 80px ${clickedNode.integration.color}18`,
                  borderRadius: 24,
                  padding: '48px 56px',
                  maxWidth: 480,
                  width: '100%',
                }}
              >
                {/* Close button */}
                <button
                  type="button"
                  onClick={handleCloseOverlay}
                  aria-label="Close integration details"
                  style={{
                    position: 'absolute',
                    top: 16,
                    right: 16,
                    width: 36,
                    height: 36,
                    borderRadius: '50%',
                    background: 'transparent',
                    border: '1px solid rgba(255,255,255,0.12)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'rgba(255,255,255,0.6)',
                    fontSize: 18,
                    lineHeight: 1,
                    transition: 'background 0.15s ease, color 0.15s ease',
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.08)';
                    (e.currentTarget as HTMLButtonElement).style.color = '#fff';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                    (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.6)';
                  }}
                >
                  &#x2715;
                </button>

                {/* Top: orb + abbr */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
                  <div
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      background: clickedNode.integration.color,
                      boxShadow: `0 0 20px ${clickedNode.integration.color}88`,
                      flexShrink: 0,
                    }}
                  />
                  <span
                    style={{
                      fontSize: 24,
                      fontWeight: 700,
                      color: '#fff',
                      letterSpacing: '0.04em',
                    }}
                  >
                    {clickedNode.integration.abbr}
                  </span>
                </div>

                {/* Integration name */}
                <h3
                  style={{
                    fontSize: 'clamp(2rem, 4vw, 3rem)',
                    fontWeight: 800,
                    color: '#fff',
                    letterSpacing: '-0.03em',
                    margin: '0 0 12px 0',
                    lineHeight: 1.05,
                  }}
                >
                  {clickedNode.integration.name}
                </h3>

                {/* Category badge */}
                <span
                  style={{
                    display: 'inline-block',
                    background: `${clickedNode.integration.color}18`,
                    border: `1px solid ${clickedNode.integration.color}44`,
                    color: clickedNode.integration.color,
                    borderRadius: 99,
                    fontSize: 12,
                    fontWeight: 600,
                    padding: '3px 12px',
                    marginBottom: 20,
                    letterSpacing: '0.02em',
                  }}
                >
                  {clickedNode.integration.category}
                </span>

                {/* Divider */}
                <div
                  style={{
                    height: 1,
                    background: `linear-gradient(90deg, transparent, ${clickedNode.integration.color}40, transparent)`,
                    margin: '0 0 20px 0',
                  }}
                />

                {/* Description */}
                <p
                  style={{
                    color: 'rgba(255,255,255,0.7)',
                    fontSize: 16,
                    lineHeight: 1.6,
                    margin: '0 0 28px 0',
                  }}
                >
                  {DESCRIPTIONS[clickedNode.integration.name] ?? 'Native integration with Vantro AI agents.'}
                </p>

                {/* Connected via Vantro tag */}
                <p
                  style={{
                    color: 'rgba(255,255,255,0.28)',
                    fontSize: 12,
                    margin: 0,
                    letterSpacing: '0.04em',
                    fontWeight: 500,
                  }}
                >
                  Connected via Vantro
                </p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    </>
  );
}
