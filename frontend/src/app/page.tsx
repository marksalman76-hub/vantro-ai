"use client";

import { useEffect, useRef, useState, useCallback, Suspense } from "react";
import { motion, useScroll, useTransform, useSpring, AnimatePresence, useMotionValue, useInView } from "framer-motion";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Sphere, MeshDistortMaterial, Float, Stars, Trail, OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  Zap, Brain, Video, Wand2, Users, BarChart3, Globe, Play,
  Sparkles, ChevronRight, Star, Shield, Clock, ArrowRight, Menu, X, CheckCircle2, Layers, Cpu,
  Mic, FileText, Mail, Share2, TrendingUp, Bot, Infinity,
  ChevronDown, Eye, Lock, Rocket, Award, Target
} from "lucide-react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

// ─── CONSTANTS ──────────────────────────────────────────────────────────────

const AGENTS = [
  { id: "aria",   name: "Aria",    role: "Creative Director",    color: "#FF6B6B", icon: Wand2,    specialty: "Video & Image Gen",   stat: "2.4M assets created" },
  { id: "nova",   name: "Nova",    role: "Marketing Strategist", color: "#4ECDC4", icon: TrendingUp, specialty: "Campaign Automation", stat: "380% avg. ROI lift"  },
  { id: "echo",   name: "Echo",    role: "Content Writer",       color: "#A78BFA", icon: FileText, specialty: "SEO & Copywriting",    stat: "10k words/min"       },
  { id: "pulse",  name: "Pulse",   role: "Data Analyst",         color: "#F59E0B", icon: BarChart3, specialty: "Insights & Reports",  stat: "Real-time analytics" },
  { id: "vox",    name: "Vox",     role: "Voice & Audio",        color: "#10B981", icon: Mic,      specialty: "Podcast & Voiceover",  stat: "48 voice personas"   },
  { id: "atlas",  name: "Atlas",   role: "Sales Closer",         color: "#3B82F6", icon: Target,   specialty: "Lead & CRM Ops",       stat: "$4.2M pipeline built"},
  { id: "lynx",   name: "Lynx",    role: "Social Manager",       color: "#EC4899", icon: Share2,   specialty: "Viral Content Engine", stat: "12M impressions/mo"  },
  { id: "cipher", name: "Cipher",  role: "Code Engineer",        color: "#14B8A6", icon: Cpu,      specialty: "Full-stack Dev",       stat: "40% faster shipping" },
];

const PRESETS = [
  { label: "CINEMATIC REVEAL",  tag: "Video",  hot: true  },
  { label: "VIRAL REEL",        tag: "Video",  hot: true  },
  { label: "BRAND ANTHEM",      tag: "Audio",  hot: false },
  { label: "3D PRODUCT SHOT",   tag: "Image",  hot: false },
  { label: "AI INFLUENCER",     tag: "Video",  hot: true  },
  { label: "MOTION POSTER",     tag: "Image",  hot: false },
  { label: "PODCAST CLONE",     tag: "Audio",  hot: false },
  { label: "AVATAR STUDIO",     tag: "Video",  hot: true  },
  { label: "NEON CITY SCENE",   tag: "Video",  hot: false },
  { label: "DATA VIZ REEL",     tag: "Video",  hot: false },
  { label: "STORY HOOK",        tag: "Video",  hot: true  },
  { label: "VOICE MANIFESTO",   tag: "Audio",  hot: false },
];

const STATS = [
  { value: "2.1M+",  label: "Creators worldwide",    icon: Globe  },
  { value: "180M+",  label: "Assets generated",       icon: Layers },
  { value: "99.97%", label: "Uptime SLA",             icon: Shield },
  { value: "< 8s",   label: "Avg. generation time",   icon: Clock  },
];

const PRICING = [
  {
    name: "Creator",
    price: 29,
    desc: "Perfect for solo creators and freelancers.",
    features: ["3 AI Agents", "500 generations/mo", "HD Video export", "Basic presets", "Email support"],
    cta: "Demo trial",
    highlight: false,
  },
  {
    name: "Studio",
    price: 79,
    desc: "For growing teams and power users.",
    features: ["All 8 AI Agents", "Unlimited generations", "4K Video export", "All viral presets", "Priority support", "Custom voice cloning", "API access"],
    cta: "Demo trial",
    highlight: true,
  },
  {
    name: "Enterprise",
    price: null,
    desc: "Custom infrastructure for large teams.",
    features: ["Unlimited agents", "Dedicated GPU cluster", "SLA guarantee", "Custom model training", "SSO & compliance", "Dedicated CSM"],
    cta: "Contact sales",
    highlight: false,
  },
];

// ─── 3D COMPONENTS ──────────────────────────────────────────────────────────

function OrbField() {
  const groupRef = useRef<THREE.Group>(null);
  const time = useRef(0);

  useFrame((_, delta) => {
    time.current += delta * 0.4;
    if (groupRef.current) {
      groupRef.current.rotation.y = time.current * 0.12;
      groupRef.current.rotation.x = Math.sin(time.current * 0.08) * 0.15;
    }
  });

  return (
    <group ref={groupRef}>
      <Stars radius={80} depth={50} count={3000} factor={4} saturation={0.5} fade speed={1} />

      {/* Central orb */}
      <Float speed={1.4} rotationIntensity={0.6} floatIntensity={0.8}>
        <Sphere args={[1.8, 128, 128]}>
          <MeshDistortMaterial
            color="#0F172A"
            attach="material"
            distort={0.45}
            speed={1.8}
            roughness={0}
            metalness={0.9}
            envMapIntensity={2}
          />
        </Sphere>
      </Float>

      {/* Ring 1 */}
      {Array.from({ length: 8 }).map((_, i) => {
        const angle = (i / 8) * Math.PI * 2;
        return (
          <Float key={i} speed={1 + i * 0.1} floatIntensity={0.3}>
            <Sphere
              args={[0.18, 32, 32]}
              position={[Math.cos(angle) * 3.2, Math.sin(angle * 0.5) * 0.6, Math.sin(angle) * 3.2]}
            >
              <meshStandardMaterial
                color={AGENTS[i].color}
                emissive={AGENTS[i].color}
                emissiveIntensity={1.4}
                roughness={0.1}
                metalness={0.8}
              />
            </Sphere>
          </Float>
        );
      })}

      {/* Ring 2 - smaller outer ring */}
      {Array.from({ length: 16 }).map((_, i) => {
        const angle = (i / 16) * Math.PI * 2;
        const colors = ["#FF6B6B","#4ECDC4","#A78BFA","#F59E0B","#10B981","#3B82F6","#EC4899","#14B8A6"];
        return (
          <Sphere
            key={`r2-${i}`}
            args={[0.06, 16, 16]}
            position={[Math.cos(angle) * 5.5, Math.sin(angle * 2) * 0.4, Math.sin(angle) * 5.5]}
          >
            <meshStandardMaterial
              color={colors[i % 8]}
              emissive={colors[i % 8]}
              emissiveIntensity={0.8}
            />
          </Sphere>
        );
      })}

      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 10]} intensity={2} color="#4ECDC4" />
      <pointLight position={[-10, -10, -5]} intensity={1.5} color="#A78BFA" />
      <pointLight position={[0, 0, 8]} intensity={1} color="#FF6B6B" />
    </group>
  );
}

function Scene3D() {
  return (
    <Canvas
      camera={{ position: [0, 0, 10], fov: 50 }}
      style={{ background: "transparent" }}
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true }}
    >
      <Suspense fallback={null}>
        <OrbField />
      </Suspense>
    </Canvas>
  );
}

// ─── CURSOR GLOW ────────────────────────────────────────────────────────────

