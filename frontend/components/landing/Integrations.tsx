'use client';

import { useState, useRef, useCallback } from 'react';
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
  { name: 'Mailchimp',    abbr: 'MC', category: 'Sales',       color: '#FFD700' },
  { name: 'Zendesk',      abbr: 'ZD', category: 'Support',     color: '#00D9FF' },
  { name: 'Intercom',     abbr: 'IC', category: 'Support',     color: '#1F8DED' },
  { name: 'Freshdesk',    abbr: 'FD', category: 'Support',     color: '#35AC47' },
  { name: 'Twilio',       abbr: 'TW', category: 'Support',     color: '#F22F46' },
  { name: 'Stripe',       abbr: 'ST', category: 'Operations',  color: '#635BFF' },
  { name: 'QuickBooks',   abbr: 'QB', category: 'Operations',  color: '#2CA01C' },
  { name: 'Xero',         abbr: 'XE', category: 'Operations',  color: '#13B5EA' },
  { name: 'Asana',        abbr: 'AS', category: 'Operations',  color: '#F06A6A' },
  { name: 'Monday.com',   abbr: 'MO', category: 'Operations',  color: '#FF3D57' },
  { name: 'Zapier',       abbr: 'ZP', category: 'Operations',  color: '#FF6B35' },
  { name: 'Jira',         abbr: 'JI', category: 'Engineering', color: '#0052CC' },
  { name: 'GitHub',       abbr: 'GH', category: 'Engineering', color: '#B084FF' },
  { name: 'Slack',        abbr: 'SL', category: 'Engineering', color: '#E01E5A' },
  { name: 'Notion',       abbr: 'NO', category: 'Engineering', color: '#9CA3AF' },
  { name: 'Analytics',    abbr: 'GA', category: 'Engineering', color: '#E37400' },
  { name: 'Segment',      abbr: 'SG', category: 'Engineering', color: '#52BD95' },
  { name: 'Mixpanel',     abbr: 'MP', category: 'Engineering', color: '#7856FF' },
  { name: 'PostgreSQL',   abbr: 'PG', category: 'Engineering', color: '#336791' },
] as const;

type Category = 'All' | 'Sales' | 'Operations' | 'Engineering' | 'Support';
const CATEGORIES: Category[] = ['All', 'Sales', 'Operations', 'Engineering', 'Support'];

// ─── Integration Card ─────────────────────────────────────────────────────────

function IntegrationCard({
  name,
  abbr,
  color,
}: {
  name: string;
  abbr: string;
  color: string;
}) {
  const [hovered, setHovered] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.88 }}
      transition={{ duration: 0.28, ease: [0.23, 1, 0.32, 1] }}
      data-integration-card
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: '100%',
        aspectRatio: '1',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 10,
        padding: 16,
        background: 'rgba(255,255,255,0.04)',
        border: `1px solid ${hovered ? `${color}55` : 'rgba(255,255,255,0.08)'}`,
        borderRadius: 16,
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        cursor: 'default',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: hovered
          ? `0 0 24px ${color}18, inset 0 0 0 1px ${color}15`
          : 'none',
        transform: hovered ? 'scale(1.05) translateY(-2px)' : 'scale(1) translateY(0px)',
        transition: 'all 250ms cubic-bezier(0.23,1,0.32,1)',
      }}
    >
      {/* Abbr badge */}
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: 10,
          background: hovered ? `${color}30` : `${color}1A`,
          border: `1px solid ${color}33`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color,
          fontSize: 14,
          fontWeight: 800,
          letterSpacing: '-0.02em',
          transition: 'background 250ms cubic-bezier(0.23,1,0.32,1)',
        }}
      >
        {abbr}
      </div>

      {/* Name */}
      <span
        style={{
          fontSize: 11,
          color: 'rgba(255,255,255,0.45)',
          textAlign: 'center',
          lineHeight: 1.3,
        }}
      >
        {name}
      </span>
    </motion.div>
  );
}

// ─── Section ──────────────────────────────────────────────────────────────────

