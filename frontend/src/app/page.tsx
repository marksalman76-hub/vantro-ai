"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { Canvas } from "@react-three/fiber";
import { Float, MeshDistortMaterial, OrbitControls, Stars } from "@react-three/drei";
import { Sparkles, ShieldCheck, Workflow, WandSparkles } from "lucide-react";
import PremiumHeroMedia from "@/components/media/PremiumHeroMedia";

import Link from "next/link";

const ticker = [
  "Strategy Agent",
  "Research Agent",
  "Creative Production Agent",
  "Brand Identity Agent",
  "Analytics Agent",
  "Operations Agent",
  "Customer Support Agent",
  "Content Agent",
  "Campaign Agent",
  "SEO Agent",
  "Outreach Agent",
  "Reporting Agent",
];

const agents = [
  ["Strategy Agent", "Produces market analysis, competitive positioning, and strategic recommendations.", "🧠", "#7C74FF"],
  ["Research Agent", "Market research, competitor analysis, trend mapping, and opportunity identification.", "🔬", "#0ECFBC"],
  ["Creative Agent", "Campaign concepts, copy, visual briefs, scripts, and creative strategies.", "🎨", "#F5C518"],
  ["Analytics Agent", "Interprets performance data and surfaces actionable optimisation opportunities.", "📊", "#4EACFF"],
  ["Operations Agent", "Streamlines workflows, produces SOPs, and improves operational efficiency.", "⚙️", "#FF6B9D"],
  ["Support Agent", "Handles customer interactions, escalation routing, and follow-up communication.", "💬", "#FF8C42"],
  ["Brand Agent", "Builds brand identity, tone of voice, messaging, and positioning systems.", "✨", "#9D97FF"],
  ["Growth Agent", "Drives SEO, outreach, pipeline growth, and conversion optimisation.", "🚀", "#0ECFBC"],
];

const plans = [
  ["Starter", "$99", "Activate your first agents and validate AI workforce value.", ["Up to 5 AI agents", "Core workflows", "Approval controls", "Output history"], "/signup?plan=starter"],
  ["Growth", "$279", "Full multi-agent deployment across key business functions.", ["Up to 20 AI agents", "Advanced workflows", "Priority execution", "Team seats"], "/signup?plan=growth"],
  ["Business", "$449", "Advanced automation with full analytics and premium support.", ["Up to 50 AI agents", "Advanced analytics", "Multi-department", "Premium support"], "/signup?plan=business"],
  ["Enterprise", "Custom", "White-label deployment, custom agent stacks, and dedicated onboarding.", ["Unlimited agents", "White-label", "Head + Orchestration agents", "Dedicated onboarding"], "/signup?plan=enterprise"],
];




function LandingSpotlightLayer() {
  return (
    <div className="landingSpotlightLayer" aria-hidden="true">
      <div className="spotlightBeam beamOne" />
      <div className="spotlightBeam beamTwo" />
      <div className="spotlightBeam beamThree" />
      <div className="ambientParticleField">
        {Array.from({ length: 34 }).map((_, index) => (
          <span key={index} style={{ ["--i" as any]: index }} />
        ))}
      </div>
    </div>
  );
}

