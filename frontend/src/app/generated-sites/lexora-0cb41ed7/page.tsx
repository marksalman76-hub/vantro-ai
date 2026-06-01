
export default function GeneratedSite() {
  return (
    <main className="page legal">
      <section className="legalHero">
        <div className="trustMark">LEX</div>
        <div><div className="pill">Legal trust conversion</div><h1>Clear Legal Guidance When The Stakes Matter.</h1><p>A calm trust-first legal site for confidential enquiries, service clarity, consultation requests, and authority building.</p><button className="btn">Request Consultation</button></div>
      </section>
      <section className="consultationFlow"><div>Confidential Enquiry</div><div>Case Assessment</div><div>Clear Next Step</div></section>
      <section className="legalProof glass"><h2>Built for authority, privacy, and calm decision-making.</h2><p>Service clarity, trust signals, and consultation conversion without aggressive sales styling.</p></section>
      <style>{`
        
      * { box-sizing: border-box; }
      body { margin: 0; background: #050713; }
      .page { min-height: 100vh; color: white; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; overflow-x: hidden; }
      .pill { display: inline-flex; padding: 10px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.08); color: #f5c76b; font-weight: 900; }
      .btn { border: none; border-radius: 999px; padding: 17px 24px; font-weight: 950; background: white; color: #020617; cursor: pointer; }
      .ghost { background: rgba(255,255,255,.08); color: white; border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(20px); }
      .glass { background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14); backdrop-filter: blur(24px); box-shadow: 0 30px 100px rgba(0,0,0,.28); }
      @keyframes floaty { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-22px); } }
      @keyframes glow { 0%,100% { opacity: .55; transform: scale(1); } 50% { opacity: .92; transform: scale(1.08); } }
      @keyframes slide { 0% { transform: translateX(-20px); opacity: .45; } 50% { transform: translateX(20px); opacity: 1; } 100% { transform: translateX(-20px); opacity: .45; } }
    
        .legal { background: radial-gradient(circle at 75% 15%, #f5c76b33, transparent 28%), linear-gradient(135deg,#080807,#17120a,#111827); }
        .legalHero { min-height: 100vh; display: grid; grid-template-columns: .55fr 1fr; gap: 60px; padding: 90px; align-items: center; }
        .trustMark { width: 360px; height: 520px; border-radius: 40px; display: grid; place-items: center; font-size: 96px; font-weight: 950; color: #f5c76b; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.06); box-shadow: 0 40px 120px rgba(0,0,0,.36); }
        h1 { font-size: clamp(58px, 7vw, 104px); line-height: .9; letter-spacing: -.07em; }
        p { color: #e5e7eb; font-size: 22px; line-height: 1.65; }
        .consultationFlow { padding: 0 90px 60px; display: grid; grid-template-columns: repeat(3,1fr); gap: 18px; }
        .consultationFlow div { padding: 30px; border-radius: 28px; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14); font-weight: 900; }
        .legalProof { margin: 0 90px 120px; border-radius: 40px; padding: 50px; }
        .legalProof h2 { font-size: 54px; line-height: .95; letter-spacing: -.05em; }
      `}</style>
    </main>
  );
}
