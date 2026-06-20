"use client";

/**
 * AgentsSection.tsx
 * Drop into: frontend/src/app/components/AgentsSection.tsx
 * Then import and replace <AgentsGrid /> in page.tsx with <AgentsSection />
 *
 * Requires existing stack:
 *   framer-motion, lucide-react
 * No new deps needed.
 */

import React, { useState, useRef } from "react";
import { motion, AnimatePresence, useInView } from "framer-motion";
import {
  Crown, GitBranch, Lightbulb, Handshake, Search, FlaskConical,
  Film, Megaphone, PenLine, LineChart, BadgeDollarSign, CalendarDays,
  Sparkles, HeartHandshake, ShieldCheck, BarChart3, Radar, Store,
  Palette, Workflow, PhoneCall, Users, Zap, ChevronRight, Bot,
  Star, Filter
} from "lucide-react";

// ─── 27-AGENT DATA ────────────────────────────────────────────────────────────

type AgentTier = "executive" | "growth" | "creative" | "revenue" | "operations";

interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  color: string;
  bgGradient: string;
  tier: AgentTier;
  icon: React.ElementType;
  stat: string;
  statLabel: string;
  skills: string[];
  avatar: React.FC<{ size?: number }>;
}

// ─── UNIQUE SVG AVATARS ───────────────────────────────────────────────────────
// Each avatar is a unique geometric/character face built from SVG primitives.
// They share a consistent style: dark background circle, geometric features,
// accent color matching the agent card color.

const makeAvatar = (accentColor: string, elements: (a: string) => string): React.FC<{ size?: number }> =>
  function Avatar({ size = 56 }: { size?: number }) {
    return (
      <svg width={size} height={size} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="28" cy="28" r="28" fill="#0F0F14" />
        <g dangerouslySetInnerHTML={{ __html: elements(accentColor) }} />
      </svg>
    );
  };

// We define each avatar inline as a React component for full type safety
const AvatarCEO: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Crown */}
    <path d="M16 36 L16 26 L22 32 L28 20 L34 32 L40 26 L40 36 Z" fill="#FFD700" opacity="0.9"/>
    <rect x="16" y="36" width="24" height="3" rx="1.5" fill="#FFD700" opacity="0.7"/>
    {/* Eyes */}
    <circle cx="22" cy="32" r="1.5" fill="#FFD700"/>
    <circle cx="34" cy="32" r="1.5" fill="#FFD700"/>
  </svg>
);

const AvatarOrchestrator: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Hub & spokes */}
    <circle cx="28" cy="28" r="5" fill="#7C6AF7" opacity="0.9"/>
    {[0,60,120,180,240,300].map((deg, i) => {
      const r = (deg * Math.PI) / 180;
      const x2 = 28 + Math.cos(r) * 14;
      const y2 = 28 + Math.sin(r) * 14;
      return <g key={i}>
        <line x1="28" y1="28" x2={x2} y2={y2} stroke="#7C6AF7" strokeWidth="1.5" opacity="0.5"/>
        <circle cx={x2} cy={y2} r="3" fill="#7C6AF7" opacity="0.8"/>
      </g>;
    })}
  </svg>
);

const AvatarStrategist: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Upward trend arrow */}
    <polyline points="14,38 22,28 30,33 42,18" stroke="#4ECDC4" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
    <polygon points="42,18 36,20 40,24" fill="#4ECDC4"/>
    {/* Grid dots */}
    {[18,28,38].map(x => [20,30,40].map(y => <circle key={`${x}${y}`} cx={x} cy={y} r="0.8" fill="#4ECDC4" opacity="0.3"/>))}
  </svg>
);

const AvatarGrowth: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Handshake / two converging paths */}
    <path d="M14 28 Q21 20 28 28 Q35 36 42 28" stroke="#10B981" strokeWidth="2" fill="none" strokeLinecap="round"/>
    <circle cx="14" cy="28" r="3.5" fill="#10B981" opacity="0.8"/>
    <circle cx="42" cy="28" r="3.5" fill="#10B981" opacity="0.8"/>
    <circle cx="28" cy="28" r="4" fill="#10B981"/>
    <path d="M14 28 Q21 36 28 28 Q35 20 42 28" stroke="#10B981" strokeWidth="1" fill="none" strokeLinecap="round" opacity="0.35"/>
  </svg>
);

const AvatarResearch: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Magnifier */}
    <circle cx="25" cy="24" r="9" stroke="#F59E0B" strokeWidth="2" fill="none"/>
    <line x1="31.5" y1="30.5" x2="40" y2="39" stroke="#F59E0B" strokeWidth="2.5" strokeLinecap="round"/>
    <circle cx="25" cy="24" r="4" fill="#F59E0B" opacity="0.2"/>
    <line x1="22" y1="24" x2="28" y2="24" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round" opacity="0.8"/>
    <line x1="25" y1="21" x2="25" y2="27" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round" opacity="0.8"/>
  </svg>
);

const AvatarProductDev: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Box with sparkle */}
    <rect x="16" y="20" width="24" height="20" rx="3" stroke="#A78BFA" strokeWidth="1.5" fill="none"/>
    <path d="M16 26 L40 26" stroke="#A78BFA" strokeWidth="1" opacity="0.5"/>
    <rect x="20" y="22" width="8" height="2" rx="1" fill="#A78BFA" opacity="0.6"/>
    {/* Sparkle top right */}
    <path d="M36 14 L37 17 L40 18 L37 19 L36 22 L35 19 L32 18 L35 17 Z" fill="#A78BFA"/>
  </svg>
);

const AvatarUGC: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Phone with record dot */}
    <rect x="20" y="14" width="16" height="28" rx="3" stroke="#FF6B6B" strokeWidth="1.5" fill="none"/>
    <circle cx="28" cy="39" r="1.5" fill="#FF6B6B" opacity="0.6"/>
    <circle cx="28" cy="28" r="5" fill="#FF6B6B" opacity="0.15"/>
    <circle cx="28" cy="28" r="3" fill="#FF6B6B"/>
    {/* Record pulse rings */}
    <circle cx="28" cy="28" r="7" stroke="#FF6B6B" strokeWidth="0.8" opacity="0.4"/>
    <circle cx="28" cy="28" r="10" stroke="#FF6B6B" strokeWidth="0.5" opacity="0.2"/>
  </svg>
);