export default function Integrations() {
  const [activeCategory, setActiveCategory] = useState<Category>('All');

  // Mouse spotlight state
  const [spotlightPos, setSpotlightPos] = useState({ x: -999, y: -999 });
  const gridWrapperRef = useRef<HTMLDivElement>(null);

  const sectionRef = useRef<HTMLElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const gridContainerRef = useRef<HTMLDivElement>(null);

  const filtered =
    activeCategory === 'All'
      ? INTEGRATIONS
      : INTEGRATIONS.filter((i) => i.category === activeCategory);

  // Track cursor for spotlight over grid wrapper
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setSpotlightPos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setSpotlightPos({ x: -999, y: -999 });
  }, []);

  // GSAP ScrollTrigger
  useGSAP(
    () => {
      if (!sectionRef.current || !headerRef.current) return;

      // Header
      gsap.from(headerRef.current, {
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%',
          once: true,
        },
      });

      // Cards stagger
      const cards = gridContainerRef.current?.querySelectorAll<HTMLElement>('[data-integration-card]');
      if (cards && cards.length) {
        ScrollTrigger.batch(cards, {
          start: 'top 90%',
          onEnter: (batch) => {
            gsap.from(batch, {
              y: 20,
              opacity: 0,
              duration: 0.5,
              ease: 'power3.out',
              stagger: 0.04,
            });
          },
          once: true,
        });
      }
    },
    { scope: sectionRef, dependencies: [filtered.length] }
  );

  return (
    <section
      id="integrations"
      ref={sectionRef}
      style={{
        width: '100%',
        paddingTop: 120,
        paddingBottom: 120,
        paddingLeft: 24,
        paddingRight: 24,
        background: '#0F1419',
      }}
    >
      <div style={{ maxWidth: 1280, margin: '0 auto' }}>

        {/* Section header */}
        <div ref={headerRef} style={{ textAlign: 'center', marginBottom: 56 }}>
          <p
            style={{
              color: '#00D9FF',
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              marginBottom: 16,
            }}
          >
            CONNECTS WITH YOUR STACK
          </p>
          <h2
            style={{
              color: '#fff',
              fontSize: 'clamp(2rem, 3.5vw, 3.2rem)',
              fontWeight: 800,
              letterSpacing: '-0.025em',
              lineHeight: 1.1,
              margin: 0,
            }}
          >
            Works With Everything
          </h2>
          <p
            style={{
              color: 'rgba(255,255,255,0.45)',
              fontSize: 18,
              marginTop: 16,
              lineHeight: 1.5,
            }}
          >
            200+ integrations. One-click setup.
          </p>
        </div>

        {/* Category filter tabs */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            marginBottom: 40,
          }}
        >
          {CATEGORIES.map((cat) => {
            const isActive = activeCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                style={{
                  position: 'relative',
                  padding: '8px 20px',
                  borderRadius: 99,
                  fontSize: 14,
                  fontWeight: 500,
                  background: 'transparent',
                  border: isActive ? 'none' : '1px solid rgba(255,255,255,0.10)',
                  cursor: 'pointer',
                  outline: 'none',
                }}
              >
                {isActive && (
                  <motion.span
                    layoutId="integration-tab-pill"
                    style={{
                      position: 'absolute',
                      inset: 0,
                      borderRadius: 99,
                      background: '#FF6B35',
                    }}
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}
                <span
                  style={{
                    position: 'relative',
                    zIndex: 1,
                    color: isActive ? '#fff' : '#9CA3AF',
                  }}
                >
                  {cat}
                </span>
              </button>
            );
          })}
        </div>

        {/* Grid wrapper with cursor spotlight */}
        <div
          ref={gridWrapperRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          style={{ position: 'relative' }}
        >
          {/* Spotlight overlay */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              pointerEvents: 'none',
              zIndex: 2,
              background: `radial-gradient(circle 300px at ${spotlightPos.x}px ${spotlightPos.y}px, rgba(0,217,255,0.06) 0%, transparent 70%)`,
              borderRadius: 16,
              transition: 'background 0ms',
            }}
          />

          {/* Integration grid */}
          <div
            ref={gridContainerRef}
            style={{ position: 'relative', zIndex: 1 }}
            className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3"
          >
            <AnimatePresence mode="popLayout">
              {filtered.map((integration) => (
                <IntegrationCard
                  key={integration.name}
                  name={integration.name}
                  abbr={integration.abbr}
                  color={integration.color}
                />
              ))}
            </AnimatePresence>
          </div>
        </div>

        {/* Bottom note */}
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
    </section>
  );
}
