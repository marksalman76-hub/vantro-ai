'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, useReducedMotion, useAnimation, type PanInfo } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const AGENTS = [
  { name: 'Atlas', role: 'Operations Orchestrator', category: 'Operations', blurb: 'Coordinates every agent and routes work end to end.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-01-atlas-HcT8hzhWCVimMA7hv773NB.webp' },
  { name: 'Echo', role: 'Customer Support', category: 'Support', blurb: 'Resolves tickets across chat, email and voice 24/7.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-02-echo-jBseNuruo6zVaNEwKn4uiC.webp' },
  { name: 'Ledger', role: 'Finance & Accounting', category: 'Finance', blurb: 'Reconciles books, tracks spend and flags anomalies.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-03-ledger-F85UZALSwUyRYrbFukUT32.webp' },
  { name: 'Quill', role: 'Content Writer', category: 'Content', blurb: 'Drafts long-form, on-brand copy at scale.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-04-quill-bj87Aczd4DkvzVpDymRCXC.webp' },
  { name: 'Pixel', role: 'Design & Creative', category: 'Creative', blurb: 'Generates layouts, assets and creative variations.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-05-pixel-5wPhecN9KKS2GP83txqg3L.webp' },
  { name: 'Forge', role: 'Code & Engineering', category: 'Engineering', blurb: 'Ships features, reviews PRs and squashes bugs.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-06-forge-74Qoi5iZ6HSHfAKCtpmGiV.webp' },
  { name: 'Sentinel', role: 'Security & Compliance', category: 'Security', blurb: 'Monitors threats and enforces policy in real time.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-07-sentinel-R2z9W7XcosMCmKrgyy5egK.webp' },
  { name: 'Pulse', role: 'Marketing Strategist', category: 'Marketing', blurb: 'Plans campaigns and optimizes spend across channels.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-08-pulse-HnoLtavTCfRkHgHn4oRHWY.webp' },
  { name: 'Harbor', role: 'Recruiting & HR', category: 'People', blurb: 'Sources, screens and schedules top candidates.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-09-harbor-JSYpGWNWqMBKuGkeADyUGQ.webp' },
  { name: 'Vector', role: 'Data Analyst', category: 'Data', blurb: 'Turns raw data into dashboards and decisions.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-10-vector-h5yum6XcwDvxJveuEcaaRr.webp' },
  { name: 'Scout', role: 'Research Agent', category: 'Research', blurb: 'Gathers market intel and synthesizes findings.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-11-scout-RA2fVyF7bjnc6jF6huf2u7.webp' },
  { name: 'Relay', role: 'Email & Comms', category: 'Comms', blurb: 'Manages inbox triage and outbound sequences.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-12-relay-hw2y7EPjNeEPfnsw4Gbb8v.webp' },
  { name: 'Nova', role: 'Sales Closer', category: 'Sales', blurb: 'Qualifies leads and drives deals to signature.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-13-nova-RjP6GCP9dydGjYzxoGqUS4.webp' },
  { name: 'Cipher', role: 'Legal Reviewer', category: 'Legal', blurb: 'Reviews contracts and surfaces risky clauses.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-14-cipher-6bpayqEPE2evcWh4kx4ewj.webp' },
  { name: 'Tempo', role: 'Project Manager', category: 'Operations', blurb: 'Keeps timelines, owners and deliverables on track.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-15-tempo-SH2nCJiGUVjw6yNbfvyR5r.webp' },
  { name: 'Mosaic', role: 'Social Media Manager', category: 'Marketing', blurb: 'Schedules posts and engages across platforms.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-16-mosaic-BLWJNJuQDBV5a4YBrz4p5X.webp' },
  { name: 'Lumen', role: 'Brand Strategist', category: 'Marketing', blurb: 'Shapes positioning, voice and identity systems.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-17-lumen-2qvMVEXiCmKsKCbwvMDhsa.webp' },
  { name: 'Drift', role: 'Logistics & Supply', category: 'Operations', blurb: 'Optimizes routing, inventory and fulfillment.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-18-drift-53Ynh9MkY87HuXeNL6Rtqc.webp' },
  { name: 'Sage', role: 'Knowledge Base', category: 'Support', blurb: 'Builds and maintains your living documentation.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-19-sage-8wXDmjtcYDgZwwVf5p8Tyn.webp' },
  { name: 'Bolt', role: 'Automation Engineer', category: 'Engineering', blurb: 'Wires up workflows and integrates your stack.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-20-bolt-62QDSf9Xu4fefkZnymAYSB.webp' },
  { name: 'Aria', role: 'Voice & Telephony', category: 'Support', blurb: 'Handles inbound and outbound calls naturally.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-21-aria-GdEzW9bgD4tMZaCrMfUAUK.webp' },
  { name: 'Onyx', role: 'Executive Assistant', category: 'Operations', blurb: 'Manages calendars, briefings and follow-ups.', image: 'https://d2xsxph8kpxj0f.cloudfront.net/310519663790183318/36rayGFrg23ycanR2oWmiQ/face-22-onyx-YJEsc2eKjrVan3gzHX8awN.webp' },
];