function CursorGlow() {
  const cursorX = useMotionValue(-200);
  const cursorY = useMotionValue(-200);
  const springConfig = { damping: 25, stiffness: 300 };
  const x = useSpring(cursorX, springConfig);
  const y = useSpring(cursorY, springConfig);

  useEffect(() => {
    const move = (e: MouseEvent) => {
      cursorX.set(e.clientX - 200);
      cursorY.set(e.clientY - 200);
    };
    window.addEventListener("mousemove", move);
    return () => window.removeEventListener("mousemove", move);
  }, [cursorX, cursorY]);

  return (
    <motion.div
      style={{ x, y }}
      className="cursor-glow"
    />
  );
}

// ─── NOISE OVERLAY ──────────────────────────────────────────────────────────

function NoiseTexture() {
  return <div className="noise-overlay" aria-hidden="true" />;
}

// ─── NAV ────────────────────────────────────────────────────────────────────

function Nav({ muted, onToggleAudio }: { muted: boolean; onToggleAudio: () => void }) {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", handler);
    return () => window.removeEventListener("scroll", handler);
  }, []);

  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className={`nav ${scrolled ? "nav--scrolled" : ""}`}
    >
      <div className="nav__inner">
        {/* Logo */}
        <a href="#" className="nav__logo">
          <span className="nav__logo-mark">◈</span>
          <span className="nav__logo-text">NEXUS</span>
          <span className="nav__logo-tag">AI</span>
        </a>

        {/* Links */}
        <div className="nav__links">
          {["Agents", "Pricing", "Enterprise"].map((l) => (
            <a key={l} href={`#${l.toLowerCase()}`} className="nav__link">{l}</a>
          ))}
        </div>

        {/* Actions */}
        <div className="nav__actions">
          <a href="#" className="nav__btn-ghost">Sign in</a>
          <a href="/demo" className="nav__btn-primary">
            Demo <ArrowRight size={14} />
          </a>
          <button className="nav__hamburger" onClick={() => setOpen(!open)}>
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="nav__mobile"
          >
            {["Agents", "Pricing", "Enterprise"].map((l) => (
              <a key={l} href={`#${l.toLowerCase()}`} className="nav__mobile-link" onClick={() => setOpen(false)}>{l}</a>
            ))}
            <a href="/demo" className="nav__btn-primary nav__btn-primary--mobile">Demo →</a>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}

// ─── ANIMATED COUNTER ───────────────────────────────────────────────────────

function Counter({ value, duration = 2 }: { value: string; duration?: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  const [displayed, setDisplayed] = useState("0");

  useEffect(() => {
    if (!inView) return;
    const numeric = parseFloat(value.replace(/[^0-9.]/g, ""));
    const suffix = value.replace(/[0-9.]/g, "");
    const start = Date.now();
    const tick = () => {
      const elapsed = (Date.now() - start) / 1000;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = numeric * eased;
      setDisplayed(
        value.includes(".")
          ? current.toFixed(2) + suffix
          : Math.floor(current) + suffix
      );
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [inView, value, duration]);

  return <span ref={ref}>{displayed}</span>;
}

// ─── TYPEWRITER ─────────────────────────────────────────────────────────────

const TYPEWRITER_PHRASES = [
  "cinematic videos",
  "viral social content",
  "AI-powered campaigns",
  "voice clones",
  "brand identities",
  "autonomous agents",
];

function Typewriter() {
  const [phrase, setPhrase] = useState(0);
  const [text, setText] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const target = TYPEWRITER_PHRASES[phrase];
    let timeout: ReturnType<typeof setTimeout>;

    if (!deleting && text.length < target.length) {
      timeout = setTimeout(() => setText(target.slice(0, text.length + 1)), 55);
    } else if (!deleting && text.length === target.length) {
      timeout = setTimeout(() => setDeleting(true), 2200);
    } else if (deleting && text.length > 0) {
      timeout = setTimeout(() => setText(text.slice(0, -1)), 28);
    } else if (deleting && text.length === 0) {
      setDeleting(false);
      setPhrase((p) => (p + 1) % TYPEWRITER_PHRASES.length);
    }

    return () => clearTimeout(timeout);
  }, [text, deleting, phrase]);

  return (
    <span className="typewriter">
      <span className="typewriter__text">{text}</span>
      <span className="typewriter__cursor">|</span>
    </span>
  );
}

// ─── HERO ───────────────────────────────────────────────────────────────────

function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: containerRef, offset: ["start start", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "40%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.7], [1, 0]);

  return (
    <section ref={containerRef} className="hero" id="platform">
      {/* 3D Canvas */}
      <div className="hero__canvas">
        <Scene3D />
      </div>

      <motion.div style={{ y, opacity }} className="hero__content">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.7 }}
          className="hero__badge"
        >
          <Sparkles size={12} />
          <span>The world&apos;s first unified AI creation supercomputer</span>
          <span className="hero__badge-new">NEW</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          className="hero__headline"
        >
          Your entire creative
          <br />
          team, powered by AI.
        </motion.h1>

        {/* Subline */}
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="hero__subline"
        >
          Generate&nbsp;<Typewriter />
          <br className="hero__br" />
          with a fleet of specialized AI agents that never sleep.
        </motion.p>

        {/* CTA row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.7 }}
          className="hero__cta-row"
        >
          <a href="#pricing" className="hero__cta-primary">
            Sign up
            <span className="hero__cta-glow" />
          </a>
        </motion.div>

        {/* Trust */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="hero__trust"
        >
          <div className="hero__avatars">
            {["#FF6B6B","#4ECDC4","#A78BFA","#F59E0B","#10B981"].map((c, i) => (
              <div key={i} className="hero__avatar" style={{ background: c, zIndex: 5 - i }} />
            ))}
          </div>
          <span className="hero__trust-text">
            Trusted by <strong>2.1M+ creators</strong> in 120 countries
          </span>
          <div className="hero__stars">
            {Array.from({length: 5}).map((_,i) => <Star key={i} size={11} fill="currentColor" />)}
            <span>4.9/5</span>
          </div>
        </motion.div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ repeat: Number.POSITIVE_INFINITY, duration: 2 }}
        className="hero__scroll-hint"
      >
        <ChevronDown size={20} />
      </motion.div>
    </section>
  );
}

// ─── MARQUEE ────────────────────────────────────────────────────────────────

function Marquee() {
  const logos = ["Spotify", "Shopify", "Figma", "Stripe", "Notion", "Vercel", "Linear", "Loom", "Arc", "Framer", "Pitch", "Webflow"];
  return (
    <div className="marquee-wrap">
      <div className="marquee-track">
        {[...logos, ...logos].map((l, i) => (
          <span key={i} className="marquee-item">{l}</span>
        ))}
      </div>
    </div>
  );
}

// ─── STATS STRIP ────────────────────────────────────────────────────────────

function StatsStrip() {
  return (
    <section className="stats-strip">
      {STATS.map(({ value, label, icon: Icon }) => (
        <div key={label} className="stats-strip__item">
          <Icon size={20} className="stats-strip__icon" />
          <div className="stats-strip__value">
            <Counter value={value} />
          </div>
          <div className="stats-strip__label">{label}</div>
        </div>
      ))}
    </section>
  );
}

// ─── AGENTS GRID ────────────────────────────────────────────────────────────