const AvatarVideoAd: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Clapperboard */}
    <rect x="13" y="22" width="30" height="20" rx="2" fill="#EC4899" opacity="0.15"/>
    <rect x="13" y="22" width="30" height="20" rx="2" stroke="#EC4899" strokeWidth="1.5"/>
    <rect x="13" y="18" width="30" height="6" rx="2" fill="#EC4899" opacity="0.8"/>
    {/* Stripes on top */}
    {[17,22,27,32,37].map((x,i) => (
      <line key={i} x1={x} y1="18" x2={x-3} y2="24" stroke="#0F0F14" strokeWidth="1.8"/>
    ))}
    {/* Play triangle */}
    <polygon points="24,28 24,36 35,32" fill="#EC4899"/>
  </svg>
);

const AvatarCopywriter: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Pen writing lines */}
    <path d="M34 16 L38 20 L24 34 L18 36 L20 30 Z" fill="#4ECDC4" opacity="0.8"/>
    <path d="M34 16 L38 20" stroke="#4ECDC4" strokeWidth="1.5"/>
    <line x1="15" y1="40" x2="41" y2="40" stroke="#4ECDC4" strokeWidth="1" opacity="0.3"/>
    <line x1="15" y1="37" x2="25" y2="37" stroke="#4ECDC4" strokeWidth="1" opacity="0.3"/>
  </svg>
);

const AvatarSEO: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Globe with orbit ring */}
    <circle cx="28" cy="28" r="12" stroke="#3B82F6" strokeWidth="1.5" fill="none"/>
    <ellipse cx="28" cy="28" rx="6" ry="12" stroke="#3B82F6" strokeWidth="1" fill="none" opacity="0.5"/>
    <line x1="16" y1="28" x2="40" y2="28" stroke="#3B82F6" strokeWidth="1" opacity="0.5"/>
    <line x1="18" y1="22" x2="38" y2="22" stroke="#3B82F6" strokeWidth="0.8" opacity="0.3"/>
    <line x1="18" y1="34" x2="38" y2="34" stroke="#3B82F6" strokeWidth="0.8" opacity="0.3"/>
  </svg>
);

const AvatarPaidAds: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Dollar with upward arrow */}
    <circle cx="28" cy="28" r="11" stroke="#F59E0B" strokeWidth="1.5" fill="none"/>
    <text x="28" y="32" textAnchor="middle" fontSize="14" fontWeight="700" fill="#F59E0B">$</text>
    <path d="M34 18 L38 14 M38 14 L34 14 M38 14 L38 18" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);

const AvatarSocial: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Share nodes */}
    <circle cx="28" cy="20" r="4" fill="#EC4899"/>
    <circle cx="18" cy="34" r="4" fill="#EC4899" opacity="0.7"/>
    <circle cx="38" cy="34" r="4" fill="#EC4899" opacity="0.7"/>
    <line x1="28" y1="24" x2="19" y2="31" stroke="#EC4899" strokeWidth="1.2" opacity="0.6"/>
    <line x1="28" y1="24" x2="37" y2="31" stroke="#EC4899" strokeWidth="1.2" opacity="0.6"/>
    <line x1="22" y1="34" x2="34" y2="34" stroke="#EC4899" strokeWidth="1" opacity="0.4"/>
  </svg>
);

const AvatarContent: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Lightbulb / idea */}
    <path d="M28 16 C22 16 18 20 18 25 C18 29 21 32 22 35 L34 35 C35 32 38 29 38 25 C38 20 34 16 28 16Z" stroke="#A78BFA" strokeWidth="1.5" fill="#A78BFA" fillOpacity="0.12"/>
    <line x1="23" y1="37" x2="33" y2="37" stroke="#A78BFA" strokeWidth="1.5" strokeLinecap="round"/>
    <line x1="24" y1="39" x2="32" y2="39" stroke="#A78BFA" strokeWidth="1.5" strokeLinecap="round"/>
    <line x1="28" y1="20" x2="28" y2="29" stroke="#A78BFA" strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M25 27 L28 30 L31 27" stroke="#A78BFA" strokeWidth="1.2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const AvatarEmail: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Envelope */}
    <rect x="12" y="20" width="32" height="22" rx="3" stroke="#10B981" strokeWidth="1.5" fill="none"/>
    <path d="M12 22 L28 32 L44 22" stroke="#10B981" strokeWidth="1.5" fill="none"/>
    {/* Lightning bolt = automation */}
    <path d="M30 16 L26 23 L30 23 L26 30" stroke="#10B981" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const AvatarCRM: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Person + data rings */}
    <circle cx="28" cy="22" r="6" stroke="#7C6AF7" strokeWidth="1.5" fill="none"/>
    <path d="M16 40 C16 34 21 30 28 30 C35 30 40 34 40 40" stroke="#7C6AF7" strokeWidth="1.5" fill="none"/>
    <circle cx="28" cy="22" r="10" stroke="#7C6AF7" strokeWidth="0.7" strokeDasharray="2 2" opacity="0.4"/>
    <circle cx="28" cy="22" r="14" stroke="#7C6AF7" strokeWidth="0.5" strokeDasharray="2 3" opacity="0.2"/>
  </svg>
);

const AvatarLeadGen: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Funnel */}
    <path d="M12 16 L22 28 L22 40 L34 40 L34 28 L44 16 Z" stroke="#FF6B6B" strokeWidth="1.5" fill="#FF6B6B" fillOpacity="0.1"/>
    <line x1="14" y1="20" x2="42" y2="20" stroke="#FF6B6B" strokeWidth="1" opacity="0.5"/>
    <line x1="18" y1="24" x2="38" y2="24" stroke="#FF6B6B" strokeWidth="1" opacity="0.4"/>
    <circle cx="28" cy="36" r="3" fill="#FF6B6B"/>
  </svg>
);