const CARD_W = 210;
const SLOT_W = 238;
const VISIBLE_RADIUS = 3;

function mod(n: number, m: number) {
  return ((n % m) + m) % m;
}

function getOffset(i: number, active: number, count: number) {
  const raw = mod(i - active, count);
  return raw > Math.floor(count / 2) ? raw - count : raw;
}

interface AgentCardInnerProps {
  agent: typeof AGENTS[0];
  isCenter: boolean;
  displayedName?: string;
}

function AgentCardInner({ agent, isCenter, displayedName }: AgentCardInnerProps) {
  const prefersReduced = useReducedMotion()
  const borderControls = useAnimation()

  useEffect(() => {
    if (!isCenter || prefersReduced) return

    const startSpin = () => borderControls.start({
      rotate: 360,
      transition: { duration: 3, repeat: Infinity, ease: 'linear' },
    })

    const handleVisibility = () => {
      if (document.visibilityState === 'hidden') borderControls.stop()
      else startSpin()
    }

    startSpin()
    document.addEventListener('visibilitychange', handleVisibility)
    return () => {
      borderControls.stop()
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [isCenter, prefersReduced, borderControls])

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      {/* Rotating gradient border — sits outside overflow:hidden */}
      {isCenter && !prefersReduced && (
        <motion.div
          animate={borderControls}
          style={{
            position: 'absolute',
            inset: -1.5,
            borderRadius: '1.4rem',
            background: 'conic-gradient(from 0deg at 50% 50%, transparent 0deg, rgba(255,255,255,0.85) 40deg, rgba(255,255,255,0.0) 80deg)',
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            maskComposite: 'exclude',
            padding: '1.5px',
            pointerEvents: 'none',
            zIndex: 7,
          }}
        />
      )}

      <div
        style={{
          width: '100%',
          borderRadius: '1.25rem',
          overflow: 'hidden',
          background: isCenter
            ? 'linear-gradient(145deg, rgba(255,255,255,0.13) 0%, rgba(255,255,255,0.04) 100%)'
            : 'linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.025) 100%)',
          border: isCenter
            ? '1.5px solid rgba(255,255,255,0.50)'
            : '1px solid rgba(255,255,255,0.25)',
          boxShadow: isCenter
            ? 'inset 0 2.5px 0 rgba(255,255,255,0.65), inset 0 -1px 0 rgba(255,255,255,0.08), 0 0 0 1px rgba(255,255,255,0.12), 0 0 60px rgba(255,255,255,0.08), 0 32px 80px rgba(0,0,0,0.65)'
            : 'inset 0 2px 0 rgba(255,255,255,0.32), inset 0 -1px 0 rgba(255,255,255,0.04), 0 8px 32px rgba(0,0,0,0.45)',
          position: 'relative',
          transition: 'box-shadow 0.4s ease, border-color 0.4s ease',
        }}
      >
        {isCenter && (
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background: 'radial-gradient(ellipse 110% 55% at 50% 108%, rgba(255,255,255,0.18) 0%, transparent 60%)',
              mixBlendMode: 'screen',
              pointerEvents: 'none',
              zIndex: 3,
              borderRadius: 'inherit',
            }}
          />
        )}
        {isCenter && (
          <div
            style={{
              position: 'absolute',
              top: 0, left: 0,
              width: '50%', height: '100%',
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.14), transparent)',
              zIndex: 4,
              pointerEvents: 'none',
              animation: 'metal-sheen 2.2s ease-out 0.3s forwards',
            }}
          />
        )}

        {/* Agent face — animated when center */}
        {isCenter && !prefersReduced ? (
          <motion.img
            src={agent.image}
            alt={`${agent.name} - ${agent.role}`}
            animate={{
              scale: [1, 1.028, 1.012, 1.035, 1.008, 1],
              y: [0, -5, -2, -6, -1, 0],
              x: [0, 2, -1.5, 2.5, -0.8, 0],
              filter: [
                'brightness(1.0) saturate(1.0) contrast(1.0)',
                'brightness(1.22) saturate(1.30) contrast(1.06)',
                'brightness(1.08) saturate(1.10) contrast(1.02)',
                'brightness(1.18) saturate(1.25) contrast(1.05)',
                'brightness(1.04) saturate(1.06) contrast(1.01)',
                'brightness(1.0) saturate(1.0) contrast(1.0)',
              ],
            }}
            transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', repeatDelay: 0.5 }}
            style={{ width: '100%', aspectRatio: '3/4', objectFit: 'cover', display: 'block' }}
          />
        ) : (
          <img
            src={agent.image}
            alt={`${agent.name} - ${agent.role}`}
            style={{ width: '100%', aspectRatio: '3/4', objectFit: 'cover', display: 'block' }}
            loading="lazy"
          />
        )}
      <div style={{ padding: '0.9rem 1rem 1.1rem' }}>
        <p
          style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '0.66rem',
            letterSpacing: '0.16em',
            color: 'rgba(255,255,255,0.40)',
            textTransform: 'uppercase',
            marginBottom: '0.2rem',
          }}
        >
          {agent.category}
        </p>
        <p
          style={{
            fontFamily: 'Space Grotesk, sans-serif',
            fontWeight: 600,
            fontSize: '1rem',
            color: isCenter ? 'oklch(0.97 0 0)' : 'oklch(0.80 0 0)',
            marginBottom: '0.1rem',
          }}
        >
          {isCenter && displayedName !== undefined ? displayedName : agent.name}
        </p>
        <p style={{ fontSize: '0.76rem', color: 'rgba(255,255,255,0.40)', lineHeight: 1.4 }}>
          {agent.role}
        </p>
        {isCenter && (
          <p
            style={{
              fontSize: '0.72rem',
              color: 'rgba(255,255,255,0.30)',
              marginTop: '0.45rem',
              lineHeight: 1.55,
            }}
          >
            {agent.blurb}
          </p>
        )}
      </div>
      </div>

      {isCenter && (
        <motion.span
          aria-label="Agent online"
          aria-hidden="true"
          style={{
            position: 'absolute',
            top: '0.625rem',
            right: '0.625rem',
            width: '7px',
            height: '7px',
            borderRadius: '50%',
            background: 'oklch(0.75 0.22 145)',
            zIndex: 10,
            boxShadow: '0 0 0 0 oklch(0.75 0.22 145 / 0.70)',
          }}
          animate={prefersReduced ? {} : {
            boxShadow: [
              '0 0 0 0 oklch(0.75 0.22 145 / 0.70)',
              '0 0 0 5px oklch(0.75 0.22 145 / 0)',
              '0 0 0 0 oklch(0.75 0.22 145 / 0)',
            ],
          }}
          transition={{ duration: 1.4, repeat: Infinity, ease: 'easeOut' }}
        />
      )}
    </div>
  );
}