function HeroVisualSystem() {
  return (
    <div className="heroVisualSystem" aria-hidden="true">
      <div className="heroGlassCard cardA">
        <strong>Product Research Agent</strong>
        <span>Analyses offers, market gaps and buyer intent.</span>
        <em>Live</em>
      </div>

      <div className="heroGlassCard cardB">
        <strong>Campaign Builder</strong>
        <span>Turns business context into launch-ready execution.</span>
        <em>Generating</em>
      </div>

      <div className="heroGlassCard cardC">
        <strong>Governed Approval</strong>
        <span>High-risk actions stay locked until owner approval.</span>
        <em>Protected</em>
      </div>

      <div className="heroGlassCard cardD">
        <strong>AI Workforce</strong>
        <span>Specialist agents coordinate across ecommerce tasks.</span>
        <em>24 active</em>
      </div>

      <div className="heroDashboardPreview">
        <div className="heroDashboardTop">
          <span />
          <span />
          <span />
        </div>
        <div className="heroDashboardBody">
          {[
            ["AI", "Store strategy", "Ready"],
            ["UGC", "Video brief", "Live"],
            ["SEO", "Growth actions", "Queued"],
          ].map(([icon, title, status]) => (
            <div className="heroMiniRow" key={title}>
              <div className="heroMiniIcon">{icon}</div>
              <div className="heroMiniText">
                <strong>{title}</strong>
                <span>Premium execution layer</span>
              </div>
              <div className="heroMiniStatus">{status}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="heroAgentRail">
        {["AI", "UGC", "SEO", "ADS", "CRM"].map((item) => (
          <div className="heroAgentDot" key={item}>{item}</div>
        ))}
      </div>
    </div>
  );
}

function PremiumHeroOrb() {
  return (
    <div className="heroOrb3d" aria-hidden="true">
      <Canvas camera={{ position: [0, 0, 4.2], fov: 46 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[3, 4, 5]} intensity={1.8} />
        <pointLight position={[-4, -2, 3]} intensity={0.8} color="#0ECFBC" />
        <Stars radius={42} depth={24} count={900} factor={3.4} saturation={0} fade speed={0.7} />
        <Float speed={2.2} rotationIntensity={1.1} floatIntensity={1.8}>
          <mesh>
            <sphereGeometry args={[1.25, 96, 96]} />
            <MeshDistortMaterial
              color="#7C74FF"
              emissive="#23195f"
              roughness={0.18}
              metalness={0.35}
              distort={0.34}
              speed={1.55}
            />
          </mesh>
        </Float>
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} />
      </Canvas>
    </div>
  );
}

function MotionBadge({ icon, title, body, delay }: { icon: React.ReactNode; title: string; body: string; delay: number }) {
  return (
    <motion.div
      className="motionBadge glassLift"
      initial={{ opacity: 0, y: 24, scale: 0.96 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, amount: 0.25 }}
      transition={{ duration: 0.62, delay, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -6, rotateX: 4, rotateY: -4 }}
    >
      <div className="motionBadgeIcon">{icon}</div>
      <div>
        <strong>{title}</strong>
        <span>{body}</span>
      </div>
    </motion.div>
  );
}

function LandingMotionRuntimeLayer() {
  return (
    <section className="motionRuntimeLayer">
      <motion.div
        className="motionRuntimeHeader"
        initial={{ opacity: 0, y: 26 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.28 }}
        transition={{ duration: 0.7 }}
      >
        <div className="runtimeEyebrow">Premium execution layer</div>
        <h2>Designed to feel like a live AI operating system, not a static SaaS page.</h2>
        <p>
          Animated workflow depth, glass panels, 3D motion, governed automation cues,
          and premium AI workforce storytelling for high-converting ecommerce clients.
        </p>
      </motion.div>

      <div className="motionRuntimeGrid">
        <MotionBadge
          delay={0.05}
          icon={<Sparkles size={20} />}
          title="Cinematic AI interface"
          body="Layered motion, glow, glass and depth for a premium product feel."
        />
        <MotionBadge
          delay={0.12}
          icon={<Workflow size={20} />}
          title="Workflow storytelling"
          body="Visualise agents moving from task to output to governed delivery."
        />
        <MotionBadge
          delay={0.19}
          icon={<ShieldCheck size={20} />}
          title="Governance visible"
          body="Approval, safety and audit confidence built into the visual language."
        />
        <MotionBadge
          delay={0.26}
          icon={<WandSparkles size={20} />}
          title="Conversion polish"
          body="Premium interactions, hover states and animated trust cues."
        />
      </div>
    </section>
  );
}


function AnimatedWorkflowSection() {
  const steps = [
    ["01", "Client context", "Business profile, offer, audience, products and goals are converted into execution-ready intelligence."],
    ["02", "Agent selection", "Specialist ecommerce agents activate based on the task, purchased access and client workflow needs."],
    ["03", "Premium output", "Agents generate commercial-grade deliverables, campaign assets, copy, strategy and execution recommendations."],
    ["04", "Governed delivery", "High-risk actions stay approval-gated while safe execution moves through the workflow with audit visibility."],
  ];

  return (
    <section className="animatedWorkflowSection">
      <motion.div
        className="workflowHeader"
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.26 }}
        transition={{ duration: 0.72 }}
      >
        <div className="runtimeEyebrow">Workflow intelligence</div>
        <h2>From business context to governed execution.</h2>
        <p>
          The landing page now shows the product as an active AI workforce system:
          context enters, agents collaborate, outputs are produced, and risky actions
          stay under approval control.
        </p>
      </motion.div>

      <div className="workflowStage">
        {steps.map(([number, title, body], index) => (
          <motion.div
            key={title}
            className="workflowStep"
            initial={{ opacity: 0, x: index % 2 === 0 ? -36 : 36, y: 22 }}
            whileInView={{ opacity: 1, x: 0, y: 0 }}
            viewport={{ once: true, amount: 0.34 }}
            transition={{ duration: 0.66, delay: index * 0.09, ease: [0.22, 1, 0.36, 1] }}
            whileHover={{ y: -8, scale: 1.015 }}
          >
            <div className="workflowNumber">{number}</div>
            <div>
              <strong>{title}</strong>
              <span>{body}</span>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="workflowConsole"
        initial={{ opacity: 0, y: 38, scale: 0.98 }}
        whileInView={{ opacity: 1, y: 0, scale: 1 }}
        viewport={{ once: true, amount: 0.24 }}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="workflowConsoleTop">
          <span />
          <span />
          <span />
          <strong>Live AI execution preview</strong>
        </div>

        <div className="workflowConsoleBody">
          {[
            ["Business intelligence", "Loaded", "100%"],
            ["Agent workflow", "Running", "76%"],
            ["Premium output", "Generating", "64%"],
            ["Approval controls", "Active", "Locked"],
          ].map(([label, status, value]) => (
            <div key={label} className="consoleRow">
              <div>
                <strong>{label}</strong>
                <span>{status}</span>
              </div>
              <em>{value}</em>
            </div>
          ))}
        </div>
      </motion.div>
    </section>
  );
}

export default function HomePage() {
  return (
    <main>
      <LandingSpotlightLayer />
      <nav className="nav">
        <Link className="logo" href="/">
          <span className="logomk">AI</span>
          <span>AI Workforce Platform</span>
        </Link>
        <div className="navLinks">
          <a href="#agents">Agents</a>
          <a href="#platform">Platform</a>
          <a href="#pricing">Pricing</a>
          <Link href="/login">Log in</Link>
          <Link className="navBtn" href="/signup">Get Started</Link>
        </div>
      </nav>

      <section className="hero">
        <div className="gridBg" />
        <div className="glow one" />
        <div className="glow two" />
        <HeroVisualSystem />
        <PremiumHeroOrb />
        <div className="heroInner">
          <div className="eyebrow"><span /> Now live — 24 specialist AI agents</div>
          <h1>Your Business.<br />
          <span className="h1-line2">Your AI Team.</span></h1>
          <p>
            Activate specialist AI agents across strategy, creative, operations, analytics, and support.
            Governed, white-label ready, and built for real commercial outcomes.
          </p>
          <div className="heroActions">
            <Link href="/signup" className="primary">Start free — no card needed →</Link>
            <a href="#agents" className="secondary">Meet the agents ↓</a>
          </div>
          <div className="trust">
            <span>✓ Approval-safe</span>
            <span>✓ White-label</span>
            <span>✓ Multi-tenant</span>
            <span>✓ Cancel anytime</span>
          </div>
        </div>
      </section>

      <section className="ticker">
        <div className="tickerTrack">
          {[...ticker, ...ticker].map((item, index) => <span key={`${item}-${index}`}>{item}</span>)}
        </div>
      </section>

      <section className="numbers">
        <div><b>148</b><span>Successful executions</span></div>
        <div><b>24</b><span>Specialist agents</span></div>
        <div><b>8</b><span>Active subscriptions</span></div>
        <div><b>94%</b><span>Average quality score</span></div>
      </section>

      <section id="agents" className="section">
        <div className="sectionHead">
          <span>Your AI workforce</span>
          <h2>Meet your team.<br /><b>Built for every function.</b></h2>
          <p>Each agent is a specialist — not a generalist. Together they cover the business functions ecommerce operators need.</p>
        </div>

        <div className="agentGrid">
          {agents.map(([name, desc, icon, color]) => (
            <div className="agentCard" key={name as string} style={{ "--accent": color } as React.CSSProperties}>
              <div className="agentVisual">
                <span>{icon}</span>
              </div>
              <h3>{name as string}</h3>
              <p>{desc as string}</p>
              <button>Run demo →</button>
            </div>
          ))}
        </div>
      </section>

      <section id="platform" className="platform">
        <div className="platformCopy">
          <span>Live platform</span>
          <h2>See it work.<br /><b>Right now.</b></h2>
          <p>
            Enter business context, select an agent, and generate premium role-specific output.
            Every output is approval-safe, quality-scored, and client-ready.
          </p>
        </div>

        <div className="window">
          <div className="windowTop"><i /><i /><i /><strong>AI Workforce Platform — Live workspace</strong></div>
          <div className="context">
            <div><small>Store</small><b>Acme Commerce</b></div>
            <div><small>Industry</small><b>Fashion Retail</b></div>
            <div><small>Audience</small><b>Premium buyers</b></div>
          </div>
          <div className="pills">
            {["Strategy", "Research", "Creative", "Analytics", "Operations", "Support"].map((item, index) => (
              <span className={index === 0 ? "on" : ""} key={item}>{item}</span>
            ))}
          </div>
          <div className="task">
            Analyse market positioning and identify three ecommerce growth opportunities.
          </div>
          <div className="output">
            <small>Premium output</small>
            <p><b>Opportunity 1:</b> Bundle premium products into seasonal offer campaigns to increase AOV.</p>
            <p><b>Opportunity 2:</b> Add creator-led UGC variations for paid social testing.</p>
            <p><b>Opportunity 3:</b> Build segmented email flows around purchase intent and retention.</p>
          </div>
        </div>
      </section>

      
      <section className="premium-media-landing-marker" style={{
        background: "#080B14",
        padding: "96px 24px",
        borderTop: "1px solid rgba(255,255,255,.08)",
        borderBottom: "1px solid rgba(255,255,255,.08)",
      }}>
        <div style={{
          maxWidth: 1240,
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(320px,1fr))",
          gap: 42,
          alignItems: "center",
        }}>
          <div>
            <div style={{
              color: "#0ECFBC",
              fontSize: 12,
              fontWeight: 900,
              letterSpacing: ".14em",
              textTransform: "uppercase",
              marginBottom: 16,
            }}>
              Premium motion layer
            </div>
            <h2 style={{
              color: "#fff",
              fontSize: "clamp(36px,5vw,64px)",
              lineHeight: 1,
              letterSpacing: "-.04em",
              margin: 0,
            }}>
              Your AI team, visualised as a live command centre.
            </h2>
            <p style={{
              color: "#94A3B8",
              fontSize: 17,
              lineHeight: 1.8,
              marginTop: 20,
              maxWidth: 580,
            }}>
              This section is ready for WebM, MP4, poster, Spline, or Lottie assets. Until custom assets are produced, it uses a premium animated fallback.
            </p>
          </div>
          <PremiumHeroMedia mode="fallback" />
        </div>
      </section>

<section id="pricing" className="section pricing">
        <div className="sectionHead">
          <span>Pricing</span>
          <h2>Choose your<br /><b>AI workforce plan.</b></h2>
          <p>Start free. Scale when ready. Every plan includes approval-safe governance and premium output quality.</p>
        </div>
        <div className="priceGrid">
          {plans.map(([name, price, desc, features, href], index) => (
            <div className={`priceCard ${index === 1 ? "featured" : ""}`} key={name as string}>
              {index === 1 ? <em>Most popular</em> : null}
              <h3>{name as string}</h3>
              <div className="price">{price as string}</div>
              <p>{desc as string}</p>
              <ul>{(features as string[]).map((feature) => <li key={feature}>✓ {feature}</li>)}</ul>
              <Link href={href as string}>{index === 3 ? "Talk to sales" : "Get started"}</Link>
            </div>
          ))}
        </div>
      </section>

      <LandingMotionRuntimeLayer />

      <AnimatedWorkflowSection />

      <section className="final">
        <h2>Your AI workforce is ready to deploy.</h2>
        <p>Start free. No credit card. Full platform access from day one.</p>
        <Link href="/signup">Deploy your AI workforce →</Link>
      </section>

      <footer>
        <strong>AI Workforce Platform</strong>
        <p>© 2026 AI Workforce Platform. Built for businesses that move faster with AI.</p>
      </footer>

      <style>{`
        *{box-sizing:border-box}
        main{background:#080B14;color:#EEF2FF;font-family:Inter,Arial,sans-serif;overflow:hidden}
        .nav{position:fixed;top:0;left:0;right:0;z-index:99;height:66px;padding:0 6%;display:flex;align-items:center;justify-content:space-between;background:rgba(8,11,20,.86);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.08)}
        .logo{display:flex;align-items:center;gap:11px;text-decoration:none;color:#fff;font-weight:800}
        .logomk{width:36px;height:36px;border-radius:9px;background:linear-gradient(135deg,#5B52F0,#7C74FF);display:grid;place-items:center}
        .navLinks{display:flex;align-items:center;gap:30px}.navLinks a{color:#B8C4D8;text-decoration:none;font-weight:700}.navBtn{background:#5B52F0!important;color:#fff!important;border-radius:8px;padding:10px 22px}
        .hero{min-height:100vh;display:flex;align-items:center;justify-content:center;position:relative;padding:120px 6% 80px;text-align:center;background:radial-gradient(ellipse 120% 80% at 50% 0%,#12183A 0%,#080B14 60%)}
        .gridBg{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:80px 80px;mask-image:radial-gradient(ellipse 90% 90% at 50% 50%,black,transparent)}
        .glow{position:absolute;border-radius:50%;filter:blur(20px);animation:breath 8s infinite ease-in-out}.one{top:-15%;width:900px;height:600px;background:rgba(91,82,240,.22)}.two{bottom:15%;left:8%;width:420px;height:420px;background:rgba(14,207,188,.10)}
        .heroInner{position:relative;max-width:920px}.eyebrow{display:inline-flex;gap:8px;align-items:center;background:rgba(91,82,240,.12);border:1px solid rgba(91,82,240,.3);border-radius:30px;padding:7px 18px;margin-bottom:32px;color:#9D97FF;font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.eyebrow span{width:7px;height:7px;border-radius:50%;background:#0ECFBC}
        h1{font-size:clamp(46px,7vw,88px);line-height:1;letter-spacing:-.06em;margin:0 0 24px;font-weight:950}h1 b,.sectionHead b,.platformCopy b{background:linear-gradient(135deg,#7C74FF,#0ECFBC,#4EACFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .hero p{font-size:clamp(16px,1.6vw,20px);color:#7A8899;line-height:1.8;max-width:650px;margin:0 auto 38px}.heroActions{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}.primary,.secondary{border-radius:10px;padding:16px 30px;text-decoration:none;font-weight:900}.primary{background:#5B52F0;color:#fff}.secondary{border:1px solid rgba(255,255,255,.16);color:#fff}.trust{display:flex;gap:24px;justify-content:center;flex-wrap:wrap;margin-top:32px;color:#7A8899}
        .ticker{padding:16px 0;overflow:hidden;background:rgba(255,255,255,.03);border-top:1px solid rgba(255,255,255,.06);border-bottom:1px solid rgba(255,255,255,.06)}.tickerTrack{display:flex;width:max-content;animation:ticker 36s linear infinite}.tickerTrack span{padding:0 32px;color:#7A8899;font-weight:800;white-space:nowrap}
        .numbers{display:grid;grid-template-columns:repeat(4,1fr);max-width:1100px;margin:0 auto;border-left:1px solid rgba(255,255,255,.06)}.numbers div{text-align:center;padding:36px 20px;border-right:1px solid rgba(255,255,255,.06)}.numbers b{display:block;font-size:42px;background:linear-gradient(135deg,#7C74FF,#0ECFBC);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.numbers span{color:#7A8899;font-size:13px}
        .section{padding:110px 6%}.sectionHead{text-align:center;max-width:780px;margin:0 auto 56px}.sectionHead>span,.platformCopy>span{color:#0ECFBC;font-size:12px;text-transform:uppercase;letter-spacing:.14em;font-weight:900}.sectionHead h2,.platformCopy h2,.final h2{font-size:clamp(36px,5vw,64px);line-height:1;letter-spacing:-.04em}.sectionHead p,.platformCopy p{color:#7A8899;line-height:1.8;font-size:17px}
        .agentGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;max-width:1280px;margin:0 auto}.agentCard{background:#0F1625;border:1px solid rgba(255,255,255,.08);border-radius:22px;padding:24px;transition:.25s}.agentCard:hover{transform:translateY(-6px);border-color:var(--accent);box-shadow:0 24px 60px rgba(0,0,0,.35)}.agentVisual{height:130px;border-radius:18px;background:radial-gradient(circle,var(--accent),transparent 65%);display:grid;place-items:center;font-size:48px;margin-bottom:18px}.agentCard h3{font-size:21px}.agentCard p{color:#7A8899;line-height:1.7}.agentCard button{width:100%;border:none;border-radius:10px;background:var(--accent);color:#fff;padding:12px;font-weight:900;margin-top:14px}
        .platform{display:grid;grid-template-columns:1fr 1.1fr;gap:70px;align-items:center;padding:110px 6%;max-width:1280px;margin:0 auto}.window{background:#080D18;border:1px solid rgba(255,255,255,.12);border-radius:18px;overflow:hidden;box-shadow:0 32px 80px rgba(0,0,0,.7)}.windowTop{height:42px;background:rgba(255,255,255,.04);display:flex;gap:8px;align-items:center;padding:0 16px}.windowTop i{width:10px;height:10px;border-radius:50%;background:#3E4A5C}.windowTop strong{margin-left:10px;color:#7A8899;font-size:12px}.context{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:18px}.context div,.task,.output{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:13px}.context small,.output small{display:block;color:#3E4A5C;text-transform:uppercase;font-weight:900;font-size:10px}.context b{font-size:13px}.pills{display:flex;gap:8px;flex-wrap:wrap;padding:0 18px 14px}.pills span{border:1px solid rgba(255,255,255,.08);border-radius:999px;padding:6px 12px;color:#7A8899;font-size:12px}.pills .on{background:rgba(91,82,240,.22);color:#9D97FF}.task{margin:0 18px 14px;color:#B8C4D8}.output{margin:0 18px 18px;color:#B8C4D8}.output p{font-size:13px;line-height:1.65}
        .pricing{background:#0D1220}.priceGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;max-width:1150px;margin:0 auto}.priceCard{position:relative;background:#0F1625;border:1px solid rgba(255,255,255,.08);border-radius:18px;padding:28px}.priceCard.featured{border-color:#5B52F0}.priceCard em{position:absolute;top:16px;right:16px;background:#5B52F0;color:#fff;border-radius:999px;padding:4px 10px;font-size:11px;font-style:normal}.price{font-size:48px;font-weight:950}.priceCard p,.priceCard li{color:#7A8899}.priceCard ul{list-style:none;padding:0;display:grid;gap:8px}.priceCard a{display:block;text-align:center;background:#5B52F0;color:#fff;text-decoration:none;border-radius:10px;padding:13px;margin-top:22px;font-weight:900}
        .final{text-align:center;padding:110px 6%}.final p{color:#7A8899}.final a{display:inline-block;margin-top:24px;background:#5B52F0;color:#fff;border-radius:10px;padding:16px 30px;text-decoration:none;font-weight:900}footer{border-top:1px solid rgba(255,255,255,.08);padding:42px 6%;color:#7A8899}footer strong{color:#fff}
        @keyframes ticker{to{transform:translateX(-50%)}}@keyframes breath{50%{transform:scale(1.08);opacity:.75}}

        /* LANDING_PREMIUM_ANIMATION_GLASS_3D_V1 */
        main{
          position:relative;
          background:
            radial-gradient(circle at 18% 4%, rgba(124,116,255,.18), transparent 26%),
            radial-gradient(circle at 84% 10%, rgba(14,207,188,.12), transparent 28%),
            linear-gradient(180deg,#050814 0%,#080B14 46%,#060916 100%);
        }
        main:before{
          content:"";
          position:fixed;
          inset:0;
          pointer-events:none;
          z-index:0;
          background:
            radial-gradient(circle at 20% 20%, rgba(124,116,255,.16), transparent 18%),
            radial-gradient(circle at 80% 30%, rgba(14,207,188,.10), transparent 20%),
            linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
          background-size:auto,auto,72px 72px,72px 72px;
          mask-image:linear-gradient(180deg,black 0%,rgba(0,0,0,.68) 42%,transparent 100%);
        }
        main > *{position:relative;z-index:1}
        .nav{
          background:rgba(8,11,20,.68)!important;
          backdrop-filter:blur(26px) saturate(150%)!important;
          -webkit-backdrop-filter:blur(26px) saturate(150%)!important;
          box-shadow:0 18px 50px rgba(0,0,0,.22);
        }
        .logo,.navBtn,.primary,.secondary,.priceCard a,.final a{
          transition:transform .22s ease, box-shadow .22s ease, border-color .22s ease, filter .22s ease;
        }
        .logo:hover,.navBtn:hover,.primary:hover,.secondary:hover,.priceCard a:hover,.final a:hover{
          transform:translateY(-2px);
          filter:brightness(1.08);
          box-shadow:0 18px 42px rgba(91,82,240,.28);
        }
        .hero{
          perspective:1200px;
          isolation:isolate;
        }
        .hero:before{
          content:"";
          position:absolute;
          width:min(86vw,980px);
          height:min(86vw,980px);
          border-radius:999px;
          background:conic-gradient(from 180deg, rgba(124,116,255,.20), rgba(14,207,188,.12), rgba(78,172,255,.10), rgba(124,116,255,.20));
          filter:blur(28px);
          opacity:.36;
          animation:slowSpin 28s linear infinite;
          transform:translateZ(-1px);
        }
        .hero:after{
          content:"";
          position:absolute;
          width:520px;
          height:520px;
          right:7%;
          bottom:11%;
          border-radius:999px;
          background:radial-gradient(circle, rgba(14,207,188,.20), transparent 64%);
          filter:blur(8px);
          animation:floatOrb 9s ease-in-out infinite;
        }
        .heroInner{
          transform-style:preserve-3d;
          animation:heroLift .9s ease both;
        }
        .eyebrow{
          backdrop-filter:blur(16px);
          -webkit-backdrop-filter:blur(16px);
          box-shadow:inset 0 1px 0 rgba(255,255,255,.12), 0 18px 46px rgba(91,82,240,.18);
        }
        h1{
          text-shadow:0 18px 70px rgba(124,116,255,.20);
        }
        .h1-line2{
          display:inline-block;
          background:linear-gradient(135deg,#fff 0%,#9D97FF 36%,#0ECFBC 76%,#fff 100%);
          background-size:220% auto;
          -webkit-background-clip:text;
          background-clip:text;
          color:transparent;
          animation:textSheen 5.8s ease-in-out infinite;
        }
        .primary{
          background:linear-gradient(135deg,#5B52F0,#7C74FF,#0ECFBC)!important;
          background-size:180% auto!important;
          animation:ctaPulse 5.5s ease-in-out infinite;
        }
        .secondary,.agentCard,.priceCard,.window,.context div,.task,.output{
          backdrop-filter:blur(18px) saturate(145%);
          -webkit-backdrop-filter:blur(18px) saturate(145%);
        }
        .numbers div,.agentCard,.priceCard,.window{
          transform-style:preserve-3d;
        }
        .numbers div{
          transition:transform .25s ease, background .25s ease;
        }
        .numbers div:hover{
          transform:translateY(-4px);
          background:rgba(255,255,255,.025);
        }
        .agentCard,.priceCard{
          position:relative;
          overflow:hidden;
          background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.035))!important;
          box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 24px 70px rgba(0,0,0,.22);
        }
        .agentCard:before,.priceCard:before,.window:before{
          content:"";
          position:absolute;
          inset:-1px;
          background:linear-gradient(120deg,transparent 0%,rgba(255,255,255,.16) 22%,transparent 44%);
          transform:translateX(-130%);
          transition:transform .75s ease;
          pointer-events:none;
        }
        .agentCard:hover:before,.priceCard:hover:before,.window:hover:before{
          transform:translateX(130%);
        }
        .agentCard:hover,.priceCard:hover{
          transform:translateY(-8px) rotateX(2deg) rotateY(-2deg);
        }
        .agentVisual{
          box-shadow:inset 0 1px 0 rgba(255,255,255,.16), 0 20px 50px color-mix(in srgb, var(--accent) 28%, transparent);
          animation:softFloat 7s ease-in-out infinite;
        }
        .agentCard:nth-child(2n) .agentVisual{animation-delay:-1.2s}
        .agentCard:nth-child(3n) .agentVisual{animation-delay:-2.3s}
        .platform{
          perspective:1300px;
        }
        .window{
          position:relative;
          background:linear-gradient(180deg,rgba(15,22,37,.92),rgba(5,10,22,.96))!important;
          transform:rotateX(2deg) rotateY(-4deg);
          transition:transform .35s ease, box-shadow .35s ease;
        }
        .window:hover{
          transform:rotateX(0deg) rotateY(0deg) translateY(-6px);
          box-shadow:0 42px 110px rgba(0,0,0,.78), 0 0 70px rgba(91,82,240,.16);
        }
        .windowTop{
          backdrop-filter:blur(18px);
          -webkit-backdrop-filter:blur(18px);
        }
        .pills span,.context div,.task,.output{
          transition:transform .22s ease, border-color .22s ease, background .22s ease;
        }
        .pills span:hover,.context div:hover,.task:hover,.output:hover{
          transform:translateY(-2px);
          border-color:rgba(124,116,255,.28);
          background:rgba(255,255,255,.07);
        }
        .premium-media-landing-marker{
          position:relative;
          overflow:hidden;
          background:
            radial-gradient(circle at 74% 22%, rgba(14,207,188,.11), transparent 24%),
            radial-gradient(circle at 18% 70%, rgba(124,116,255,.12), transparent 26%),
            #080B14!important;
        }
        .premium-media-landing-marker:before{
          content:"";
          position:absolute;
          inset:0;
          background:linear-gradient(115deg,transparent,rgba(255,255,255,.06),transparent);
          transform:translateX(-100%);
          animation:sectionSweep 9s ease-in-out infinite;
        }
        .priceCard.featured{
          box-shadow:0 28px 80px rgba(91,82,240,.26), inset 0 1px 0 rgba(255,255,255,.10);
        }
        .final{
          position:relative;
          overflow:hidden;
          background:
            radial-gradient(circle at 50% 10%, rgba(124,116,255,.18), transparent 28%),
            linear-gradient(180deg,transparent,rgba(255,255,255,.018));
        }
        @keyframes heroLift{
          from{opacity:0;transform:translateY(28px) scale(.985)}
          to{opacity:1;transform:translateY(0) scale(1)}
        }
        @keyframes slowSpin{
          to{transform:rotate(360deg)}
        }
        @keyframes floatOrb{
          0%,100%{transform:translate3d(0,0,0) scale(1)}
          50%{transform:translate3d(-24px,-30px,0) scale(1.08)}
        }
        @keyframes textSheen{
          0%,100%{background-position:0% center}
          50%{background-position:100% center}
        }
        @keyframes ctaPulse{
          0%,100%{background-position:0% center;box-shadow:0 18px 44px rgba(91,82,240,.26)}
          50%{background-position:100% center;box-shadow:0 24px 62px rgba(14,207,188,.20)}
        }
        @keyframes softFloat{
          0%,100%{transform:translateY(0)}
          50%{transform:translateY(-8px)}
        }
        @keyframes sectionSweep{
          0%,72%{transform:translateX(-110%)}
          100%{transform:translateX(110%)}
        }
        @media (prefers-reduced-motion: reduce){
          *,*:before,*:after{
            animation:none!important;
            transition:none!important;
            scroll-behavior:auto!important;
          }
        }


        /* LANDING_MOTION_RUNTIME_LAYER_V1 */
        .heroOrb3d{
          position:absolute;
          right:min(6vw,90px);
          top:120px;
          width:min(42vw,520px);
          height:min(42vw,520px);
          opacity:.92;
          filter:drop-shadow(0 34px 90px rgba(91,82,240,.22));
          pointer-events:none;
          z-index:0;
        }
        .heroInner{position:relative;z-index:2}
        .motionRuntimeLayer{
          position:relative;
          max-width:1180px;
          margin:40px auto 0;
          padding:56px 24px;
          z-index:2;
        }
        .motionRuntimeHeader{
          max-width:820px;
          margin:0 auto 28px;
          text-align:center;
        }
        .runtimeEyebrow{
          display:inline-flex;
          padding:9px 13px;
          border-radius:999px;
          border:1px solid rgba(124,116,255,.28);
          background:rgba(124,116,255,.12);
          color:#BDB8FF;
          font-size:12px;
          font-weight:900;
          letter-spacing:.12em;
          text-transform:uppercase;
          margin-bottom:16px;
          backdrop-filter:blur(18px);
        }
        .motionRuntimeHeader h2{
          margin:0;
          font-size:clamp(32px,5vw,58px);
          line-height:.98;
          letter-spacing:-.06em;
          color:#fff;
        }
        .motionRuntimeHeader p{
          margin:18px auto 0;
          max-width:700px;
          color:#A7B0C6;
          line-height:1.65;
          font-size:16px;
        }
        .motionRuntimeGrid{
          display:grid;
          grid-template-columns:repeat(4,minmax(0,1fr));
          gap:16px;
          perspective:1200px;
        }
        .motionBadge{
          min-height:188px;
          border:1px solid rgba(124,116,255,.20);
          border-radius:26px;
          padding:22px;
          background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.032));
          box-shadow:inset 0 1px 0 rgba(255,255,255,.10),0 28px 70px rgba(0,0,0,.24);
          transform-style:preserve-3d;
        }
        .motionBadgeIcon{
          width:44px;
          height:44px;
          display:grid;
          place-items:center;
          border-radius:16px;
          background:linear-gradient(135deg,rgba(124,116,255,.28),rgba(14,207,188,.14));
          color:#C7D2FE;
          margin-bottom:18px;
          box-shadow:0 18px 40px rgba(91,82,240,.20);
        }
        .motionBadge strong{
          display:block;
          color:#fff;
          font-size:17px;
          letter-spacing:-.02em;
          margin-bottom:8px;
        }
        .motionBadge span{
          display:block;
          color:#A7B0C6;
          font-size:14px;
          line-height:1.55;
        }
        .glassLift{
          backdrop-filter:blur(20px) saturate(150%);
          -webkit-backdrop-filter:blur(20px) saturate(150%);
        }
        @media(max-width:980px){
          .heroOrb3d{position:relative;right:auto;top:auto;margin:20px auto 0;width:86vw;height:360px}
          .motionRuntimeGrid{grid-template-columns:repeat(2,minmax(0,1fr))}
        }
        @media(max-width:640px){
          .motionRuntimeGrid{grid-template-columns:1fr}
        }


        /* LANDING_SCROLL_WORKFLOW_ANIMATION_V1 */
        .animatedWorkflowSection{
          max-width:1180px;
          margin:32px auto 0;
          padding:70px 24px;
          position:relative;
          z-index:2;
        }
        .animatedWorkflowSection:before{
          content:"";
          position:absolute;
          left:50%;
          top:180px;
          bottom:140px;
          width:1px;
          background:linear-gradient(180deg,transparent,rgba(124,116,255,.42),rgba(14,207,188,.28),transparent);
          opacity:.8;
        }
        .workflowHeader{
          max-width:820px;
          margin:0 auto 42px;
          text-align:center;
        }
        .workflowHeader h2{
          margin:0;
          color:#fff;
          font-size:clamp(34px,5vw,62px);
          line-height:.98;
          letter-spacing:-.06em;
        }
        .workflowHeader p{
          margin:18px auto 0;
          max-width:720px;
          color:#A7B0C6;
          line-height:1.65;
          font-size:16px;
        }
        .workflowStage{
          display:grid;
          grid-template-columns:repeat(2,minmax(0,1fr));
          gap:18px;
          position:relative;
        }
        .workflowStep{
          min-height:168px;
          border-radius:28px;
          padding:24px;
          border:1px solid rgba(124,116,255,.22);
          background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.032));
          box-shadow:inset 0 1px 0 rgba(255,255,255,.10),0 24px 70px rgba(0,0,0,.22);
          backdrop-filter:blur(20px) saturate(150%);
          -webkit-backdrop-filter:blur(20px) saturate(150%);
          display:grid;
          grid-template-columns:56px 1fr;
          gap:18px;
          align-items:start;
        }
        .workflowNumber{
          width:52px;
          height:52px;
          display:grid;
          place-items:center;
          border-radius:18px;
          background:linear-gradient(135deg,rgba(124,116,255,.30),rgba(14,207,188,.14));
          color:#C7D2FE;
          font-weight:950;
          box-shadow:0 18px 44px rgba(91,82,240,.22);
        }
        .workflowStep strong{
          display:block;
          color:#fff;
          font-size:19px;
          letter-spacing:-.03em;
          margin-bottom:10px;
        }
        .workflowStep span{
          display:block;
          color:#A7B0C6;
          line-height:1.58;
          font-size:14.5px;
        }
        .workflowConsole{
          margin:26px auto 0;
          max-width:820px;
          border-radius:30px;
          overflow:hidden;
          border:1px solid rgba(124,116,255,.24);
          background:linear-gradient(180deg,rgba(9,15,31,.96),rgba(3,8,20,.98));
          box-shadow:0 38px 100px rgba(0,0,0,.48), inset 0 1px 0 rgba(255,255,255,.08);
        }
        .workflowConsoleTop{
          height:54px;
          display:flex;
          align-items:center;
          gap:9px;
          padding:0 18px;
          border-bottom:1px solid rgba(255,255,255,.08);
          background:rgba(255,255,255,.035);
          color:#CBD5E1;
          font-size:12px;
          font-weight:900;
          letter-spacing:.04em;
          text-transform:uppercase;
        }
        .workflowConsoleTop span{
          width:10px;
          height:10px;
          border-radius:99px;
          background:#7C74FF;
        }
        .workflowConsoleTop span:nth-child(2){background:#0ECFBC}
        .workflowConsoleTop span:nth-child(3){background:#F59E0B}
        .workflowConsoleTop strong{margin-left:8px}
        .workflowConsoleBody{
          display:grid;
          gap:10px;
          padding:18px;
        }
        .consoleRow{
          display:flex;
          justify-content:space-between;
          gap:16px;
          align-items:center;
          padding:14px 16px;
          border-radius:18px;
          border:1px solid rgba(124,116,255,.16);
          background:rgba(255,255,255,.045);
        }
        .consoleRow strong{
          display:block;
          color:#fff;
          font-size:14px;
          margin-bottom:3px;
        }
        .consoleRow span{
          color:#94A3B8;
          font-size:12px;
          font-weight:800;
        }
        .consoleRow em{
          font-style:normal;
          color:#0ECFBC;
          font-weight:950;
          font-size:13px;
        }
        @media(max-width:860px){
          .animatedWorkflowSection:before{display:none}
          .workflowStage{grid-template-columns:1fr}
        }


        /* LANDING_HERO_VISUAL_DENSITY_V1 */
        .heroVisualSystem{
          position:absolute;
          inset:0;
          pointer-events:none;
          overflow:hidden;
          z-index:1;
        }
        .heroGlassCard{
          position:absolute;
          width:220px;
          border-radius:24px;
          padding:16px;
          border:1px solid rgba(124,116,255,.24);
          background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,.035));
          box-shadow:0 28px 70px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.12);
          backdrop-filter:blur(22px) saturate(150%);
          -webkit-backdrop-filter:blur(22px) saturate(150%);
          color:#fff;
          animation:heroCardFloat 7.5s ease-in-out infinite;
        }
        .heroGlassCard strong{
          display:block;
          font-size:13px;
          margin-bottom:6px;
        }
        .heroGlassCard span{
          display:block;
          color:#A7B0C6;
          font-size:12px;
          line-height:1.45;
        }
        .heroGlassCard em{
          display:inline-flex;
          margin-top:12px;
          padding:6px 9px;
          border-radius:999px;
          background:rgba(14,207,188,.13);
          color:#5EEAD4;
          font-size:11px;
          font-style:normal;
          font-weight:900;
        }
        .heroGlassCard.cardA{left:7%;top:28%;animation-delay:-.7s}
        .heroGlassCard.cardB{right:8%;top:29%;animation-delay:-2.1s}
        .heroGlassCard.cardC{right:15%;bottom:16%;animation-delay:-3.4s}
        .heroGlassCard.cardD{left:13%;bottom:20%;animation-delay:-4.6s}
        .heroAgentRail{
          position:absolute;
          left:50%;
          bottom:8%;
          transform:translateX(-50%);
          display:flex;
          gap:10px;
          padding:10px;
          border-radius:999px;
          border:1px solid rgba(124,116,255,.20);
          background:rgba(8,11,20,.55);
          backdrop-filter:blur(18px);
          -webkit-backdrop-filter:blur(18px);
          box-shadow:0 22px 60px rgba(0,0,0,.30);
        }
        .heroAgentDot{
          width:42px;
          height:42px;
          border-radius:999px;
          display:grid;
          place-items:center;
          color:#fff;
          font-size:12px;
          font-weight:950;
          background:linear-gradient(135deg,rgba(124,116,255,.85),rgba(14,207,188,.52));
          box-shadow:0 14px 34px rgba(91,82,240,.32);
          animation:agentPulse 2.8s ease-in-out infinite;
        }
        .heroAgentDot:nth-child(2){animation-delay:.25s}
        .heroAgentDot:nth-child(3){animation-delay:.5s}
        .heroAgentDot:nth-child(4){animation-delay:.75s}
        .heroAgentDot:nth-child(5){animation-delay:1s}
        .heroDashboardPreview{
          position:absolute;
          right:11%;
          top:46%;
          width:310px;
          border-radius:28px;
          overflow:hidden;
          border:1px solid rgba(124,116,255,.26);
          background:linear-gradient(180deg,rgba(9,15,31,.94),rgba(3,8,20,.97));
          box-shadow:0 38px 100px rgba(0,0,0,.46),0 0 80px rgba(91,82,240,.16);
          backdrop-filter:blur(18px);
          -webkit-backdrop-filter:blur(18px);
          animation:dashboardFloat 8.5s ease-in-out infinite;
        }
        .heroDashboardTop{
          height:40px;
          display:flex;
          align-items:center;
          gap:7px;
          padding:0 14px;
          border-bottom:1px solid rgba(255,255,255,.08);
          background:rgba(255,255,255,.04);
        }
        .heroDashboardTop span{
          width:9px;
          height:9px;
          border-radius:999px;
          background:#7C74FF;
        }
        .heroDashboardTop span:nth-child(2){background:#0ECFBC}
        .heroDashboardTop span:nth-child(3){background:#F59E0B}
        .heroDashboardBody{
          padding:14px;
          display:grid;
          gap:10px;
        }
        .heroMiniRow{
          display:grid;
          grid-template-columns:34px 1fr 44px;
          gap:9px;
          align-items:center;
          padding:10px;
          border:1px solid rgba(124,116,255,.16);
          background:rgba(255,255,255,.045);
          border-radius:16px;
        }
        .heroMiniIcon{
          width:34px;
          height:34px;
          border-radius:12px;
          display:grid;
          place-items:center;
          color:#C7D2FE;
          background:rgba(124,116,255,.18);
          font-size:12px;
          font-weight:950;
        }
        .heroMiniText strong{
          display:block;
          color:#fff;
          font-size:12px;
          margin-bottom:3px;
        }
        .heroMiniText span{
          display:block;
          color:#94A3B8;
          font-size:11px;
        }
        .heroMiniStatus{
          color:#0ECFBC;
          font-size:10px;
          font-weight:950;
        }
        @keyframes heroCardFloat{
          0%,100%{transform:translate3d(0,0,0) rotate(0deg)}
          50%{transform:translate3d(0,-14px,0) rotate(1deg)}
        }
        @keyframes dashboardFloat{
          0%,100%{transform:translate3d(0,0,0) rotateY(-7deg)}
          50%{transform:translate3d(0,-18px,0) rotateY(-2deg)}
        }
        @keyframes agentPulse{
          0%,100%{transform:translateY(0) scale(1);filter:brightness(1)}
          50%{transform:translateY(-7px) scale(1.05);filter:brightness(1.16)}
        }
        @media(max-width:1100px){
          .heroGlassCard,.heroDashboardPreview{display:none}
          .heroAgentRail{bottom:5%}
        }


        /* LANDING_BELOW_FOLD_MOTION_POLISH_V1 */
        .agents,.platform,.pricing,.final{
          position:relative;
          overflow:hidden;
        }
        .agents:before,.platform:before,.pricing:before{
          content:"";
          position:absolute;
          inset:8% auto auto 50%;
          width:760px;
          height:760px;
          transform:translateX(-50%);
          border-radius:999px;
          background:radial-gradient(circle, rgba(124,116,255,.10), transparent 64%);
          pointer-events:none;
          filter:blur(10px);
        }
        .agentGrid,.pricingGrid{
          perspective:1300px;
        }
        .agentCard,.priceCard{
          will-change:transform;
        }
        .agentCard:hover .agentVisual{
          transform:translateY(-10px) scale(1.05) rotate(2deg);
          filter:brightness(1.16);
        }
        .agentCard h3,.priceCard h3{
          letter-spacing:-.035em;
        }
        .agentCard p,.priceCard p{
          color:#A7B0C6!important;
        }
        .platform .window{
          border-color:rgba(124,116,255,.26)!important;
        }
        .platform .window:after{
          content:"";
          position:absolute;
          inset:0;
          background:
            radial-gradient(circle at 74% 18%, rgba(14,207,188,.10), transparent 26%),
            radial-gradient(circle at 22% 74%, rgba(124,116,255,.13), transparent 30%);
          pointer-events:none;
        }
        .context div,.task,.output{
          box-shadow:inset 0 1px 0 rgba(255,255,255,.08);
        }
        .task{
          position:relative;
          overflow:hidden;
        }
        .task:after{
          content:"";
          position:absolute;
          left:0;
          bottom:0;
          height:2px;
          width:64%;
          background:linear-gradient(90deg,#7C74FF,#0ECFBC);
          animation:taskProgress 4.8s ease-in-out infinite;
        }
        .output{
          position:relative;
          overflow:hidden;
        }
        .output:after{
          content:"";
          position:absolute;
          inset:auto 14px 14px auto;
          width:72px;
          height:72px;
          border-radius:999px;
          background:radial-gradient(circle, rgba(14,207,188,.18), transparent 70%);
          filter:blur(2px);
        }
        .priceCard{
          transition:transform .28s ease, box-shadow .28s ease, border-color .28s ease;
        }
        .priceCard:hover{
          border-color:rgba(14,207,188,.30)!important;
          box-shadow:0 34px 95px rgba(0,0,0,.34),0 0 80px rgba(91,82,240,.12);
        }
        .priceCard.featured{
          transform:translateY(-8px);
          border-color:rgba(124,116,255,.46)!important;
        }
        .priceCard.featured:hover{
          transform:translateY(-14px) rotateX(2deg) rotateY(-2deg);
        }
        .final{
          border-top:1px solid rgba(124,116,255,.14);
        }
        .final:before{
          content:"";
          position:absolute;
          inset:12% 18%;
          background:radial-gradient(circle, rgba(124,116,255,.18), transparent 64%);
          filter:blur(20px);
          pointer-events:none;
        }
        .final h2{
          background:linear-gradient(135deg,#fff,#A5B4FC,#5EEAD4);
          -webkit-background-clip:text;
          background-clip:text;
          color:transparent!important;
        }
        @keyframes taskProgress{
          0%,100%{width:18%;opacity:.55}
          50%{width:92%;opacity:1}
        }


        /* LANDING_PARALLAX_SPOTLIGHT_V1 */
        .landingSpotlightLayer{
          position:fixed;
          inset:0;
          pointer-events:none;
          z-index:0;
          overflow:hidden;
        }
        .spotlightBeam{
          position:absolute;
          width:42vw;
          height:42vw;
          border-radius:999px;
          filter:blur(42px);
          opacity:.24;
          mix-blend-mode:screen;
          animation:spotlightDrift 16s ease-in-out infinite;
        }
        .beamOne{
          left:-12vw;
          top:18vh;
          background:radial-gradient(circle, rgba(124,116,255,.48), transparent 64%);
        }
        .beamTwo{
          right:-10vw;
          top:8vh;
          background:radial-gradient(circle, rgba(14,207,188,.32), transparent 66%);
          animation-delay:-5s;
        }
        .beamThree{
          left:32vw;
          bottom:-20vw;
          background:radial-gradient(circle, rgba(78,172,255,.22), transparent 70%);
          animation-delay:-9s;
        }
        .ambientParticleField{
          position:absolute;
          inset:0;
          opacity:.55;
        }
        .ambientParticleField span{
          position:absolute;
          width:3px;
          height:3px;
          border-radius:999px;
          background:rgba(255,255,255,.72);
          left:calc((var(--i) * 29px) % 100vw);
          top:calc((var(--i) * 53px) % 100vh);
          animation:particleRise calc(7s + (var(--i) * .17s)) linear infinite;
          animation-delay:calc(var(--i) * -.31s);
          box-shadow:0 0 14px rgba(124,116,255,.42);
        }
        .heroGlassCard.cardA{transform:translateY(var(--scroll-shift-a,0px))}
        .heroGlassCard.cardB{transform:translateY(var(--scroll-shift-b,0px))}
        .heroDashboardPreview{transform:translateY(var(--scroll-shift-c,0px))}
        .heroAgentRail{transform:translateX(-50%) translateY(var(--scroll-shift-d,0px))}
        @keyframes spotlightDrift{
          0%,100%{transform:translate3d(0,0,0) scale(1)}
          50%{transform:translate3d(4vw,-4vh,0) scale(1.12)}
        }
        @keyframes particleRise{
          from{transform:translateY(18vh);opacity:0}
          16%{opacity:.7}
          82%{opacity:.45}
          to{transform:translateY(-110vh);opacity:0}
        }

        @media(max-width:900px){.nav{height:auto;padding:14px 20px}.navLinks{gap:14px}.navLinks a:not(.navBtn){display:none}.hero{padding-top:110px}.numbers{grid-template-columns:repeat(2,1fr)}.platform{grid-template-columns:1fr;padding:80px 6%}.context{grid-template-columns:1fr}.section{padding:80px 6%}}
      `}</style>
    </main>
  );
}