const AvatarSetter: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Calendar with check */}
    <rect x="14" y="18" width="28" height="24" rx="3" stroke="#F59E0B" strokeWidth="1.5" fill="none"/>
    <line x1="14" y1="24" x2="42" y2="24" stroke="#F59E0B" strokeWidth="1.2"/>
    <line x1="20" y1="14" x2="20" y2="22" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round"/>
    <line x1="36" y1="14" x2="36" y2="22" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M21 32 L26 37 L35 28" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const AvatarSales: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Trophy */}
    <path d="M20 16 L36 16 L36 28 C36 34 32 38 28 38 C24 38 20 34 20 28 Z" stroke="#FFD700" strokeWidth="1.5" fill="#FFD700" fillOpacity="0.1"/>
    <path d="M14 18 L20 18 L20 26 C14 26 14 18 14 18 Z" stroke="#FFD700" strokeWidth="1" fill="none"/>
    <path d="M42 18 L36 18 L36 26 C42 26 42 18 42 18 Z" stroke="#FFD700" strokeWidth="1" fill="none"/>
    <line x1="22" y1="38" x2="34" y2="38" stroke="#FFD700" strokeWidth="1.5"/>
    <rect x="22" y="38" width="12" height="4" rx="1" fill="#FFD700" opacity="0.6"/>
  </svg>
);

const AvatarSupport: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Headset */}
    <path d="M16 28 C16 20 21 14 28 14 C35 14 40 20 40 28" stroke="#4ECDC4" strokeWidth="1.5" fill="none"/>
    <rect x="12" y="26" width="6" height="10" rx="3" fill="#4ECDC4" opacity="0.8"/>
    <rect x="38" y="26" width="6" height="10" rx="3" fill="#4ECDC4" opacity="0.8"/>
    <path d="M40 36 C40 38 36 42 28 42" stroke="#4ECDC4" strokeWidth="1.5" fill="none"/>
    <circle cx="28" cy="42" r="2" fill="#4ECDC4"/>
  </svg>
);

const AvatarReputation: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Shield with star */}
    <path d="M28 14 L40 19 L40 29 C40 35 35 40 28 43 C21 40 16 35 16 29 L16 19 Z" stroke="#10B981" strokeWidth="1.5" fill="#10B981" fillOpacity="0.1"/>
    <path d="M28 20 L29.5 24.5 L34 24.5 L30.5 27.5 L32 32 L28 29 L24 32 L25.5 27.5 L22 24.5 L26.5 24.5 Z" fill="#10B981"/>
  </svg>
);

const AvatarAnalytics: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Bar chart rising */}
    <rect x="14" y="32" width="6" height="10" rx="1" fill="#3B82F6" opacity="0.5"/>
    <rect x="22" y="26" width="6" height="16" rx="1" fill="#3B82F6" opacity="0.7"/>
    <rect x="30" y="20" width="6" height="22" rx="1" fill="#3B82F6" opacity="0.9"/>
    <rect x="38" y="14" width="6" height="28" rx="1" fill="#3B82F6"/>
    <line x1="12" y1="42" x2="46" y2="42" stroke="#3B82F6" strokeWidth="1" opacity="0.5"/>
  </svg>
);

const AvatarCompetitor: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Radar / sonar */}
    <circle cx="28" cy="28" r="12" stroke="#EC4899" strokeWidth="1" fill="none" opacity="0.5"/>
    <circle cx="28" cy="28" r="7" stroke="#EC4899" strokeWidth="1" fill="none" opacity="0.7"/>
    <circle cx="28" cy="28" r="3" fill="#EC4899"/>
    <path d="M28 28 L34 16" stroke="#EC4899" strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M28 28 L40 28" stroke="#EC4899" strokeWidth="0.8" opacity="0.4"/>
    <path d="M28 28 L28 16" stroke="#EC4899" strokeWidth="0.8" opacity="0.3"/>
    <circle cx="22" cy="20" r="2" fill="#EC4899" opacity="0.7"/>
    <circle cx="36" cy="22" r="1.5" fill="#EC4899" opacity="0.5"/>
  </svg>
);

const AvatarWebsite: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Browser frame */}
    <rect x="10" y="16" width="36" height="26" rx="3" stroke="#7C6AF7" strokeWidth="1.5" fill="none"/>
    <line x1="10" y1="22" x2="46" y2="22" stroke="#7C6AF7" strokeWidth="1"/>
    <circle cx="15" cy="19" r="1.2" fill="#7C6AF7" opacity="0.5"/>
    <circle cx="19" cy="19" r="1.2" fill="#7C6AF7" opacity="0.5"/>
    <circle cx="23" cy="19" r="1.2" fill="#7C6AF7" opacity="0.5"/>
    {/* Layout inside */}
    <rect x="14" y="26" width="10" height="12" rx="1.5" fill="#7C6AF7" opacity="0.2"/>
    <rect x="27" y="26" width="15" height="5" rx="1" fill="#7C6AF7" opacity="0.3"/>
    <rect x="27" y="33" width="15" height="5" rx="1" fill="#7C6AF7" opacity="0.2"/>
  </svg>
);

const AvatarBrand: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Diamond / gem */}
    <path d="M28 14 L40 24 L28 42 L16 24 Z" stroke="#FFD700" strokeWidth="1.5" fill="#FFD700" fillOpacity="0.1"/>
    <path d="M16 24 L28 28 L40 24" stroke="#FFD700" strokeWidth="1" fill="none" opacity="0.6"/>
    <path d="M28 14 L28 28" stroke="#FFD700" strokeWidth="0.8" opacity="0.4"/>
    <path d="M16 24 L40 24" stroke="#FFD700" strokeWidth="1" opacity="0.5"/>
  </svg>
);

const AvatarAutomation: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Gear */}
    <path d="M28 18 L30 14 L26 14 L28 18 Z M28 38 L26 42 L30 42 L28 38 Z M18 28 L14 26 L14 30 L18 28 Z M38 28 L42 30 L42 26 L38 28 Z M21 21 L18 18 L15 21 L18 24 Z M35 35 L38 38 L41 35 L38 32 Z M21 35 L18 32 L15 35 L18 38 Z M35 21 L38 24 L41 21 L38 18 Z" fill="#14B8A6" opacity="0.7"/>
    <circle cx="28" cy="28" r="7" stroke="#14B8A6" strokeWidth="1.5" fill="none"/>
    <circle cx="28" cy="28" r="3" fill="#14B8A6"/>
  </svg>
);

