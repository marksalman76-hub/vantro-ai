
export default function GeneratedSite() {
  return (
    <main className="page fitness">
      <section className="scoreHero">
        <div className="metricWall">
          <div className="metric big">07<span>DAY TRIAL</span></div><div className="metric">1:1<span>GOAL MAP</span></div><div className="metric">24/7<span>BOOKINGS</span></div>
        </div>
        <div className="fitnessCopy">
          <div className="pill">Performance studio landing</div><h1>Train Smarter. Move Stronger. Stay Consistent.</h1><p>A kinetic studio landing page built around trial bookings, coaching confidence, and performance progression.</p>
          <button className="btn">Book Trial Session</button>
        </div>
      </section>
      <section className="programs">
        <div className="program glass"><h3>Strength Track</h3><p>Progressive training blocks.</p></div>
        <div className="program glass"><h3>Conditioning</h3><p>Kinetic class schedule module.</p></div>
        <div className="program glass"><h3>Recovery</h3><p>Premium retention and habit loop.</p></div>
      </section>
      <style>{`
        
      * { box-sizing: border-box; }
      body { margin: 0; background: #050713; }
      .page { min-height: 100vh; color: white; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; overflow-x: hidden; }
      .pill { display: inline-flex; padding: 10px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.08); color: #22d3ee; font-weight: 900; }
      .btn { border: none; border-radius: 999px; padding: 17px 24px; font-weight: 950; background: white; color: #020617; cursor: pointer; }
      .ghost { background: rgba(255,255,255,.08); color: white; border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(20px); }
      .glass { background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14); backdrop-filter: blur(24px); box-shadow: 0 30px 100px rgba(0,0,0,.28); }
      @keyframes floaty { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-22px); } }
      @keyframes glow { 0%,100% { opacity: .55; transform: scale(1); } 50% { opacity: .92; transform: scale(1.08); } }
      @keyframes slide { 0% { transform: translateX(-20px); opacity: .45; } 50% { transform: translateX(20px); opacity: 1; } 100% { transform: translateX(-20px); opacity: .45; } }
    
        .fitness { background: radial-gradient(circle at 18% 22%, #22d3ee55, transparent 28%), linear-gradient(135deg,#020617,#07111f,#111827); }
        .scoreHero { min-height: 100vh; display: grid; grid-template-columns: .9fr 1.1fr; gap: 40px; padding: 80px; align-items: center; }
        .metricWall { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; transform: rotate(-2deg); }
        .metric { min-height: 220px; border-radius: 34px; display: flex; flex-direction: column; justify-content: center; padding: 30px; background: #071827; border: 1px solid #22d3ee66; font-size: 56px; font-weight: 950; box-shadow: 0 30px 90px rgba(0,0,0,.36); animation: floaty 7s infinite; }
        .metric.big { grid-column: span 2; min-height: 300px; font-size: 120px; color: #22d3ee; }
        .metric span { display: block; font-size: 16px; letter-spacing: .22em; color: #dbeafe; }
        h1 { font-size: clamp(62px, 8vw, 112px); line-height: .86; letter-spacing: -.08em; }
        p { color: #cbd5e1; font-size: 22px; line-height: 1.6; max-width: 700px; }
        .programs { padding: 30px 80px 120px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
        .program { padding: 34px; border-radius: 34px; min-height: 280px; }
      `}</style>
    </main>
  );
}
