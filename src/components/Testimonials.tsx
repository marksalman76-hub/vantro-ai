'use client';

import { useRef } from 'react';

const QUOTES = [
  {
    text: 'Vantro replaced three separate tools and a backlog of busywork. Our ops team finally builds instead of firefighting.',
    name: 'Maya Renner',
    title: 'COO',
    company: 'Northwind Labs',
  },
  {
    text: 'We deployed Nova and Echo in an afternoon. Pipeline coverage went up and response times dropped overnight.',
    name: 'Daniel Okafor',
    title: 'VP Revenue',
    company: 'Cleardesk',
  },
  {
    text: 'The shared-memory model is the real unlock. Handoffs between agents are seamless in a way our humans envy.',
    name: 'Sofia Marchetti',
    title: 'Head of Product',
    company: 'Lumen Systems',
  },
  {
    text: 'Forge ships small fixes while my engineers focus on the hard problems. It is like adding a tireless junior dev.',
    name: 'Aaron Patel',
    title: 'CTO',
    company: 'Stacksmith',
  },
  {
    text: 'Compliance was our blocker for AI. Sentinel\'s audit trail and approval gates got us a green light from legal.',
    name: 'Greta Lindqvist',
    title: 'GC',
    company: 'Halden Group',
  },
  {
    text: 'It feels less like software and more like hiring a whole department that onboards in minutes.',
    name: 'Marcus Webb',
    title: 'Founder',
    company: 'Tidalflow',
  },
];

interface QuoteCardProps {
  quote: typeof QUOTES[0];
  idx: number;
}

function QuoteCard({ quote, idx }: QuoteCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const el = cardRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    el.style.setProperty('--mx', `${e.clientX - rect.left}px`);
    el.style.setProperty('--my', `${e.clientY - rect.top}px`);
  }

  return (
    <div
      ref={cardRef}
      className="glass-card rounded-2xl p-8 flex-shrink-0 flex flex-col gap-4"
      style={{ width: '380px', maxWidth: '380px' }}
      onMouseMove={handleMouseMove}
    >
      <div className="spotlight" />
      <div className="sheen" />
      <p
        className="text-base leading-relaxed font-medium"
        style={{ color: 'rgba(246,246,246,0.90)' }}
      >
        <span
          aria-hidden="true"
          className="text-4xl leading-none mr-1 select-none"
          style={{ color: 'oklch(0.55 0 0)', fontFamily: 'Georgia, serif', verticalAlign: '-0.2em' }}
        >
          &ldquo;
        </span>
        {quote.text}
      </p>
      <div className="mt-auto">
        <p className="text-snow font-semibold text-sm" style={{ color: 'oklch(0.97 0 0)' }}>
          {quote.name}
        </p>
        <p className="text-sm" style={{ color: 'oklch(0.70 0 0)' }}>
          {quote.title}, {quote.company}
        </p>
      </div>
    </div>
  );
}

export function Testimonials() {
  return (
    <section className="py-32 overflow-hidden" style={{ backgroundColor: 'oklch(0.33 0 0)' }}>
      <h2
        className="text-center mb-16 font-bold text-4xl md:text-5xl"
        style={{ fontFamily: 'Space Grotesk, sans-serif', color: 'oklch(0.97 0 0)' }}
      >
        Operators are moving faster.
      </h2>

      <div
        className="marquee-row overflow-hidden"
        style={{ cursor: 'default' }}
        onMouseEnter={(e) => {
          const track = e.currentTarget.querySelector('.marquee-track') as HTMLElement;
          if (track) track.style.animationPlayState = 'paused';
        }}
        onMouseLeave={(e) => {
          const track = e.currentTarget.querySelector('.marquee-track') as HTMLElement;
          if (track) track.style.animationPlayState = 'running';
        }}
      >
        <div
          className="marquee-track flex gap-6"
          style={{ animation: 'marquee 50s linear infinite', width: 'max-content' }}
        >
          {[...QUOTES, ...QUOTES].map((quote, i) => (
            <QuoteCard key={i} quote={quote} idx={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