const AvatarReceptionist: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Mic / voice waveform */}
    <rect x="23" y="14" width="10" height="16" rx="5" stroke="#F59E0B" strokeWidth="1.5" fill="#F59E0B" fillOpacity="0.1"/>
    <path d="M18 30 C18 37 38 37 38 30" stroke="#F59E0B" strokeWidth="1.5" fill="none"/>
    <line x1="28" y1="37" x2="28" y2="42" stroke="#F59E0B" strokeWidth="1.5"/>
    <line x1="22" y1="42" x2="34" y2="42" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round"/>
    {/* Sound waves */}
    <path d="M14 26 Q16 28 14 30" stroke="#F59E0B" strokeWidth="1" fill="none" opacity="0.5"/>
    <path d="M42 26 Q40 28 42 30" stroke="#F59E0B" strokeWidth="1" fill="none" opacity="0.5"/>
  </svg>
);

const AvatarInfluencer: React.FC<{ size?: number }> = ({ size = 56 }) => (
  <svg width={size} height={size} viewBox="0 0 56 56" fill="none">
    <circle cx="28" cy="28" r="28" fill="#0F0F14"/>
    {/* Star burst / influencer */}
    {[0,45,90,135,180,225,270,315].map((deg, i) => {
      const r = (deg * Math.PI) / 180;
      const x1 = 28 + Math.cos(r) * 6;
      const y1 = 28 + Math.sin(r) * 6;
      const x2 = 28 + Math.cos(r) * 14;
      const y2 = 28 + Math.sin(r) * 14;
      return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#FF6B6B" strokeWidth={i % 2 === 0 ? "2" : "1"} strokeLinecap="round" opacity={i % 2 === 0 ? "0.9" : "0.4"}/>;
    })}
    <circle cx="28" cy="28" r="5" fill="#FF6B6B"/>
    <circle cx="28" cy="28" r="2" fill="#0F0F14"/>
  </svg>
);

// ─── FULL AGENT CATALOGUE ─────────────────────────────────────────────────────

