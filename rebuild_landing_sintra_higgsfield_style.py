from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"landing_page_before_full_rebuild_sintra_higgsfield_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

TARGET.write_text(r'''"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, ShieldCheck, Sparkles, Workflow, Globe2, ShoppingBag, BrainCircuit, WandSparkles } from "lucide-react";

const agents = [
  ["Product Research", "Finds gaps, buyer intent, angles, offers and market opportunities."],
  ["UGC Creative", "Creates realistic UGC scripts, hooks, briefs and creator-ready concepts."],
  ["Store Builder", "Plans premium ecommerce pages, product sections and conversion flows."],
  ["SEO Growth", "Builds search-ready product, collection and content strategy."],
  ["Ads Strategist", "Creates campaign angles, offers, audiences and approval-safe launch plans."],
  ["Support Agent", "Handles customer support logic, reply direction and escalation rules."],
];

const chips = [
  "AI workforce", "Ecommerce agents", "UGC scripts", "Product pages", "Ad campaigns", "SEO", "Store strategy",
  "CRM", "Email", "Social content", "Analytics", "Global localisation", "White-label", "Approvals", "Governed execution"
];

const steps = [
  ["01", "Add business context", "Your offer, products, audience, competitors, region and brand voice become the platform’s working memory."],
  ["02", "Choose active agents", "Clients select the ecommerce agents they purchased. Enterprise can unlock orchestration and head-agent coordination."],
  ["03", "Generate premium outputs", "The system produces client-ready copy, campaign direction, scripts, product ideas, page strategy and execution plans."],
  ["04", "Approve governed actions", "High-risk spend, scaling, publishing and commercial actions stay protected until approved."],
];

export default function HomePage() {
  return (
    <main className="page">
      <nav className="nav">
        <Link href="/" className="brand">
          <span>AI</span>
          <strong>Ecommerce AI Workforce</strong>
        </Link>
        <div className="navLinks">
          <a href="#agents">Agents</a>
          <a href="#workflow">Workflow</a>
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
          <Link href="/login">Log in</Link>
          <Link href="/signup" className="navCta">Sign up</Link>
        </div>
      </nav>

      <section className="hero">
        <div className="noise" />
        <div className="heroGlow heroGlowA" />
        <div className="heroGlow heroGlowB" />

        <motion.div
          className="heroText"
          initial={{ opacity: 0, y: 26 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75 }}
        >
          <div className="eyebrow"><span /> Now live — governed ecommerce AI agents</div>
          <h1>Hire your ecommerce AI team.</h1>
          <p>
            A premium AI workforce platform for product research, UGC, ads, store pages,
            SEO, support, analytics and governed execution — built for white-label resale
            and real commercial outcomes.
          </p>
          <div className="heroActions">
            <Link href="/signup" className="primary">Start free — no card needed <ArrowRight size={18} /></Link>
            <a href="#agents" className="secondary">Explore agents</a>
          </div>
          <div className="trust">
            {["Approval-safe", "White-label", "Multi-client", "Global-ready"].map((x) => (
              <span key={x}><CheckCircle2 size={15} /> {x}</span>
            ))}
          </div>
        </motion.div>

        <motion.div
          className="heroVisual"
          initial={{ opacity: 0, scale: .94, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: .9, delay: .15 }}
        >
          <div className="orb" />
          <div className="dash">
            <div className="dashTop"><span /><span /><span /> Live execution console</div>
            {[
              ["Business Brain", "Context loaded", "100%"],
              ["UGC Creative", "Campaign brief", "Live"],
              ["Store Builder", "Landing page plan", "Ready"],
              ["Approval Layer", "Spend locked", "Safe"],
            ].map(([a,b,c]) => (
              <div className="dashRow" key={a}>
                <div><strong>{a}</strong><small>{b}</small></div>
                <em>{c}</em>
              </div>
            ))}
          </div>
          <div className="floatCard left">Product Research Agent <small>Market gaps found</small></div>
          <div className="floatCard right">Governed Approval <small>High-risk action blocked</small></div>
        </motion.div>
      </section>

      <section className="chips">
        {chips.map((chip) => <span key={chip}>{chip}</span>)}
      </section>

      <section id="agents" className="section">
        <div className="sectionHead">
          <span>Specialist AI employees</span>
          <h2>Agents that do ecommerce work, not generic chat.</h2>
          <p>Each agent has a clear role, no overlap, and can be sold individually or as a package.</p>
        </div>
        <div className="agentGrid">
          {agents.map(([title, body], i) => (
            <motion.div
              className="agentCard"
              key={title}
              initial={{ opacity: 0, y: 22 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * .05 }}
              whileHover={{ y: -8 }}
            >
              <div className="agentIcon"><Sparkles size={18} /></div>
              <h3>{title}</h3>
              <p>{body}</p>
              <button>View workflow</button>
            </motion.div>
          ))}
        </div>
      </section>

      <section id="workflow" className="section workflow">
        <div className="sectionHead">
          <span>From context to execution</span>
          <h2>Simple for clients. Powerful behind the scenes.</h2>
        </div>
        <div className="stepGrid">
          {steps.map(([n,t,b]) => (
            <div className="step" key={n}>
              <div>{n}</div>
              <h3>{t}</h3>
              <p>{b}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="features" className="featureBand">
        <div className="featureCopy">
          <span>Business Brain</span>
          <h2>The platform learns each client’s business context.</h2>
          <p>
            Agents adapt to products, offer, country, currency, language style, audience,
            buyer behaviour and brand positioning — without exposing protected internal logic.
          </p>
        </div>
        <div className="featureCards">
          {[
            [BrainCircuit, "Persistent client memory"],
            [Globe2, "Global localisation"],
            [ShieldCheck, "Governed approvals"],
            [Workflow, "Agent workflows"],
            [ShoppingBag, "Ecommerce-first outputs"],
            [WandSparkles, "Premium creative direction"],
          ].map(([Icon, label]: any) => (
            <div key={label}><Icon size={22} /> {label}</div>
          ))}
        </div>
      </section>

      <section id="pricing" className="section pricing">
        <div className="sectionHead">
          <span>Packages</span>
          <h2>Start small. Scale into a governed AI workforce.</h2>
        </div>
        <div className="priceGrid">
          {["Starter", "Growth", "Business", "Enterprise"].map((p, i) => (
            <div className={i === 2 ? "price featured" : "price"} key={p}>
              <h3>{p}</h3>
              <p>{i === 0 ? "1–3 agents" : i === 1 ? "4–7 agents" : i === 2 ? "7–10 agents" : "Full workforce"}</p>
              <ul>
                <li>Premium ecommerce agents</li>
                <li>Business context memory</li>
                <li>Governed execution</li>
                <li>{i === 3 ? "Head Agent orchestration" : "Client workspace"}</li>
              </ul>
              <Link href="/signup">Choose {p}</Link>
            </div>
          ))}
        </div>
      </section>

      <section className="final">
        <h2>Build, sell and operate a premium ecommerce AI workforce.</h2>
        <p>White-label ready, governed, client-safe and built for real business execution.</p>
        <Link href="/signup">Get started <ArrowRight size={18} /></Link>
      </section>

      <footer>
        <span>© {new Date().getFullYear()} Ecommerce AI Workforce Platform</span>
        <div>
          <Link href="/privacy-policy">Privacy</Link>
          <Link href="/terms-of-service">Terms</Link>
          <Link href="/support-request">Contact</Link>
        </div>
      </footer>

      <style jsx>{`
        .page{min-height:100vh;background:#07090d;color:#fff;font-family:Inter,ui-sans-serif,system-ui;overflow:hidden}
        .nav{height:72px;position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;padding:0 7vw;background:rgba(7,9,13,.82);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.08)}
        .brand{display:flex;align-items:center;gap:12px;color:#fff;text-decoration:none}.brand span{width:38px;height:38px;border-radius:12px;background:#6d5dfc;display:grid;place-items:center;font-weight:900}
        .navLinks{display:flex;align-items:center;gap:26px}.navLinks a{color:#cbd5e1;text-decoration:none;font-weight:800}.navCta{background:#c7ff00!important;color:#050505!important;padding:13px 18px;border-radius:16px}
        .hero{position:relative;min-height:780px;display:grid;grid-template-columns:1fr 1fr;align-items:center;padding:80px 7vw 60px;background:radial-gradient(circle at 50% 20%,rgba(100,90,255,.28),transparent 34%),linear-gradient(180deg,#0a0d18,#07090d)}
        .noise{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:74px 74px;mask-image:linear-gradient(black,transparent 92%)}
        .heroGlow{position:absolute;border-radius:999px;filter:blur(50px);opacity:.35}.heroGlowA{left:10%;top:30%;width:480px;height:480px;background:#00ffe0}.heroGlowB{right:15%;top:18%;width:560px;height:560px;background:#6d5dfc}
        .heroText{position:relative;z-index:2;max-width:720px}.eyebrow{display:inline-flex;gap:10px;align-items:center;border:1px solid rgba(199,255,0,.28);background:rgba(199,255,0,.08);border-radius:999px;padding:10px 15px;color:#c7ff00;font-size:12px;font-weight:950;letter-spacing:.12em;text-transform:uppercase}.eyebrow span{width:8px;height:8px;border-radius:99px;background:#c7ff00}
        h1{font-size:clamp(62px,8vw,118px);line-height:.88;letter-spacing:-.08em;margin:26px 0;background:linear-gradient(135deg,#fff,#a7a3ff,#36ffe6);-webkit-background-clip:text;color:transparent}
        .heroText p{font-size:21px;line-height:1.55;color:#aab3c5;max-width:650px}.heroActions{display:flex;gap:14px;margin-top:30px}.primary,.secondary{height:58px;padding:0 24px;border-radius:16px;display:inline-flex;align-items:center;gap:8px;text-decoration:none;font-weight:950}.primary{background:#c7ff00;color:#050505}.secondary{border:1px solid rgba(255,255,255,.16);color:#fff;background:rgba(255,255,255,.04)}
        .trust{display:flex;flex-wrap:wrap;gap:18px;margin-top:24px;color:#9aa5b8}.trust span{display:flex;gap:6px;align-items:center}
        .heroVisual{position:relative;height:580px}.orb{position:absolute;right:8%;top:8%;width:390px;height:390px;border-radius:42% 58% 52% 48%;background:linear-gradient(135deg,#6d5dfc,#1fd8ca);filter:drop-shadow(0 40px 90px rgba(109,93,252,.34));animation:float 8s ease-in-out infinite}
        .dash{position:absolute;right:15%;top:28%;width:350px;border-radius:28px;background:rgba(8,12,25,.88);border:1px solid rgba(255,255,255,.14);box-shadow:0 40px 100px rgba(0,0,0,.55);overflow:hidden;backdrop-filter:blur(18px)}
        .dashTop{height:48px;border-bottom:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:8px;padding:0 16px;color:#94a3b8;font-size:12px;font-weight:900}.dashTop span{width:9px;height:9px;border-radius:99px;background:#c7ff00}.dashTop span:nth-child(2){background:#00d8ff}.dashTop span:nth-child(3){background:#ff4cb4}
        .dashRow{margin:14px;padding:14px;border-radius:16px;background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.09);display:flex;justify-content:space-between}.dashRow strong{display:block}.dashRow small{color:#94a3b8}.dashRow em{color:#c7ff00;font-style:normal;font-weight:950}
        .floatCard{position:absolute;padding:18px 20px;border-radius:22px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);backdrop-filter:blur(18px);box-shadow:0 28px 70px rgba(0,0,0,.34);font-weight:950}.floatCard small{display:block;color:#aab3c5;margin-top:7px}.left{left:2%;top:22%}.right{right:0;top:16%}
        .chips{padding:36px 7vw;display:flex;flex-wrap:wrap;gap:12px;justify-content:center}.chips span{background:#171b22;border:1px solid rgba(255,255,255,.08);padding:12px 16px;border-radius:999px;color:#cbd5e1;font-weight:850}
        .section{padding:92px 7vw}.sectionHead{text-align:center;max-width:860px;margin:0 auto 44px}.sectionHead span,.featureCopy span{color:#c7ff00;text-transform:uppercase;font-weight:950;letter-spacing:.12em;font-size:12px}.sectionHead h2,.featureCopy h2,.final h2{font-size:clamp(42px,6vw,76px);line-height:.94;letter-spacing:-.07em;margin:16px 0}.sectionHead p,.featureCopy p,.final p{color:#aab3c5;font-size:18px;line-height:1.6}
        .agentGrid,.priceGrid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.agentCard,.price{background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(255,255,255,.035));border:1px solid rgba(255,255,255,.10);border-radius:28px;padding:26px;box-shadow:0 28px 70px rgba(0,0,0,.25)}.agentIcon{width:48px;height:48px;border-radius:16px;background:rgba(199,255,0,.12);color:#c7ff00;display:grid;place-items:center}.agentCard h3,.price h3{font-size:24px}.agentCard p,.price p,.step p{color:#aab3c5;line-height:1.55}.agentCard button{margin-top:14px;background:#c7ff00;color:#050505;border:0;border-radius:14px;padding:12px 15px;font-weight:950}
        .stepGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.step{padding:24px;border-radius:26px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.10)}.step div{width:46px;height:46px;border-radius:16px;background:#6d5dfc;display:grid;place-items:center;font-weight:950}
        .featureBand{margin:40px 7vw;padding:54px;border-radius:34px;background:#c7ff00;color:#050505;display:grid;grid-template-columns:1fr 1fr;gap:34px}.featureCopy p{color:#1f2937}.featureCards{display:grid;grid-template-columns:1fr 1fr;gap:12px}.featureCards div{background:rgba(0,0,0,.08);border:1px solid rgba(0,0,0,.10);border-radius:18px;padding:18px;font-weight:950;display:flex;gap:10px;align-items:center}
        .price.featured{border-color:#c7ff00;box-shadow:0 0 80px rgba(199,255,0,.14)}.price ul{padding-left:18px;color:#cbd5e1;line-height:1.9}.price a{display:flex;justify-content:center;margin-top:20px;background:#c7ff00;color:#050505;text-decoration:none;border-radius:16px;padding:14px;font-weight:950}
        .final{text-align:center;padding:110px 7vw}.final a{display:inline-flex;gap:8px;align-items:center;background:#c7ff00;color:#050505;text-decoration:none;border-radius:18px;padding:18px 24px;font-weight:950}
        footer{display:flex;justify-content:space-between;padding:28px 7vw;border-top:1px solid rgba(255,255,255,.08);color:#94a3b8}footer a{color:#cbd5e1;margin-left:18px;text-decoration:none}
        @keyframes float{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-22px) rotate(8deg)}}
        @media(max-width:960px){.hero,.featureBand{grid-template-columns:1fr}.heroVisual{height:460px}.agentGrid,.priceGrid,.stepGrid{grid-template-columns:1fr}.navLinks a:not(.navCta){display:none}}
      `}</style>
    </main>
  );
}
''', encoding="utf-8")

print("LANDING_PAGE_REBUILT_SINTRA_HIGGSFIELD_STYLE")
print(f"Backup: {backup}")