function AgentsGrid() {
  const [active, setActive] = useState<string | null>(null);

  return (
    <section className="agents" id="agents">
      <div className="section-header">
        <motion.span
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="section-eyebrow"
        >
          <Bot size={13} /> AI AGENTS
        </motion.span>
        <motion.h2
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: [0.16,1,0.3,1] }}
          className="section-title"
        >
          Meet your new<br />dream team.
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1, duration: 0.7 }}
          className="section-subtitle"
        >
          8 specialized agents. One shared brain. Infinite output.
        </motion.p>
      </div>

      <div className="agents__grid">
        {AGENTS.map((agent, i) => {
          const Icon = agent.icon;
          return (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ delay: i * 0.07, duration: 0.7, ease: [0.16,1,0.3,1] }}
              className={`agent-card ${active === agent.id ? "agent-card--active" : ""}`}
              style={{ "--agent-color": agent.color } as React.CSSProperties}
              onMouseEnter={() => setActive(agent.id)}
              onMouseLeave={() => setActive(null)}
            >
              <div className="agent-card__glow" />
              <div className="agent-card__icon-wrap">
                <Icon size={22} />
              </div>
              <div className="agent-card__body">
                <div className="agent-card__name">{agent.name}</div>
                <div className="agent-card__role">{agent.role}</div>
                <div className="agent-card__specialty">{agent.specialty}</div>
              </div>
              <div className="agent-card__stat">
                <Zap size={10} />
                {agent.stat}
              </div>
              <div className="agent-card__status">
                <span className="agent-card__dot" /> Online
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="agents__cta">
        <a href="#" className="btn-outline">
          Explore all agents <ChevronRight size={14} />
        </a>
      </div>
    </section>
  );
}

// ─── STUDIO / PRESETS ───────────────────────────────────────────────────────