const ALL_AGENTS: Agent[] = [
  {
    id: "ceo", name: "Rex", role: "Head Agent / CEO", tier: "executive",
    description: "Oversees all active agents, reviews reports, coordinates workflows and flags risks.",
    color: "#FFD700", bgGradient: "rgba(255,215,0,0.08)",
    icon: Crown, stat: "27 agents", statLabel: "coordinated",
    skills: ["Executive oversight", "Risk detection", "Board reporting"],
    avatar: AvatarCEO,
  },
  {
    id: "orchestrator", name: "Axon", role: "Orchestration Agent", tier: "executive",
    description: "Manages cross-agent task routing, execution sequencing and workflow coordination.",
    color: "#7C6AF7", bgGradient: "rgba(124,106,247,0.08)",
    icon: GitBranch, stat: "∞ tasks", statLabel: "in parallel",
    skills: ["Task routing", "Dependency mgmt", "Approval flows"],
    avatar: AvatarOrchestrator,
  },
  {
    id: "strategist", name: "Veda", role: "Strategist", tier: "growth",
    description: "Builds overall business, ecommerce, marketing, growth and positioning strategies.",
    color: "#4ECDC4", bgGradient: "rgba(78,205,196,0.08)",
    icon: Lightbulb, stat: "3× faster", statLabel: "go-to-market",
    skills: ["Market positioning", "Growth strategy", "Competitive analysis"],
    avatar: AvatarStrategist,
  },
  {
    id: "growth", name: "Koda", role: "Growth & Partnerships", tier: "growth",
    description: "Identifies partnerships, expansion opportunities, collaborations and revenue channels.",
    color: "#10B981", bgGradient: "rgba(16,185,129,0.08)",
    icon: Handshake, stat: "$2.1M+", statLabel: "deals sourced",
    skills: ["Partner outreach", "Revenue expansion", "Co-marketing"],
    avatar: AvatarGrowth,
  },
  {
    id: "research", name: "Scout", role: "Product Research", tier: "growth",
    description: "Finds trending products, market gaps, competitor weaknesses and opportunities.",
    color: "#F59E0B", bgGradient: "rgba(245,158,11,0.08)",
    icon: Search, stat: "500+", statLabel: "products analysed/mo",
    skills: ["Trend spotting", "Gap analysis", "Demand scoring"],
    avatar: AvatarResearch,
  },
  {
    id: "productdev", name: "Forge", role: "Product Development", tier: "growth",
    description: "Improves existing products and recommends new concepts and positioning.",
    color: "#A78BFA", bgGradient: "rgba(167,139,250,0.08)",
    icon: FlaskConical, stat: "62%", statLabel: "faster product cycles",
    skills: ["Concept design", "UX direction", "Positioning"],
    avatar: AvatarProductDev,
  },
  {
    id: "ugc", name: "Flux", role: "UGC Creative", tier: "creative",
    description: "Creates premium UGC concepts, creator briefs, hooks, scripts and content directions.",
    color: "#FF6B6B", bgGradient: "rgba(255,107,107,0.08)",
    icon: Film, stat: "8× more", statLabel: "UGC volume",
    skills: ["Hook writing", "Creator briefs", "Script direction"],
    avatar: AvatarUGC,
  },
  {
    id: "videoads", name: "Cine", role: "Video Ad Creative", tier: "creative",
    description: "Produces ad concepts, storyboard flows, visual directions and conversion creatives.",
    color: "#EC4899", bgGradient: "rgba(236,72,153,0.08)",
    icon: Film, stat: "4K output", statLabel: "in under 8 sec",
    skills: ["Storyboarding", "Ad structure", "Conversion hooks"],
    avatar: AvatarVideoAd,
  },
  {
    id: "copy", name: "Quill", role: "Copywriter", tier: "creative",
    description: "Writes high-converting product copy, landing pages, emails, headlines and CTAs.",
    color: "#4ECDC4", bgGradient: "rgba(78,205,196,0.08)",
    icon: PenLine, stat: "10k words", statLabel: "per minute",
    skills: ["Sales copy", "Landing pages", "Email sequences"],
    avatar: AvatarCopywriter,
  },
  {
    id: "seo", name: "Rank", role: "SEO Growth", tier: "creative",
    description: "Handles SEO strategy, keywords, metadata, blog direction and organic traffic.",
    color: "#3B82F6", bgGradient: "rgba(59,130,246,0.08)",
    icon: LineChart, stat: "Top 3", statLabel: "ranking avg.",
    skills: ["Keyword research", "On-page SEO", "Content clusters"],
    avatar: AvatarSEO,
  },
  {
    id: "paidads", name: "Blaze", role: "Paid Ads Strategist", tier: "revenue",
    description: "Creates Meta/TikTok/Google ad strategies, targeting logic and scaling plans.",
    color: "#F59E0B", bgGradient: "rgba(245,158,11,0.08)",
    icon: BadgeDollarSign, stat: "380% avg.", statLabel: "ROAS lift",
    skills: ["Meta ads", "TikTok ads", "Funnel architecture"],
    avatar: AvatarPaidAds,
  },
  {
    id: "social", name: "Lynx", role: "Social Media Manager", tier: "creative",
    description: "Plans social calendars, captions, engagement strategy and platform growth.",
    color: "#EC4899", bgGradient: "rgba(236,72,153,0.08)",
    icon: CalendarDays, stat: "12M+", statLabel: "impressions/mo",
    skills: ["Content calendar", "Caption writing", "Community growth"],
    avatar: AvatarSocial,
  },
  {
    id: "content", name: "Spark", role: "Content Creator", tier: "creative",
    description: "Generates social content ideas, scripts, post concepts and branded media direction.",
    color: "#A78BFA", bgGradient: "rgba(167,139,250,0.08)",
    icon: Sparkles, stat: "60 pieces", statLabel: "per week",
    skills: ["Short-form scripts", "Trend adaption", "Brand alignment"],
    avatar: AvatarContent,
  },
  {
    id: "email", name: "Flow", role: "Email Marketing", tier: "revenue",
    description: "Builds email flows, campaigns, abandoned cart sequences and retention flows.",
    color: "#10B981", bgGradient: "rgba(16,185,129,0.08)",
    icon: Megaphone, stat: "42% open", statLabel: "rate average",
    skills: ["Klaviyo flows", "Abandoned cart", "Win-back sequences"],
    avatar: AvatarEmail,
  },
  {
    id: "crm", name: "Nexo", role: "CRM AI", tier: "operations",
    description: "Manages CRM workflows, contact logic, tagging, lead states and lifecycle automation.",
    color: "#7C6AF7", bgGradient: "rgba(124,106,247,0.08)",
    icon: Users, stat: "100%", statLabel: "contact coverage",
    skills: ["Pipeline hygiene", "Lead scoring", "Lifecycle tagging"],
    avatar: AvatarCRM,
  },
  {
    id: "leadgen", name: "Lure", role: "Lead Generation", tier: "revenue",
    description: "Finds and qualifies leads, prospect opportunities and outreach targets.",
    color: "#FF6B6B", bgGradient: "rgba(255,107,107,0.08)",
    icon: Search, stat: "5k leads", statLabel: "per month",
    skills: ["Prospecting", "ICP matching", "Outreach angles"],
    avatar: AvatarLeadGen,
  },
  {
    id: "setter", name: "Hook", role: "Appointment Setter", tier: "revenue",
    description: "Handles outreach follow-ups, scheduling logic and booking flow sequences.",
    color: "#F59E0B", bgGradient: "rgba(245,158,11,0.08)",
    icon: CalendarDays, stat: "3× faster", statLabel: "booking rate",
    skills: ["Follow-up sequences", "Calendar sync", "Lead warm-up"],
    avatar: AvatarSetter,
  },
  {
    id: "sales", name: "Klose", role: "Sales / Closer", tier: "revenue",
    description: "Assists with objections, proposal follow-up, deal progression and conversion support.",
    color: "#FFD700", bgGradient: "rgba(255,215,0,0.08)",
    icon: BadgeDollarSign, stat: "$4.2M+", statLabel: "pipeline closed",
    skills: ["Objection handling", "Proposal follow-up", "Deal velocity"],
    avatar: AvatarSales,
  },
  {
    id: "support", name: "Cara", role: "Customer Support", tier: "operations",
    description: "Handles support replies, FAQ logic, escalation detection and CS workflows.",
    color: "#4ECDC4", bgGradient: "rgba(78,205,196,0.08)",
    icon: HeartHandshake, stat: "< 2 min", statLabel: "response time",
    skills: ["Ticket triage", "FAQ handling", "Escalation routing"],
    avatar: AvatarSupport,
  },
  {
    id: "reputation", name: "Vera", role: "Reputation Management", tier: "operations",
    description: "Monitors reviews, customer sentiment, trust signals and improvement opportunities.",
    color: "#10B981", bgGradient: "rgba(16,185,129,0.08)",
    icon: ShieldCheck, stat: "4.9★ avg.", statLabel: "rating maintained",
    skills: ["Review monitoring", "Sentiment analysis", "Trust building"],
    avatar: AvatarReputation,
  },
  {
    id: "analytics", name: "Pulse", role: "Analytics & Insights", tier: "operations",
    description: "Analyses store performance, campaign metrics, conversion trends and ROI opportunities.",
    color: "#3B82F6", bgGradient: "rgba(59,130,246,0.08)",
    icon: BarChart3, stat: "Real-time", statLabel: "dashboards",
    skills: ["Conversion analysis", "Cohort reporting", "ROI attribution"],
    avatar: AvatarAnalytics,
  },
  {
    id: "competitor", name: "Iris", role: "Competitor Intelligence", tier: "growth",
    description: "Tracks competitors, offers, pricing, messaging, creatives and strategic movements.",
    color: "#EC4899", bgGradient: "rgba(236,72,153,0.08)",
    icon: Radar, stat: "24/7", statLabel: "competitor watch",
    skills: ["Pricing alerts", "Ad spy", "Positioning gaps"],
    avatar: AvatarCompetitor,
  },
  {
    id: "website", name: "Grid", role: "Website / Store Builder", tier: "operations",
    description: "Designs ecommerce pages, landing pages, store structures and UX flows.",
    color: "#7C6AF7", bgGradient: "rgba(124,106,247,0.08)",
    icon: Store, stat: "87% avg.", statLabel: "CVR improvement",
    skills: ["Landing pages", "UX flow", "Store architecture"],
    avatar: AvatarWebsite,
  },
  {
    id: "brand", name: "Aura", role: "Brand Identity", tier: "creative",
    description: "Develops brand voice, positioning, messaging consistency and differentiation.",
    color: "#FFD700", bgGradient: "rgba(255,215,0,0.08)",
    icon: Palette, stat: "100%", statLabel: "brand consistency",
    skills: ["Brand voice", "Style guides", "Differentiation"],
    avatar: AvatarBrand,
  },
  {
    id: "automation", name: "Zeno", role: "Automation Workflow", tier: "operations",
    description: "Builds automation flows, execution chains, integrations and efficiency systems.",
    color: "#14B8A6", bgGradient: "rgba(20,184,166,0.08)",
    icon: Workflow, stat: "200+ flows", statLabel: "deployed",
    skills: ["Zapier / Make", "Workflow design", "Integration ops"],
    avatar: AvatarAutomation,
  },
  {
    id: "receptionist", name: "Aria", role: "Receptionist / Voice", tier: "operations",
    description: "Handles voice interactions, inbound enquiries, receptionist tasks and routing.",
    color: "#F59E0B", bgGradient: "rgba(245,158,11,0.08)",
    icon: PhoneCall, stat: "48 voices", statLabel: "available",
    skills: ["Voice routing", "Inbound handling", "Conversational AI"],
    avatar: AvatarReceptionist,
  },
  {
    id: "influencer", name: "Nova", role: "Influencer Collaboration", tier: "revenue",
    description: "Finds creators, evaluates influencer fit, drafts outreach and manages strategy.",
    color: "#FF6B6B", bgGradient: "rgba(255,107,107,0.08)",
    icon: Users, stat: "10k+", statLabel: "creator network",
    skills: ["Creator vetting", "Brief writing", "Collab management"],
    avatar: AvatarInfluencer,
  },
];