function AgentCarousel() {
  const [active, setActive] = useState(0);
  const prefersReduced = useReducedMotion();
  const count = AGENTS.length;
  const [displayedName, setDisplayedName] = useState(AGENTS[0].name);
  const typingRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const targetName = AGENTS[active].name;

    if (typingRef.current) clearTimeout(typingRef.current);

    if (prefersReduced) {
      setDisplayedName(targetName);
      return;
    }

    let charIndex = 0;
    setDisplayedName('');

    function typeNext() {
      charIndex++;
      setDisplayedName(targetName.slice(0, charIndex));
      if (charIndex < targetName.length) {
        typingRef.current = setTimeout(typeNext, 38);
      } else {
        // Cursor blink: show '|' then remove after 400ms
        setDisplayedName(targetName + '|');
        typingRef.current = setTimeout(() => {
          setDisplayedName(targetName);
        }, 400);
      }
    }

    typingRef.current = setTimeout(typeNext, 38);

    return () => {
      if (typingRef.current) clearTimeout(typingRef.current);
    };
  }, [active, prefersReduced]);

  function next() { setActive((i) => mod(i + 1, count)); }
  function prev() { setActive((i) => mod(i - 1, count)); }

  function handlePanEnd(_: unknown, info: PanInfo) {
    if (info.offset.x < -55 || info.velocity.x < -220) next();
    else if (info.offset.x > 55 || info.velocity.x > 220) prev();
  }

  return (
    <div>
      <div
        className="agent-carousel-stage"
        style={{ position: 'relative', height: '460px', overflow: 'hidden' }}
      >
        <motion.div
          onPanEnd={handlePanEnd}
          style={{
            position: 'absolute',
            inset: 0,
            zIndex: 50,
            cursor: 'grab',
            touchAction: 'none',
          }}
          whileTap={{ cursor: 'grabbing' } as any}
        />

        <div
          style={{
            position: 'absolute', left: 0, top: 0, bottom: 0, width: '18%',
            background: 'linear-gradient(to right, oklch(0.27 0 0) 30%, transparent)',
            zIndex: 45, pointerEvents: 'none',
          }}
        />
        <div
          style={{
            position: 'absolute', right: 0, top: 0, bottom: 0, width: '18%',
            background: 'linear-gradient(to left, oklch(0.27 0 0) 30%, transparent)',
            zIndex: 45, pointerEvents: 'none',
          }}
        />

        {AGENTS.map((agent, i) => {
          const offset = getOffset(i, active, count);
          const absOff = Math.abs(offset);
          const isVisible = absOff <= VISIBLE_RADIUS;
          const isCenter = offset === 0;

          const animateValues = prefersReduced
            ? { x: offset * SLOT_W, scale: isCenter ? 1 : 0.88, opacity: isVisible ? 1 : 0 }
            : {
                x: offset * SLOT_W,
                rotateY: offset * -30,
                z: isCenter ? 100 : -absOff * 45,
                scale: isCenter ? 1.04 : Math.max(0.55, 1 - absOff * 0.09),
                opacity: isVisible ? Math.max(0, 1 - absOff * 0.20) : 0,
              };

          return (
            <motion.div
              key={agent.name}
              animate={animateValues}
              transition={{ type: 'spring', stiffness: 295, damping: 33, mass: 0.85 }}
              style={{
                position: 'absolute',
                top: '8px',
                left: '50%',
                marginLeft: `-${CARD_W / 2}px`,
                width: `${CARD_W}px`,
                zIndex: isVisible ? VISIBLE_RADIUS + 2 - absOff : 0,
                pointerEvents: isVisible && !isCenter ? 'auto' : 'none',
                cursor: isVisible && !isCenter ? 'pointer' : 'default',
                willChange: 'transform',
              }}
              onClick={() => { if (!isCenter && isVisible) setActive(i); }}
            >
              <AgentCardInner agent={agent} isCenter={isCenter} displayedName={isCenter ? displayedName : undefined} />
            </motion.div>
          );
        })}
      </div>

      {/* Position indicator */}
      <p
        style={{
          textAlign: 'center',
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '0.68rem',
          letterSpacing: '0.14em',
          color: 'oklch(0.38 0 0)',
          marginTop: '1.25rem',
          userSelect: 'none',
        }}
        aria-label={`Agent ${active + 1} of ${count}`}
      >
        {String(active + 1).padStart(2, '0')} / {String(count).padStart(2, '0')}
      </p>

      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '1.5rem',
          marginTop: '2.5rem',
        }}
      >
        <button
          onClick={prev}
          aria-label="Previous agent"
          style={{
            background: 'rgba(255,255,255,0.055)',
            border: '1px solid rgba(255,255,255,0.11)',
            borderRadius: '50%',
            width: '44px',
            height: '44px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'oklch(0.97 0 0)',
            cursor: 'pointer',
            transition: 'background 0.2s, border-color 0.2s',
            boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.10)',
            flexShrink: 0,
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.11)';
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.22)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.055)';
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.11)';
          }}
        >
          <ChevronLeft size={18} strokeWidth={1.5} />
        </button>

        <div style={{ textAlign: 'center', minWidth: '130px' }}>
          <motion.p
            key={AGENTS[active].name}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22 }}
            style={{
              fontFamily: 'Space Grotesk, sans-serif',
              fontWeight: 600,
              fontSize: '0.9rem',
              color: 'oklch(0.97 0 0)',
              marginBottom: '0.15rem',
            }}
          >
            {AGENTS[active].name}
          </motion.p>
          <p
            style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.62rem',
              letterSpacing: '0.12em',
              color: 'rgba(255,255,255,0.28)',
              textTransform: 'uppercase',
            }}
          >
            {active + 1} / {count}
          </p>
        </div>

        <button
          onClick={next}
          aria-label="Next agent"
          style={{
            background: 'rgba(255,255,255,0.055)',
            border: '1px solid rgba(255,255,255,0.11)',
            borderRadius: '50%',
            width: '44px',
            height: '44px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'oklch(0.97 0 0)',
            cursor: 'pointer',
            transition: 'background 0.2s, border-color 0.2s',
            boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.10)',
            flexShrink: 0,
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.11)';
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.22)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.055)';
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.11)';
          }}
        >
          <ChevronRight size={18} strokeWidth={1.5} />
        </button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '5px', marginTop: '1.1rem' }}>
        {Array.from({ length: 7 }, (_, j) => {
          const dotIdx = mod(active - 3 + j, count);
          const isActiveDot = dotIdx === active;
          return (
            <button
              key={j}
              onClick={() => setActive(dotIdx)}
              aria-label={`Agent ${dotIdx + 1}`}
              style={{
                width: isActiveDot ? '22px' : '6px',
                height: '6px',
                borderRadius: '3px',
                background: isActiveDot ? 'oklch(0.97 0 0)' : 'rgba(255,255,255,0.20)',
                border: 'none',
                cursor: 'pointer',
                padding: 0,
                transition: 'width 0.3s ease, background 0.3s ease',
                flexShrink: 0,
              }}
            />
          );
        })}
      </div>
    </div>
  );
}

export function AgentRoster() {
  return (
    <section
      id="agents"
      className="py-32 overflow-hidden"
      style={{ backgroundColor: 'oklch(0.27 0 0)', position: 'relative' }}
    >
      <h2
        className="text-center mb-4 font-bold text-4xl md:text-5xl"
        style={{ fontFamily: 'Space Grotesk, sans-serif', color: 'oklch(0.97 0 0)' }}
      >
        Meet your 22 specialists.
      </h2>
      <p className="text-center mb-16 text-base" style={{ color: 'oklch(0.70 0 0)' }}>
        Every agent is purpose-built, always on, and wired to work together.
      </p>
      <AgentCarousel />
    </section>
  );
}
