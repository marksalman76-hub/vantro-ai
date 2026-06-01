
export default function GeneratedSite() {
  return (
    <main className="page saas">
      <section className="dashboardHero">
        <div><div className="pill">SaaS command centre</div><h1>Your Operating System For Scalable Execution.</h1><p>A dashboard-led SaaS site designed around workflow clarity, operational visibility, automation proof, and demo conversion.</p><button className="btn">Book Demo</button></div>
        <div className="dashboard glass">
          <div className="topbar"></div><div className="chart"></div><div className="modules"><i></i><i></i><i></i><i></i></div>
        </div>
      </section>
      <section className="orbitModules"><div>Automation</div><div>Analytics</div><div>Security</div><div>Workflow</div></section>
      <style>{`
        
      * { box-sizing: border-box; }
      body { margin: 0; background: #050713; }
      .page { min-height: 100vh; color: white; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; overflow-x: hidden; }
      .pill { display: inline-flex; padding: 10px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.08); color: #a78bfa; font-weight: 900; }
      .btn { border: none; border-radius: 999px; padding: 17px 24px; font-weight: 950; background: white; color: #020617; cursor: pointer; }
      .ghost { background: rgba(255,255,255,.08); color: white; border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(20px); }
      .glass { background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14); backdrop-filter: blur(24px); box-shadow: 0 30px 100px rgba(0,0,0,.28); }
      @keyframes floaty { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-22px); } }
      @keyframes glow { 0%,100% { opacity: .55; transform: scale(1); } 50% { opacity: .92; transform: scale(1.08); } }
      @keyframes slide { 0% { transform: translateX(-20px); opacity: .45; } 50% { transform: translateX(20px); opacity: 1; } 100% { transform: translateX(-20px); opacity: .45; } }
    
        .saas { background: radial-gradient(circle at 15% 15%, #a78bfa55, transparent 30%), linear-gradient(135deg,#050816,#111827,#1e1b4b); }
        .dashboardHero { min-height: 100vh; display: grid; grid-template-columns: .9fr 1.1fr; gap: 50px; padding: 80px; align-items: center; }
        h1 { font-size: clamp(60px, 8vw, 110px); line-height: .86; letter-spacing: -.08em; }
        p { color: #dbe3f0; font-size: 22px; line-height: 1.6; }
        .dashboard { height: 620px; border-radius: 38px; padding: 28px; display: grid; grid-template-rows: 60px 1fr 160px; gap: 20px; animation: floaty 7s infinite; }
        .topbar,.chart,.modules i { border-radius: 22px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.14); }
        .chart { background: radial-gradient(circle at 30% 30%, #a78bfa66, transparent 40%), rgba(255,255,255,.08); }
        .modules { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; }
        .orbitModules { padding: 0 80px 120px; display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; }
        .orbitModules div { padding: 30px; border-radius: 30px; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14); font-weight: 900; }
      `}</style>
    </main>
  );
}
