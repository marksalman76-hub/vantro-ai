"use client";

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

export default function HomePage() {
  return (
    <main>
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
        @media(max-width:900px){.nav{height:auto;padding:14px 20px}.navLinks{gap:14px}.navLinks a:not(.navBtn){display:none}.hero{padding-top:110px}.numbers{grid-template-columns:repeat(2,1fr)}.platform{grid-template-columns:1fr;padding:80px 6%}.context{grid-template-columns:1fr}.section{padding:80px 6%}}
      `}</style>
    </main>
  );
}