const TIER_LABELS: Record<AgentTier, string> = {
  executive: "Executive",
  growth: "Growth",
  creative: "Creative",
  revenue: "Revenue",
  operations: "Operations",
};

const TIER_COLORS: Record<AgentTier, string> = {
  executive: "#FFD700",
  growth: "#4ECDC4",
  creative: "#A78BFA",
  revenue: "#FF6B6B",
  operations: "#3B82F6",
};

// ─── AGENT CARD ───────────────────────────────────────────────────────────────

function AgentCard({ agent, index, onClick }: {
  agent: Agent;
  index: number;
  onClick: (a: Agent) => void;
}) {
  const AvatarComponent = agent.avatar;
  const Icon = agent.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 32 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ delay: (index % 9) * 0.045, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="agent-card-v2"
      style={{ "--ac": agent.color, "--ac-bg": agent.bgGradient } as React.CSSProperties}
      onClick={() => onClick(agent)}
    >
      {/* Tier badge */}
      <div className="acard__tier" style={{ color: TIER_COLORS[agent.tier], borderColor: `${TIER_COLORS[agent.tier]}33`, background: `${TIER_COLORS[agent.tier]}0d` }}>
        {TIER_LABELS[agent.tier]}
      </div>

      {/* Status dot */}
      <div className="acard__online">
        <span className="acard__dot" />
        Online
      </div>

      {/* Avatar */}
      <div className="acard__avatar-wrap">
        <AvatarComponent size={64} />
        <div className="acard__avatar-ring" />
      </div>

      {/* Identity */}
      <div className="acard__name">{agent.name}</div>
      <div className="acard__role">{agent.role}</div>

      {/* Skills */}
      <div className="acard__skills">
        {agent.skills.slice(0, 2).map(s => (
          <span key={s} className="acard__skill">{s}</span>
        ))}
      </div>

      {/* Stat */}
      <div className="acard__stat-row">
        <Zap size={10} className="acard__zap" />
        <span className="acard__stat-val">{agent.stat}</span>
        <span className="acard__stat-label">{agent.statLabel}</span>
      </div>

      {/* Hover glow */}
      <div className="acard__glow" />
    </motion.div>
  );
}

// ─── AGENT MODAL ──────────────────────────────────────────────────────────────

function AgentModal({ agent, onClose }: { agent: Agent; onClose: () => void }) {
  const AvatarComponent = agent.avatar;
  const Icon = agent.icon;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="agent-modal-overlay"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.92, y: 24 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.92, y: 24 }}
        transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
        className="agent-modal"
        style={{ "--ac": agent.color } as React.CSSProperties}
        onClick={e => e.stopPropagation()}
      >
        <button className="agent-modal__close" onClick={onClose}>✕</button>

        <div className="agent-modal__header">
          <div className="agent-modal__avatar">
            <AvatarComponent size={80} />
          </div>
          <div>
            <div className="agent-modal__name">{agent.name}</div>
            <div className="agent-modal__role" style={{ color: agent.color }}>{agent.role}</div>
            <div className="agent-modal__tier-badge" style={{ color: TIER_COLORS[agent.tier], background: `${TIER_COLORS[agent.tier]}15`, borderColor: `${TIER_COLORS[agent.tier]}30` }}>
              {TIER_LABELS[agent.tier]} tier
            </div>
          </div>
        </div>

        <p className="agent-modal__desc">{agent.description}</p>

        <div className="agent-modal__stats">
          <div className="agent-modal__stat">
            <span className="agent-modal__stat-val" style={{ color: agent.color }}>{agent.stat}</span>
            <span className="agent-modal__stat-label">{agent.statLabel}</span>
          </div>
          <div className="agent-modal__stat">
            <span className="agent-modal__stat-val" style={{ color: agent.color }}>24/7</span>
            <span className="agent-modal__stat-label">autonomous</span>
          </div>
          <div className="agent-modal__stat">
            <span className="agent-modal__stat-val" style={{ color: agent.color }}>0s</span>
            <span className="agent-modal__stat-label">setup time</span>
          </div>
        </div>

        <div className="agent-modal__skills-title">Core capabilities</div>
        <div className="agent-modal__skills">
          {agent.skills.map(s => (
            <span key={s} className="agent-modal__skill" style={{ borderColor: `${agent.color}33`, color: agent.color, background: `${agent.color}0d` }}>
              {s}
            </span>
          ))}
        </div>

        <button className="agent-modal__cta" style={{ background: `linear-gradient(135deg, ${agent.color}, ${agent.color}99)` }}>
          Activate {agent.name} <ChevronRight size={14} />
        </button>
      </motion.div>
    </motion.div>
  );
}