function Studio() {
  const [activePreset, setActivePreset] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"Video"|"Image"|"Audio">("Video");

  const filtered = PRESETS.filter(p => activeTab === "Video" ? p.tag === "Video" : activeTab === "Image" ? p.tag === "Image" : p.tag === "Audio");

  return (
    <section className="studio" id="studio">
      <div className="section-header">
        <motion.span className="section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <Video size={13} /> CREATION STUDIO
        </motion.span>
        <motion.h2 className="section-title" initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }}>
          One-click presets.<br />Hollywood output.
        </motion.h2>
        <motion.p className="section-subtitle" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.1 }}>
          Start from a proven template or prompt from scratch. Every output is 4K-ready.
        </motion.p>
      </div>

      {/* Tab bar */}
      <div className="studio__tabs">
        {(["Video","Image","Audio"] as const).map(tab => (
          <button
            key={tab}
            className={`studio__tab ${activeTab === tab ? "studio__tab--active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === "Video" && <Video size={13} />}
            {tab === "Image" && <Eye size={13} />}
            {tab === "Audio" && <Mic size={13} />}
            {tab}
          </button>
        ))}
      </div>

      {/* Preset grid */}
      <motion.div className="studio__grid" layout>
        <AnimatePresence mode="popLayout">
          {filtered.map((preset, i) => (
            <motion.button
              key={preset.label}
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ delay: i * 0.04, duration: 0.35 }}
              className={`preset-chip ${activePreset === i ? "preset-chip--active" : ""}`}
              onClick={() => setActivePreset(activePreset === i ? null : i)}
            >
              {preset.hot && <span className="preset-chip__hot">🔥</span>}
              {preset.label}
              <span className="preset-chip__tag">{preset.tag}</span>
            </motion.button>
          ))}
        </AnimatePresence>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="studio__prompt-box"
      >
        <div className="studio__prompt-label">
          <Wand2 size={14} />
          <span>Try the studio — no signup needed</span>
        </div>
        <div className="studio__prompt-input-row">
          <input
            className="studio__prompt-input"
            placeholder="A cinematic drone shot over a neon-lit Tokyo skyline at dusk…"
            readOnly
          />
          <button className="studio__prompt-btn">
            <Sparkles size={14} />
            Generate
          </button>
        </div>
        <div className="studio__prompt-modes">
          {["4K Video", "Cinematic", "6 seconds", "Seedance v2.0"].map(m => (
            <span key={m} className="studio__mode-tag">{m}</span>
          ))}
        </div>
      </motion.div>
    </section>
  );
}

// ─── FEATURE BENTO ──────────────────────────────────────────────────────────

function FeatureBento() {
  return (
    <section className="bento" id="features">
      <div className="section-header">
        <motion.span className="section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <Layers size={13} /> PLATFORM
        </motion.span>
        <motion.h2 className="section-title" initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }}>
          Everything in one orbit.
        </motion.h2>
      </div>

      <div className="bento__grid">
        {/* Big card - Supercomputer */}
        <motion.div
          className="bento-card bento-card--xl"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <div className="bento-card__eyebrow"><Cpu size={14} /> SUPERCOMPUTER</div>
          <h3 className="bento-card__title">Your agents work 24/7,<br />even while you sleep.</h3>
          <p className="bento-card__body">Autonomous scheduling, memory, connectors, and real-time automations — all orchestrated by a shared intelligence layer.</p>
          <div className="bento-card__visual bento-card__visual--grid">
            {Array.from({length: 24}).map((_,i) => (
              <motion.div
                key={i}
                className="bento-card__dot"
                animate={{ opacity: [0.2, 1, 0.2], scale: [1, 1.3, 1] }}
                transition={{ delay: i * 0.12, duration: 2.5, repeat: Number.POSITIVE_INFINITY }}
              />
            ))}
          </div>
        </motion.div>

        {/* Brain AI */}
        <motion.div
          className="bento-card bento-card--md bento-card--accent-purple"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1, duration: 0.8 }}
        >
          <div className="bento-card__eyebrow"><Brain size={14} /> BRAIN AI</div>
          <h3 className="bento-card__title">Learns your brand.<br />Thinks like you.</h3>
          <p className="bento-card__body">Upload docs, style guides, past work — your agents internalize everything.</p>
          <div className="bento-card__pulse">
            <div className="bento-card__pulse-ring" />
            <div className="bento-card__pulse-ring bento-card__pulse-ring--2" />
            <Brain size={28} className="bento-card__pulse-icon" />
          </div>
        </motion.div>

        {/* Video gen */}
        <motion.div
          className="bento-card bento-card--md bento-card--accent-teal"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.15, duration: 0.8 }}
        >
          <div className="bento-card__eyebrow"><Video size={14} /> CINEMA ENGINE</div>
          <h3 className="bento-card__title">4K video in under 8 seconds.</h3>
          <p className="bento-card__body">Powered by Seedance 2.0 — the fastest diffusion model on the planet.</p>
          <div className="bento-card__meter">
            <motion.div
              className="bento-card__meter-fill"
              initial={{ width: 0 }}
              whileInView={{ width: "87%" }}
              viewport={{ once: true }}
              transition={{ duration: 1.5, ease: "easeOut", delay: 0.3 }}
            />
            <span className="bento-card__meter-label">87% faster than competitors</span>
          </div>
        </motion.div>

        {/* Integrations */}
        <motion.div
          className="bento-card bento-card--sm"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.8 }}
        >
          <div className="bento-card__eyebrow"><Globe size={14} /> INTEGRATIONS</div>
          <h3 className="bento-card__title">200+ connectors.</h3>
          <div className="bento-card__integrations">
            {["Slack","Notion","HubSpot","Zapier","Shopify","YouTube","TikTok","X"].map(s => (
              <span key={s} className="bento-card__badge">{s}</span>
            ))}
          </div>
        </motion.div>

        {/* Gamification */}
        <motion.div
          className="bento-card bento-card--sm bento-card--accent-amber"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.25, duration: 0.8 }}
        >
          <div className="bento-card__eyebrow"><Award size={14} /> MILESTONES</div>
          <h3 className="bento-card__title">Level up your workflow.</h3>
          <div className="bento-card__xp">
            <div className="bento-card__xp-bar">
              <motion.div
                className="bento-card__xp-fill"
                initial={{ width: 0 }}
                whileInView={{ width: "72%" }}
                viewport={{ once: true }}
                transition={{ duration: 1.2, ease: "easeOut", delay: 0.4 }}
              />
            </div>
            <span className="bento-card__xp-label">Level 12 · 7,200 XP</span>
          </div>
        </motion.div>

        {/* API */}
        <motion.div
          className="bento-card bento-card--wide"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3, duration: 0.8 }}
        >
          <div className="bento-card__eyebrow"><Cpu size={14} /> API & MCP</div>
          <h3 className="bento-card__title">Build anything on top of Nexus.</h3>
          <div className="bento-card__code">
            <pre>{`const nexus = new NexusAI({ apiKey: process.env.NEXUS_KEY });
const video = await nexus.generate({
  agent: "aria",
  prompt: "Cinematic product reveal, neon noir",
  quality: "4k", duration: 8
});`}</pre>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// ─── PRICING ────────────────────────────────────────────────────────────────

function Pricing() {
  const [annual, setAnnual] = useState(true);

  return (
    <section className="pricing" id="pricing">
      <div className="section-header">
        <motion.span className="section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <Infinity size={13} /> PRICING
        </motion.span>
        <motion.h2 className="section-title" initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }}>
          Simple, honest pricing.
        </motion.h2>

        {/* Toggle */}
        <div className="pricing__toggle">
          <span className={!annual ? "pricing__toggle-label--active" : ""}>Monthly</span>
          <button
            className={`pricing__switch ${annual ? "pricing__switch--on" : ""}`}
            onClick={() => setAnnual(!annual)}
          >
            <motion.div className="pricing__switch-thumb" layout />
          </button>
          <span className={annual ? "pricing__toggle-label--active" : ""}>Annual <span className="pricing__save">Save 30%</span></span>
        </div>
      </div>

      <div className="pricing__grid">
        {PRICING.map((plan, i) => (
          <motion.div
            key={plan.name}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1, duration: 0.7 }}
            className={`pricing-card ${plan.highlight ? "pricing-card--highlight" : ""}`}
          >
            {plan.highlight && <div className="pricing-card__popular">Most popular</div>}
            <div className="pricing-card__name">{plan.name}</div>
            <div className="pricing-card__price">
              {plan.price
                ? <><span className="pricing-card__currency">$</span>{annual ? Math.round(plan.price * 0.7) : plan.price}<span className="pricing-card__period">/mo</span></>
                : <span className="pricing-card__custom">Custom</span>
              }
            </div>
            <p className="pricing-card__desc">{plan.desc}</p>
            <a href="#" className={`pricing-card__cta ${plan.highlight ? "pricing-card__cta--highlight" : ""}`}>
              {plan.cta} <ArrowRight size={14} />
            </a>
            <ul className="pricing-card__features">
              {plan.features.map(f => (
                <li key={f}>
                  <CheckCircle2 size={14} />
                  {f}
                </li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

// ─── TESTIMONIALS ────────────────────────────────────────────────────────────

const TESTIMONIALS = [
  { name: "Sofia Chen", role: "Founder @ NovaBrand", text: "Nexus replaced our entire creative department. We generate campaign assets in seconds that used to take 3 weeks.", stars: 5 },
  { name: "Marcus Webb", role: "Head of Content, Stripe", text: "The agents are scarily good. Aria produced a product video better than anything our agency made at 10x the cost.", stars: 5 },
  { name: "Priya Nair", role: "Solo creator, 2.1M followers", text: "I went from 3 videos a month to 60. My engagement is up 380%. Nexus is the unfair advantage I needed.", stars: 5 },
  { name: "Lucas Ferreira", role: "CMO @ ShopCloud", text: "Our whole team is 2 people now. Nexus handles everything else. This is how startups should operate in 2026.", stars: 5 },
  { name: "Aiko Tanaka", role: "Video Director", text: "The Cinema Engine is unreal — Hollywood-grade visuals, 8 seconds, no renders. I feel like I have a GPU farm in my browser.", stars: 5 },
  { name: "James Oduya", role: "Growth Lead, Linear", text: "We shipped 3 full ad campaigns in one afternoon. Our CPM dropped 42%. Nexus pays for itself in day one.", stars: 5 },
];

function Testimonials() {
  const trackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!trackRef.current) return;
    const track = trackRef.current;
    let pos = 0;
    const speed = 0.5;
    const total = track.scrollWidth / 2;
    let raf: number;
    const animate = () => {
      pos += speed;
      if (pos >= total) pos = 0;
      track.style.transform = `translateX(-${pos}px)`;
      raf = requestAnimationFrame(animate);
    };
    raf = requestAnimationFrame(animate);
    const pause = () => cancelAnimationFrame(raf);
    const resume = () => { raf = requestAnimationFrame(animate); };
    track.addEventListener("mouseenter", pause);
    track.addEventListener("mouseleave", resume);
    return () => {
      cancelAnimationFrame(raf);
      track.removeEventListener("mouseenter", pause);
      track.removeEventListener("mouseleave", resume);
    };
  }, []);

  return (
    <section className="testimonials">
      <div className="section-header">
        <motion.span className="section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <Star size={13} /> TESTIMONIALS
        </motion.span>
        <motion.h2 className="section-title" initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }}>
          Creators love Nexus.
        </motion.h2>
      </div>
      <div className="testimonials__track-wrap">
        <div ref={trackRef} className="testimonials__track">
          {[...TESTIMONIALS, ...TESTIMONIALS].map((t, i) => (
            <div key={i} className="testimonial-card">
              <div className="testimonial-card__stars">
                {Array.from({length: t.stars}).map((_,j) => <Star key={j} size={11} fill="currentColor" />)}
              </div>
              <p className="testimonial-card__text">&ldquo;{t.text}&rdquo;</p>
              <div className="testimonial-card__author">
                <div className="testimonial-card__avatar" style={{ background: AGENTS[i % 8].color }} />
                <div>
                  <div className="testimonial-card__name">{t.name}</div>
                  <div className="testimonial-card__role">{t.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── FINAL CTA ───────────────────────────────────────────────────────────────

function FinalCTA() {
  return (
    <section className="final-cta">
      <div className="final-cta__glow" />
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.9, ease: [0.16,1,0.3,1] }}
        className="final-cta__inner"
      >
        <span className="final-cta__eyebrow"><Rocket size={14} /> GET STARTED TODAY</span>
        <h2 className="final-cta__title">
          The future of creative<br />work starts now.
        </h2>
        <p className="final-cta__sub">
          Free 14-day trial · No credit card · Cancel anytime
        </p>
        <div id="about" className="final-cta__buttons">
          <a href="#" className="hero__cta-primary">
            <Sparkles size={16} />
            Start for free
            <span className="hero__cta-glow" />
          </a>
          <a href="#" className="hero__cta-secondary">
            Book a demo <ChevronRight size={14} />
          </a>
        </div>
      </motion.div>
    </section>
  );
}

// ─── FOOTER ──────────────────────────────────────────────────────────────────

function Footer() {
  const cols = [
    { title: "Company",    links: [["About","/about"],["Blog","/blog"],["Contact","/support-request"]] },
    { title: "Legal",      links: [["Terms","/terms-of-service"],["Privacy","/privacy-policy"],["Cookies","/cookies"]] },
  ];
  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__brand">
          <a href="#" className="nav__logo">
            <span className="nav__logo-mark">◈</span>
            <span className="nav__logo-text">NEXUS</span>
            <span className="nav__logo-tag">AI</span>
          </a>
          <p className="footer__tagline">The creative supercomputer<br />for the world&apos;s best teams.</p>
        </div>

        {cols.map(col => (
          <div key={col.title} className="footer__col">
            <div className="footer__col-title">{col.title}</div>
            {col.links.map(([label, href]) => (
              <a key={label} href={href} className="footer__link">{label}</a>
            ))}
          </div>
        ))}
      </div>
      <div className="footer__bottom">
        <span>© 2026 Nexus AI Inc. All rights reserved.</span>
        <span>Made with ◈ by the Nexus team</span>
      </div>
    </footer>
  );
}

// ─── AUDIO AMBIENT ───────────────────────────────────────────────────────────

function useAmbientAudio(muted: boolean) {
  const ctxRef = useRef<AudioContext | null>(null);
  const gainRef = useRef<GainNode | null>(null);
  const startedRef = useRef(false);

  const start = useCallback(() => {
    if (startedRef.current || typeof window === "undefined") return;
    startedRef.current = true;
    const ctx = new AudioContext();
    ctxRef.current = ctx;
    const gain = ctx.createGain();
    gain.gain.value = muted ? 0 : 0.06;
    gainRef.current = gain;
    gain.connect(ctx.destination);

    // Simple pads using oscillators
    [[55, 0],[82.5, 0.3],[110, 0.6],[165, 1]].forEach(([freq, delay]) => {
      const osc = ctx.createOscillator();
      const oscGain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = freq;
      oscGain.gain.value = 0.3;
      osc.connect(oscGain);
      oscGain.connect(gain);
      osc.start(ctx.currentTime + delay);
    });
  }, [muted]);

  useEffect(() => {
    if (gainRef.current) {
      gainRef.current.gain.setTargetAtTime(muted ? 0 : 0.06, ctxRef.current!.currentTime, 0.5);
    }
  }, [muted]);

  return start;
}

// ─── ROOT ────────────────────────────────────────────────────────────────────

export default function Page() {
  const [cookieConsentVisible, setCookieConsentVisible] = useState(false);

  useEffect(() => {
    try {
      const savedConsent = window.localStorage.getItem("nexus_cookie_consent");
      setCookieConsentVisible(savedConsent !== "accepted");
    } catch {
      setCookieConsentVisible(true);
    }
  }, []);

  function acceptCookieConsent() {
    try {
      window.localStorage.setItem("nexus_cookie_consent", "accepted");
    } catch {}
    setCookieConsentVisible(false);
  }


  const [muted, setMuted] = useState(true);
  const startAudio = useAmbientAudio(muted);

  const handleToggleAudio = () => {
    setMuted(m => !m);
    startAudio();
  };

  return (
    <>
      <style>{CSS}</style>
      <CursorGlow />
      <NoiseTexture />
      <Nav muted={muted} onToggleAudio={handleToggleAudio} />
      <main>
        <Hero />
        <Marquee />
        <StatsStrip />
        <AgentsGrid />
        <Studio />
        <FeatureBento />
        <Testimonials />
        <Pricing />
        <FinalCTA />
      
      {cookieConsentVisible ? (
        <div className="cookieConsent" role="dialog" aria-label="Cookie notice">
          <div>
            <strong>Cookies help us run Nexus AI properly.</strong>
            <p>
              We use essential cookies for login, workspace security, billing flow continuity,
              preferences, and performance. You can read more in our Cookie Policy.
            </p>
          </div>
          <div className="cookieConsent__actions">
            <a href="/cookies">Cookie Policy</a>
            <button type="button" onClick={acceptCookieConsent}>Accept cookies</button>
          </div>
        </div>
      ) : null}

    </main>
      <Footer />
    </>
  );
}

// ─── CSS ─────────────────────────────────────────────────────────────────────

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #060608;
    --bg-2: #0c0c10;
    --bg-3: #111116;
    --surface: #16161c;
    --surface-2: #1e1e26;
    --border: rgba(255,255,255,0.07);
    --border-2: rgba(255,255,255,0.12);
    --text: #f0f0f4;
    --text-2: #9494a8;
    --text-3: #5a5a72;
    --accent: #7C6AF7;
    --accent-2: #4ECDC4;
    --accent-3: #FF6B6B;
    --amber: #F59E0B;
    --font-display: 'Syne', sans-serif;
    --font-body: 'DM Sans', sans-serif;
    --radius: 16px;
    --radius-sm: 10px;
    --radius-lg: 24px;
  }

  html { scroll-behavior: smooth; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-body);
    font-size: 16px;
    line-height: 1.6;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
  }

  /* Cursor glow */
  .cursor-glow {
    position: fixed;
    top: 0; left: 0;
    width: 400px; height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(124,106,247,0.12) 0%, transparent 70%);
    pointer-events: none;
    z-index: 9999;
    mix-blend-mode: screen;
  }

  /* Noise overlay */
  .noise-overlay {
    position: fixed;
    inset: 0;
    z-index: 9998;
    pointer-events: none;
    opacity: 0.025;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 200px 200px;
  }

  /* ── NAV ── */
  .nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 1000;
    padding: 0 24px;
    transition: background 0.4s, border-color 0.4s, backdrop-filter 0.4s;
    border-bottom: 1px solid transparent;
  }
  .nav--scrolled {
    background: rgba(6,6,8,0.85);
    backdrop-filter: blur(20px) saturate(1.5);
    border-color: var(--border);
  }
  .nav__inner {
    max-width: 1280px;
    margin: 0 auto;
    height: 68px;
    display: flex;
    align-items: center;
    gap: 32px;
  }
  .nav__logo {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    flex-shrink: 0;
  }
  .nav__logo-mark {
    font-size: 22px;
    color: var(--accent);
    line-height: 1;
  }
  .nav__logo-text {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: 0.08em;
  }
  .nav__logo-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    border: 1px solid var(--border-2);
    border-radius: 4px;
    padding: 1px 5px;
  }
  .nav__links {
    display: flex;
    gap: 4px;
    margin-left: auto;
  }
  .nav__link {
    padding: 6px 14px;
    border-radius: 8px;
    color: var(--text-2);
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: color 0.2s, background 0.2s;
  }
  .nav__link:hover { color: var(--text); background: var(--surface); }
  .nav__actions { display: flex; align-items: center; gap: 10px; }
  .nav__audio {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    width: 34px; height: 34px;
    display: flex; align-items: center; justify-content: center;
    color: var(--text-2);
    cursor: pointer;
    transition: color 0.2s, border-color 0.2s;
  }
  .nav__audio:hover { color: var(--text); border-color: var(--border-2); }
  .nav__btn-ghost {
    padding: 7px 16px;
    border-radius: 8px;
    color: var(--text-2);
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: color 0.2s;
  }
  .nav__btn-ghost:hover { color: var(--text); }
  .nav__btn-primary {
    display: flex; align-items: center; gap: 6px;
    padding: 8px 18px;
    background: linear-gradient(135deg, var(--accent), #5b4de0);
    color: #fff;
    border-radius: 9px;
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
    transition: opacity 0.2s, transform 0.2s;
    box-shadow: 0 0 24px rgba(124,106,247,0.3);
  }
  .nav__btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }
  .nav__hamburger {
    display: none;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    width: 36px; height: 36px;
    align-items: center; justify-content: center;
    color: var(--text);
    cursor: pointer;
  }
  .nav__mobile {
    display: flex;
    flex-direction: column;
    padding: 16px 0 20px;
    border-top: 1px solid var(--border);
    overflow: hidden;
  }
  .nav__mobile-link {
    padding: 12px 4px;
    color: var(--text-2);
    text-decoration: none;
    font-size: 16px;
    font-weight: 500;
    border-bottom: 1px solid var(--border);
    transition: color 0.2s;
  }
  .nav__mobile-link:hover { color: var(--text); }
  .nav__btn-primary--mobile {
    margin-top: 16px;
    text-align: center;
    justify-content: center;
  }
  @media (max-width: 900px) {
    .nav__links { display: none; }
    .nav__btn-ghost { display: none; }
    .nav__hamburger { display: flex; }
  }

  /* ── HERO ── */
  .hero {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 0 24px;
  }
  .hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse 80% 60% at 50% 40%, rgba(124,106,247,0.12) 0%, transparent 70%),
      radial-gradient(ellipse 50% 40% at 80% 60%, rgba(78,205,196,0.06) 0%, transparent 60%),
      radial-gradient(ellipse 40% 30% at 20% 70%, rgba(255,107,107,0.05) 0%, transparent 60%);
  }
  .hero__canvas {
    position: absolute;
    inset: 0;
    z-index: 0;
  }
  .hero__content {
    position: relative;
    z-index: 10;
    text-align: center;
    max-width: 860px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 80px;
  }
  .hero__badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: rgba(124,106,247,0.1);
    border: 1px solid rgba(124,106,247,0.3);
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.04em;
    margin-bottom: 28px;
  }
  .hero__badge-new {
    background: var(--accent);
    color: #fff;
    font-size: 9px;
    padding: 1px 5px;
    border-radius: 4px;
    letter-spacing: 0.08em;
  }
  .hero__headline {
    font-family: var(--font-display);
    font-size: clamp(42px, 7vw, 88px);
    font-weight: 800;
    line-height: 1.04;
    letter-spacing: -0.03em;
    color: var(--text);
    margin-bottom: 24px;
  }
  .hero__subline {
    font-size: clamp(17px, 2.2vw, 22px);
    color: var(--text-2);
    line-height: 1.55;
    max-width: 600px;
    margin-bottom: 40px;
  }
  .hero__br { display: block; }
  .typewriter { display: inline; }
  .typewriter__text {
    color: var(--accent);
    font-weight: 600;
  }
  .typewriter__cursor {
    color: var(--accent);
    animation: blink 1s step-end infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

  .hero__cta-row {
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 44px;
  }
  .hero__cta-primary {
    position: relative;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 14px 30px;
    background: linear-gradient(135deg, var(--accent) 0%, #5b4de0 100%);
    color: #fff;
    border-radius: 12px;
    text-decoration: none;
    font-size: 15px;
    font-weight: 700;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(124,106,247,0.4), 0 4px 24px rgba(0,0,0,0.4);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .hero__cta-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 60px rgba(124,106,247,0.55), 0 8px 32px rgba(0,0,0,0.4);
  }
  .hero__cta-glow {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 60%);
  }
  .hero__cta-secondary {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 13px 24px;
    background: var(--surface);
    border: 1px solid var(--border-2);
    color: var(--text);
    border-radius: 12px;
    text-decoration: none;
    font-size: 15px;
    font-weight: 600;
    transition: border-color 0.2s, background 0.2s;
  }
  .hero__cta-secondary:hover { background: var(--surface-2); border-color: rgba(255,255,255,0.2); }

  .hero__trust {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .hero__avatars { display: flex; }
  .hero__avatar {
    width: 28px; height: 28px;
    border-radius: 50%;
    border: 2px solid var(--bg);
    margin-left: -8px;
    first-child { margin-left: 0; }
  }
  .hero__trust-text {
    font-size: 14px;
    color: var(--text-2);
  }
  .hero__trust-text strong { color: var(--text); }
  .hero__stars {
    display: flex;
    align-items: center;
    gap: 3px;
    color: var(--amber);
    font-size: 12px;
    font-weight: 700;
  }
  .hero__scroll-hint {
    position: absolute;
    bottom: 28px;
    left: 50%;
    transform: translateX(-50%);
    color: var(--text-3);
    z-index: 10;
  }

  /* ── MARQUEE ── */
  .marquee-wrap {
    overflow: hidden;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    background: var(--bg-2);
    padding: 16px 0;
    mask-image: linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%);
  }
  .marquee-track {
    display: flex;
    width: max-content;
    animation: marquee 28s linear infinite;
  }
  .marquee-item {
    padding: 0 36px;
    font-family: var(--font-display);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--text-3);
    text-transform: uppercase;
    white-space: nowrap;
  }
  @keyframes marquee { from { transform: translateX(0) } to { transform: translateX(-50%) } }

  /* ── STATS STRIP ── */
  .stats-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
  }
  .stats-strip__item {
    background: var(--bg);
    padding: 36px 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    text-align: center;
    transition: background 0.2s;
  }
  .stats-strip__item:hover { background: var(--bg-2); }
  .stats-strip__icon { color: var(--accent); }
  .stats-strip__value {
    font-family: var(--font-display);
    font-size: 36px;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
  }
  .stats-strip__label {
    font-size: 13px;
    color: var(--text-2);
    font-weight: 500;
  }
  @media (max-width: 700px) {
    .stats-strip { grid-template-columns: repeat(2, 1fr); }
  }

  /* ── SECTIONS ── */
  .section-header {
    text-align: center;
    max-width: 720px;
    margin: 0 auto 64px;
  }
  .section-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 16px;
    border: 1px solid rgba(124,106,247,0.25);
    padding: 5px 12px;
    border-radius: 100px;
    background: rgba(124,106,247,0.06);
  }
  .section-title {
    font-family: var(--font-display);
    font-size: clamp(34px, 5vw, 58px);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.025em;
    color: var(--text);
    margin-bottom: 18px;
  }
  .section-subtitle {
    font-size: 18px;
    color: var(--text-2);
    line-height: 1.6;
  }

  /* ── AGENTS ── */
  .agents {
    padding: 120px 24px;
    max-width: 1280px;
    margin: 0 auto;
  }
  .agents__grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }
  .agent-card {
    position: relative;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    cursor: pointer;
    overflow: hidden;
    transition: border-color 0.3s, transform 0.3s;
  }
  .agent-card:hover, .agent-card--active {
    border-color: var(--agent-color);
    transform: translateY(-4px);
  }
  .agent-card__glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at top left, color-mix(in srgb, var(--agent-color) 10%, transparent) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.4s;
  }
  .agent-card:hover .agent-card__glow,
  .agent-card--active .agent-card__glow { opacity: 1; }

  .agent-card__icon-wrap {
    width: 44px; height: 44px;
    border-radius: 12px;
    background: color-mix(in srgb, var(--agent-color) 15%, transparent);
    border: 1px solid color-mix(in srgb, var(--agent-color) 30%, transparent);
    display: flex; align-items: center; justify-content: center;
    color: var(--agent-color);
    margin-bottom: 16px;
  }
  .agent-card__name {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 2px;
  }
  .agent-card__role {
    font-size: 12px;
    font-weight: 600;
    color: var(--agent-color);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .agent-card__specialty {
    font-size: 13px;
    color: var(--text-2);
    margin-bottom: 16px;
  }
  .agent-card__stat {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-3);
    padding: 6px 10px;
    background: var(--bg-2);
    border-radius: 8px;
    border: 1px solid var(--border);
  }
  .agent-card__stat svg { color: var(--agent-color); }
  .agent-card__status {
    display: flex;
    align-items: center;
    gap: 6px;
    position: absolute;
    top: 16px; right: 16px;
    font-size: 11px;
    color: var(--text-3);
    font-weight: 600;
  }
  .agent-card__dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 6px #10B981;
    animation: pulse-dot 2s ease-in-out infinite;
  }
  @keyframes pulse-dot {
    0%,100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(1.3); }
  }
  .agents__cta {
    text-align: center;
    margin-top: 48px;
  }
  .btn-outline {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    border: 1px solid var(--border-2);
    border-radius: 10px;
    color: var(--text-2);
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
    transition: color 0.2s, border-color 0.2s, background 0.2s;
  }
  .btn-outline:hover { color: var(--text); border-color: rgba(255,255,255,0.25); background: var(--surface); }
  @media (max-width: 900px) {
    .agents__grid { grid-template-columns: repeat(2, 1fr); }
  }
  @media (max-width: 540px) {
    .agents__grid { grid-template-columns: 1fr; }
  }

  /* ── STUDIO ── */
  .studio {
    padding: 120px 24px;
    max-width: 1280px;
    margin: 0 auto;
  }
  .studio__tabs {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-bottom: 40px;
  }
  .studio__tab {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 9px 20px;
    border-radius: 10px;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-2);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  .studio__tab--active {
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
    box-shadow: 0 0 20px rgba(124,106,247,0.35);
  }
  .studio__grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    min-height: 200px;
    margin-bottom: 48px;
  }
  .preset-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text-2);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: all 0.2s;
    font-family: var(--font-display);
  }
  .preset-chip:hover, .preset-chip--active {
    background: var(--surface-2);
    border-color: var(--border-2);
    color: var(--text);
    transform: translateY(-2px);
  }
  .preset-chip--active {
    border-color: var(--accent);
    box-shadow: 0 0 16px rgba(124,106,247,0.2);
  }
  .preset-chip__hot { font-size: 14px; }
  .preset-chip__tag {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    background: var(--bg-2);
    border: 1px solid var(--border);
    color: var(--text-3);
    font-weight: 700;
    letter-spacing: 0.08em;
  }

  .studio__prompt-box {
    max-width: 800px;
    margin: 0 auto;
    background: var(--surface);
    border: 1px solid var(--border-2);
    border-radius: var(--radius-lg);
    padding: 28px;
  }
  .studio__prompt-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 16px;
  }
  .studio__prompt-input-row {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }
  .studio__prompt-input {
    flex: 1;
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    color: var(--text-2);
    font-size: 14px;
    font-family: var(--font-body);
    outline: none;
    transition: border-color 0.2s;
  }
  .studio__prompt-input:focus { border-color: var(--border-2); color: var(--text); }
  .studio__prompt-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 22px;
    background: linear-gradient(135deg, var(--accent), #5b4de0);
    color: #fff;
    border-radius: 10px;
    border: none;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
    box-shadow: 0 0 24px rgba(124,106,247,0.3);
    transition: opacity 0.2s, transform 0.2s;
  }
  .studio__prompt-btn:hover { opacity: 0.9; transform: translateY(-1px); }
  .studio__prompt-modes {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .studio__mode-tag {
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 6px;
    background: var(--bg-2);
    border: 1px solid var(--border);
    color: var(--text-3);
    font-weight: 600;
  }

  /* ── BENTO ── */
  .bento {
    padding: 120px 24px;
    max-width: 1280px;
    margin: 0 auto;
  }
  .bento__grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto auto;
    gap: 16px;
  }
  .bento-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 32px;
    overflow: hidden;
    position: relative;
    transition: border-color 0.3s, transform 0.3s;
  }
  .bento-card:hover { border-color: var(--border-2); transform: translateY(-3px); }
  .bento-card--xl {
    grid-column: span 2;
    min-height: 360px;
  }
  .bento-card--md { min-height: 280px; }
  .bento-card--sm { min-height: 220px; }
  .bento-card--wide {
    grid-column: span 2;
  }
  .bento-card--accent-purple {
    border-color: rgba(124,106,247,0.2);
    background: linear-gradient(135deg, rgba(124,106,247,0.05) 0%, var(--surface) 100%);
  }
  .bento-card--accent-teal {
    border-color: rgba(78,205,196,0.2);
    background: linear-gradient(135deg, rgba(78,205,196,0.05) 0%, var(--surface) 100%);
  }
  .bento-card--accent-amber {
    border-color: rgba(245,158,11,0.2);
    background: linear-gradient(135deg, rgba(245,158,11,0.05) 0%, var(--surface) 100%);
  }
  .bento-card__eyebrow {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 16px;
  }
  .bento-card__title {
    font-family: var(--font-display);
    font-size: 24px;
    font-weight: 700;
    line-height: 1.2;
    color: var(--text);
    margin-bottom: 12px;
  }
  .bento-card__body {
    font-size: 14px;
    color: var(--text-2);
    line-height: 1.6;
  }

  .bento-card__visual--grid {
    position: absolute;
    bottom: 24px; right: 24px;
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 8px;
    width: 200px;
  }
  .bento-card__dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
  }

  .bento-card__pulse {
    position: absolute;
    bottom: 24px; right: 24px;
    display: flex; align-items: center; justify-content: center;
    width: 80px; height: 80px;
  }
  .bento-card__pulse-ring {
    position: absolute;
    width: 80px; height: 80px;
    border-radius: 50%;
    border: 2px solid rgba(124,106,247,0.3);
    animation: pulse-ring 2.5s ease-out infinite;
  }
  .bento-card__pulse-ring--2 { animation-delay: 1.25s; }
  @keyframes pulse-ring {
    0% { transform: scale(0.6); opacity: 1; }
    100% { transform: scale(1.4); opacity: 0; }
  }
  .bento-card__pulse-icon { color: var(--accent); position: relative; z-index: 1; }

  .bento-card__meter {
    margin-top: 24px;
    position: relative;
  }
  .bento-card__meter::before {
    content: '';
    display: block;
    height: 6px;
    background: var(--bg-2);
    border-radius: 100px;
  }
  .bento-card__meter-fill {
    position: absolute;
    top: 0; left: 0;
    height: 6px;
    background: linear-gradient(90deg, var(--accent-2), #3b82f6);
    border-radius: 100px;
  }
  .bento-card__meter-label {
    display: block;
    font-size: 12px;
    color: var(--text-3);
    margin-top: 8px;
  }

  .bento-card__integrations {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;
  }
  .bento-card__badge {
    padding: 4px 10px;
    border-radius: 6px;
    background: var(--bg-2);
    border: 1px solid var(--border);
    font-size: 12px;
    color: var(--text-2);
    font-weight: 600;
  }

  .bento-card__xp { margin-top: 16px; }
  .bento-card__xp-bar {
    height: 8px;
    background: var(--bg-2);
    border-radius: 100px;
    position: relative;
    overflow: hidden;
  }
  .bento-card__xp-fill {
    position: absolute;
    top: 0; left: 0;
    height: 100%;
    background: linear-gradient(90deg, var(--amber), #f97316);
    border-radius: 100px;
  }
  .bento-card__xp-label {
    display: block;
    font-size: 12px;
    color: var(--amber);
    font-weight: 700;
    margin-top: 8px;
  }

  .bento-card__code {
    margin-top: 20px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    font-size: 12px;
    color: var(--accent-2);
    font-family: 'Fira Code', monospace;
    line-height: 1.7;
    overflow-x: auto;
  }

  @media (max-width: 900px) {
    .bento__grid { grid-template-columns: 1fr; }
    .bento-card--xl, .bento-card--wide { grid-column: span 1; }
  }

  /* ── TESTIMONIALS ── */
  .testimonials {
    padding: 120px 0;
    overflow: hidden;
  }
  .testimonials .section-header { padding: 0 24px; }
  .testimonials__track-wrap {
    overflow: hidden;
    mask-image: linear-gradient(to right, transparent 0%, black 8%, black 92%, transparent 100%);
  }
  .testimonials__track {
    display: flex;
    gap: 16px;
    width: max-content;
    padding: 8px 24px;
  }
  .testimonial-card {
    width: 340px;
    flex-shrink: 0;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px;
    transition: border-color 0.3s;
  }
  .testimonial-card:hover { border-color: var(--border-2); }
  .testimonial-card__stars {
    display: flex;
    gap: 3px;
    color: var(--amber);
    margin-bottom: 14px;
  }
  .testimonial-card__text {
    font-size: 14px;
    color: var(--text-2);
    line-height: 1.65;
    margin-bottom: 20px;
  }
  .testimonial-card__author {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .testimonial-card__avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .testimonial-card__name {
    font-weight: 700;
    font-size: 14px;
    color: var(--text);
  }
  .testimonial-card__role {
    font-size: 12px;
    color: var(--text-3);
  }

  /* ── PRICING ── */
  .pricing {
    padding: 120px 24px;
    max-width: 1100px;
    margin: 0 auto;
  }
  .pricing__toggle {
    display: flex;
    align-items: center;
    gap: 14px;
    justify-content: center;
    margin-top: 24px;
    font-size: 14px;
    color: var(--text-2);
    font-weight: 600;
  }
  .pricing__toggle-label--active { color: var(--text); }
  .pricing__switch {
    width: 52px; height: 28px;
    border-radius: 100px;
    background: var(--surface-2);
    border: 1px solid var(--border-2);
    position: relative;
    cursor: pointer;
    display: flex; align-items: center;
    padding: 3px;
  }
  .pricing__switch--on { background: var(--accent); border-color: var(--accent); }
  .pricing__switch-thumb {
    width: 20px; height: 20px;
    border-radius: 50%;
    background: #fff;
    margin-left: auto;
  }
  .pricing__switch--on .pricing__switch-thumb { margin-left: 0; margin-right: auto; }
  /* Fix: use framer-motion layout for thumb */
  .pricing__switch-thumb {
    position: absolute;
    right: 4px;
    transition: right 0.3s;
  }
  .pricing__switch--on .pricing__switch-thumb {
    right: auto;
    left: 4px;
  }
  .pricing__save {
    background: linear-gradient(135deg, #10B981, #059669);
    color: #fff;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 700;
    margin-left: 4px;
  }

  .pricing__grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 48px;
  }
  .pricing-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 36px;
    position: relative;
    transition: border-color 0.3s, transform 0.3s;
  }
  .pricing-card:hover { transform: translateY(-4px); }
  .pricing-card--highlight {
    border-color: var(--accent);
    background: linear-gradient(160deg, rgba(124,106,247,0.08) 0%, var(--surface) 100%);
    box-shadow: 0 0 60px rgba(124,106,247,0.15);
  }
  .pricing-card__popular {
    position: absolute;
    top: -1px; left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, var(--accent), #5b4de0);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 0 0 10px 10px;
    letter-spacing: 0.08em;
  }
  .pricing-card__name {
    font-family: var(--font-display);
    font-size: 16px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 12px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
  .pricing-card__price {
    font-family: var(--font-display);
    font-size: 52px;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
    margin-bottom: 12px;
    display: flex;
    align-items: flex-start;
    gap: 4px;
  }
  .pricing-card__currency {
    font-size: 22px;
    margin-top: 8px;
    color: var(--text-2);
  }
  .pricing-card__period {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-3);
    align-self: flex-end;
    margin-bottom: 6px;
  }
  .pricing-card__custom {
    font-size: 36px;
    color: var(--text);
  }
  .pricing-card__desc {
    font-size: 14px;
    color: var(--text-2);
    margin-bottom: 24px;
    line-height: 1.6;
  }
  .pricing-card__cta {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 20px;
    border-radius: 10px;
    text-decoration: none;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 28px;
    background: var(--surface-2);
    border: 1px solid var(--border-2);
    color: var(--text);
    transition: all 0.2s;
  }
  .pricing-card__cta:hover { background: var(--bg-3); }
  .pricing-card__cta--highlight {
    background: linear-gradient(135deg, var(--accent), #5b4de0);
    border-color: transparent;
    color: #fff;
    box-shadow: 0 0 30px rgba(124,106,247,0.3);
  }
  .pricing-card__cta--highlight:hover { opacity: 0.9; }
  .pricing-card__features {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .pricing-card__features li {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    color: var(--text-2);
  }
  .pricing-card__features li svg { color: var(--accent-2); flex-shrink: 0; }
  @media (max-width: 860px) {
    .pricing__grid { grid-template-columns: 1fr; max-width: 420px; margin-left: auto; margin-right: auto; }
  }

  /* ── FINAL CTA ── */
  .final-cta {
    padding: 160px 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .final-cta__glow {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse 70% 50% at 50% 50%, rgba(124,106,247,0.12) 0%, transparent 70%);
    pointer-events: none;
  }
  .final-cta__inner { position: relative; z-index: 1; }
  .final-cta__eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 24px;
    border: 1px solid rgba(124,106,247,0.25);
    padding: 6px 14px;
    border-radius: 100px;
    background: rgba(124,106,247,0.06);
  }
  .final-cta__title {
    font-family: var(--font-display);
    font-size: clamp(38px, 6vw, 72px);
    font-weight: 800;
    line-height: 1.06;
    letter-spacing: -0.03em;
    color: var(--text);
    margin-bottom: 20px;
  }
  .final-cta__sub {
    font-size: 16px;
    color: var(--text-3);
    margin-bottom: 44px;
  }
  .final-cta__buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
  }

  /* ── FOOTER ── */
  .footer {
    border-top: 1px solid var(--border);
    padding: 80px 24px 40px;
    background: var(--bg-2);
  }
  .footer__inner {
    max-width: 1280px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
    gap: 40px;
    margin-bottom: 60px;
  }
  .footer__brand {}
  .footer__tagline {
    font-size: 14px;
    color: var(--text-3);
    line-height: 1.6;
    margin: 16px 0 24px;
  }
  .footer__social {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
  .footer__social-link {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-3);
    text-decoration: none;
    transition: color 0.2s;
  }
  .footer__social-link:hover { color: var(--text); }
  .footer__col {}
  .footer__col-title {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text);
    margin-bottom: 20px;
  }
  .footer__link {
    display: block;
    font-size: 14px;
    color: var(--text-3);
    text-decoration: none;
    margin-bottom: 12px;
    transition: color 0.2s;
  }
  .footer__link:hover { color: var(--text-2); }
  .footer__bottom {
    max-width: 1280px;
    margin: 0 auto;
    padding-top: 28px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: var(--text-3);
    flex-wrap: wrap;
    gap: 12px;
  }
  @media (max-width: 900px) {
    .footer__inner { grid-template-columns: 1fr 1fr; }
    .footer__brand { grid-column: span 2; }
  }
  @media (max-width: 540px) {
    .footer__inner { grid-template-columns: 1fr; }
    .footer__brand { grid-column: span 1; }
  }
  .cookieConsent {
    position: fixed;
    left: 24px;
    right: 24px;
    bottom: 24px;
    z-index: 9999;
    max-width: 980px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    padding: 18px 20px;
    border-radius: 22px;
    border: 1px solid rgba(165, 180, 252, 0.28);
    background: linear-gradient(180deg, rgba(8, 13, 28, 0.96), rgba(3, 7, 18, 0.98));
    box-shadow: 0 28px 90px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255,255,255,0.08);
    backdrop-filter: blur(22px) saturate(150%);
    -webkit-backdrop-filter: blur(22px) saturate(150%);
    color: #f8fafc;
  }

  .cookieConsent strong {
    display: block;
    font-size: 15px;
    font-weight: 950;
    margin-bottom: 5px;
  }

  .cookieConsent p {
    margin: 0;
    color: #94a3b8;
    font-size: 13px;
    line-height: 1.45;
    max-width: 680px;
  }

  .cookieConsent__actions {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }

  .cookieConsent__actions a {
    color: #c7d2fe;
    font-size: 13px;
    font-weight: 850;
    text-decoration: none;
  }

  .cookieConsent__actions button {
    border: 0;
    border-radius: 14px;
    padding: 11px 14px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: #ffffff;
    font-weight: 950;
    cursor: pointer;
    box-shadow: 0 16px 34px rgba(79, 70, 229, 0.32);
  }

  @media (max-width: 720px) {
    .cookieConsent {
      align-items: flex-start;
      flex-direction: column;
    }

    .cookieConsent__actions {
      width: 100%;
      justify-content: space-between;
    }
  }

`;