// ─── AGENTS SECTION ───────────────────────────────────────────────────────────

export function AgentsSection() {
  const [activeFilter, setActiveFilter] = useState<AgentTier | "all">("all");
  const [activeAgent, setActiveAgent] = useState<Agent | null>(null);
  const [search, setSearch] = useState("");

  const filtered = ALL_AGENTS.filter(a => {
    const matchTier = activeFilter === "all" || a.tier === activeFilter;
    const matchSearch = search === "" ||
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.role.toLowerCase().includes(search.toLowerCase()) ||
      a.skills.some(s => s.toLowerCase().includes(search.toLowerCase()));
    return matchTier && matchSearch;
  });

  const tiers: Array<AgentTier | "all"> = ["all", "executive", "growth", "creative", "revenue", "operations"];

  return (
    <section className="agents-v2" id="agents">
      <style>{AGENTS_CSS}</style>

      {/* Header */}
      <div className="section-header">
        <motion.span className="section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <Bot size={13} /> YOUR AI WORKFORCE
        </motion.span>
        <motion.h2 className="section-title" initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8, ease: [0.16,1,0.3,1] }}>
          27 specialist agents.<br />One unified team.
        </motion.h2>
        <motion.p className="section-subtitle" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.1 }}>
          Every role your ecommerce business needs — automated, always on, and working in sync.
        </motion.p>
      </div>

      {/* Controls */}
      <motion.div
        className="agents-v2__controls"
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ delay: 0.15 }}
      >
        {/* Search */}
        <div className="agents-v2__search-wrap">
          <Filter size={14} className="agents-v2__search-icon" />
          <input
            className="agents-v2__search"
            placeholder="Search agents, roles, or skills…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {/* Tier filters */}
        <div className="agents-v2__filters">
          {tiers.map(tier => (
            <button
              key={tier}
              className={`agents-v2__filter ${activeFilter === tier ? "agents-v2__filter--active" : ""}`}
              style={activeFilter === tier && tier !== "all" ? {
                background: `${TIER_COLORS[tier as AgentTier]}18`,
                borderColor: `${TIER_COLORS[tier as AgentTier]}55`,
                color: TIER_COLORS[tier as AgentTier],
              } : {}}
              onClick={() => setActiveFilter(tier)}
            >
              {tier === "all" ? `All agents (${ALL_AGENTS.length})` : `${TIER_LABELS[tier as AgentTier]} (${ALL_AGENTS.filter(a => a.tier === tier).length})`}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Grid */}
      <motion.div className="agents-v2__grid" layout>
        <AnimatePresence mode="popLayout">
          {filtered.map((agent, i) => (
            <AgentCard key={agent.id} agent={agent} index={i} onClick={setActiveAgent} />
          ))}
        </AnimatePresence>
        {filtered.length === 0 && (
          <div className="agents-v2__empty">
            No agents match your search. <button onClick={() => { setSearch(""); setActiveFilter("all"); }}>Clear filters</button>
          </div>
        )}
      </motion.div>

      {/* CTA strip */}
      <motion.div
        className="agents-v2__cta-strip"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ delay: 0.2 }}
      >
        <div className="agents-v2__cta-left">
          <Star size={14} className="agents-v2__cta-star" />
          <span>All 27 agents available on Studio & Enterprise plans. Free plan includes 3 agents.</span>
        </div>
        <a href="#pricing" className="agents-v2__cta-btn">
          See pricing <ChevronRight size={14} />
        </a>
      </motion.div>

      {/* Modal */}
      <AnimatePresence>
        {activeAgent && (
          <AgentModal agent={activeAgent} onClose={() => setActiveAgent(null)} />
        )}
      </AnimatePresence>
    </section>
  );
}

// ─── SCOPED CSS ───────────────────────────────────────────────────────────────

const AGENTS_CSS = `
  .agents-v2 {
    padding: 120px 24px 80px;
    max-width: 1320px;
    margin: 0 auto;
  }

  /* Controls */
  .agents-v2__controls {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 48px;
  }
  .agents-v2__search-wrap {
    position: relative;
    max-width: 440px;
    margin: 0 auto;
    width: 100%;
  }
  .agents-v2__search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: #5a5a72;
    pointer-events: none;
  }
  .agents-v2__search {
    width: 100%;
    background: #16161c;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 11px 16px 11px 38px;
    color: #f0f0f4;
    font-size: 14px;
    font-family: 'DM Sans', sans-serif;
    outline: none;
    transition: border-color 0.2s;
  }
  .agents-v2__search:focus { border-color: rgba(124,106,247,0.5); }
  .agents-v2__search::placeholder { color: #5a5a72; }
  .agents-v2__filters {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
  }
  .agents-v2__filter {
    padding: 7px 16px;
    border-radius: 100px;
    background: #16161c;
    border: 1px solid rgba(255,255,255,0.08);
    color: #9494a8;
    font-size: 12px;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.02em;
  }
  .agents-v2__filter:hover { color: #f0f0f4; border-color: rgba(255,255,255,0.15); }
  .agents-v2__filter--active { color: #f0f0f4 !important; }

  /* Grid */
  .agents-v2__grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    gap: 14px;
    margin-bottom: 40px;
  }

  /* Individual card */
  .agent-card-v2 {
    position: relative;
    background: #111116;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 22px 20px 18px;
    cursor: pointer;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 0;
    transition: border-color 0.3s, transform 0.25s, background 0.3s;
    min-height: 240px;
  }
  .agent-card-v2:hover {
    border-color: var(--ac);
    transform: translateY(-5px);
    background: #141419;
  }
  .agent-card-v2:hover .acard__glow { opacity: 1; }
  .agent-card-v2:hover .acard__avatar-ring { opacity: 1; }

  .acard__glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at top, var(--ac-bg) 0%, transparent 65%);
    opacity: 0;
    transition: opacity 0.4s;
    pointer-events: none;
  }

  .acard__tier {
    position: absolute;
    top: 14px;
    left: 14px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 6px;
    border: 1px solid;
  }
  .acard__online {
    position: absolute;
    top: 14px;
    right: 14px;
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    color: #5a5a72;
    font-weight: 600;
  }
  .acard__dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 5px #10B981;
    animation: agent-pulse 2.2s ease-in-out infinite;
  }
  @keyframes agent-pulse {
    0%,100% { opacity: 1; } 50% { opacity: 0.4; }
  }

  /* Avatar */
  .acard__avatar-wrap {
    position: relative;
    width: 64px;
    height: 64px;
    margin: 28px 0 14px;
  }
  .acard__avatar-ring {
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    border: 1.5px solid var(--ac);
    opacity: 0;
    transition: opacity 0.35s;
    animation: ring-spin 6s linear infinite;
  }
  @keyframes ring-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .acard__name {
    font-family: 'Syne', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #f0f0f4;
    margin-bottom: 2px;
  }
  .acard__role {
    font-size: 11px;
    font-weight: 600;
    color: var(--ac);
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 12px;
    opacity: 0.85;
  }
  .acard__skills {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 14px;
    flex: 1;
  }
  .acard__skill {
    font-size: 10px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    color: #9494a8;
    white-space: nowrap;
  }
  .acard__stat-row {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 7px 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 9px;
    margin-top: auto;
  }
  .acard__zap { color: var(--ac); flex-shrink: 0; }
  .acard__stat-val {
    font-size: 12px;
    font-weight: 700;
    color: var(--ac);
  }
  .acard__stat-label {
    font-size: 11px;
    color: #5a5a72;
  }

  /* Empty state */
  .agents-v2__empty {
    grid-column: 1/-1;
    text-align: center;
    padding: 60px 24px;
    color: #5a5a72;
    font-size: 15px;
  }
  .agents-v2__empty button {
    background: none;
    border: none;
    color: #7C6AF7;
    cursor: pointer;
    font-size: 15px;
    text-decoration: underline;
    font-family: inherit;
    margin-left: 6px;
  }

  /* CTA strip */
  .agents-v2__cta-strip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 18px 24px;
    background: #111116;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    flex-wrap: wrap;
  }
  .agents-v2__cta-left {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: #9494a8;
  }
  .agents-v2__cta-star { color: #F59E0B; flex-shrink: 0; }
  .agents-v2__cta-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 9px 20px;
    background: linear-gradient(135deg, #7C6AF7, #5b4de0);
    color: #fff;
    border-radius: 9px;
    text-decoration: none;
    font-size: 13px;
    font-weight: 700;
    white-space: nowrap;
    box-shadow: 0 0 20px rgba(124,106,247,0.25);
    transition: opacity 0.2s;
  }
  .agents-v2__cta-btn:hover { opacity: 0.9; }

  /* Modal */
  .agent-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(8px);
    z-index: 2000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }
  .agent-modal {
    background: #111116;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 36px;
    max-width: 480px;
    width: 100%;
    position: relative;
    box-shadow: 0 0 80px rgba(0,0,0,0.6), 0 0 40px rgba(0,0,0,0.4);
  }
  .agent-modal::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 120px;
    border-radius: 24px 24px 0 0;
    background: radial-gradient(ellipse at center top, color-mix(in srgb, var(--ac) 12%, transparent), transparent 80%);
    pointer-events: none;
  }
  .agent-modal__close {
    position: absolute;
    top: 16px; right: 16px;
    width: 32px; height: 32px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    color: #9494a8;
    cursor: pointer;
    font-size: 13px;
    display: flex; align-items: center; justify-content: center;
    transition: background 0.2s;
  }
  .agent-modal__close:hover { background: rgba(255,255,255,0.1); color: #f0f0f4; }
  .agent-modal__header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
    position: relative;
  }
  .agent-modal__avatar {
    flex-shrink: 0;
    width: 80px; height: 80px;
    border-radius: 50%;
    overflow: hidden;
    border: 2px solid rgba(255,255,255,0.08);
  }
  .agent-modal__name {
    font-family: 'Syne', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #f0f0f4;
    margin-bottom: 4px;
  }
  .agent-modal__role {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .agent-modal__tier-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 6px;
    border: 1px solid;
  }
  .agent-modal__desc {
    font-size: 14px;
    color: #9494a8;
    line-height: 1.65;
    margin-bottom: 24px;
  }
  .agent-modal__stats {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 12px;
    margin-bottom: 24px;
  }
  .agent-modal__stat {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    text-align: center;
  }
  .agent-modal__stat-val {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 800;
    line-height: 1;
  }
  .agent-modal__stat-label {
    font-size: 11px;
    color: #5a5a72;
    font-weight: 600;
  }
  .agent-modal__skills-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5a5a72;
    margin-bottom: 10px;
  }
  .agent-modal__skills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 28px;
  }
  .agent-modal__skill {
    font-size: 12px;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 8px;
    border: 1px solid;
  }
  .agent-modal__cta {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px;
    border-radius: 12px;
    border: none;
    color: #fff;
    font-size: 15px;
    font-weight: 700;
    font-family: 'Syne', sans-serif;
    cursor: pointer;
    transition: opacity 0.2s, transform 0.2s;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
  }
  .agent-modal__cta:hover { opacity: 0.92; transform: translateY(-1px); }

  @media (max-width: 640px) {
    .agents-v2__grid { grid-template-columns: repeat(2, 1fr); }
    .agent-modal { padding: 24px; }
    .agent-modal__stats { grid-template-columns: repeat(3,1fr); }
  }
  @media (max-width: 420px) {
    .agents-v2__grid { grid-template-columns: 1fr 1fr; }
  }
`;
