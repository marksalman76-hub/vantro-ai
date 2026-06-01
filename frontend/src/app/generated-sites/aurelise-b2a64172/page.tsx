
export default function GeneratedSite() {
  return (
    <main className="page beauty">
      <aside className="sideRail"><span>Aurelise</span><i>01 / Ritual</i><i>02 / Science</i><i>03 / Proof</i></aside>
      <section className="beautyHero">
        <div className="copy">
          <div className="pill">Beauty editorial commerce</div>
          <h1>Clinical Radiance, Reimagined As Luxury Ritual.</h1>
          <p>A cinematic beauty ecommerce experience built around ingredient science, luxury ritual, proof, and premium launch conversion.</p>
          <div className="actions"><button className="btn">Shop Launch Collection</button><button className="btn ghost">Explore Science</button></div>
        </div>
        <div className="ritualScene">
          <div className="halo"></div><div className="serumBottle"><small>Aurelise</small><strong>RADIANCE</strong></div>
          <div className="ingredient one">Peptide Complex</div><div className="ingredient two">Barrier Repair</div>
        </div>
      </section>
      <section className="editorialGrid">
        <div className="large glass"><span>Ingredient Science</span><h2>Clinical-grade formulation presented as an elevated daily ritual.</h2></div>
        <div className="tall glass"><h3>Before / After Proof</h3><p>Generated visual proof section for customer transformation storytelling.</p></div>
        <div className="wide glass"><h3>Launch Offer</h3><p>15% off first order, free express shipping, complimentary sample ritual over $150.</p></div>
      </section>
      <style>{`
        
      * { box-sizing: border-box; }
      body { margin: 0; background: #050713; }
      .page { min-height: 100vh; color: white; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; overflow-x: hidden; }
      .pill { display: inline-flex; padding: 10px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.08); color: #f472b6; font-weight: 900; }
      .btn { border: none; border-radius: 999px; padding: 17px 24px; font-weight: 950; background: white; color: #020617; cursor: pointer; }
      .ghost { background: rgba(255,255,255,.08); color: white; border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(20px); }
      .glass { background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14); backdrop-filter: blur(24px); box-shadow: 0 30px 100px rgba(0,0,0,.28); }
      @keyframes floaty { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-22px); } }
      @keyframes glow { 0%,100% { opacity: .55; transform: scale(1); } 50% { opacity: .92; transform: scale(1.08); } }
      @keyframes slide { 0% { transform: translateX(-20px); opacity: .45; } 50% { transform: translateX(20px); opacity: 1; } 100% { transform: translateX(-20px); opacity: .45; } }
    
        .beauty { background: radial-gradient(circle at 25% 10%, #f472b655, transparent 34%), linear-gradient(135deg,#090712,#17101f,#040712); }
        .sideRail { position: fixed; left: 0; top: 0; bottom: 0; width: 92px; border-right: 1px solid rgba(255,255,255,.12); display: flex; flex-direction: column; gap: 34px; align-items: center; padding: 28px 12px; writing-mode: vertical-rl; font-weight: 900; color: #fff9; }
        .beautyHero { min-height: 100vh; padding: 90px 80px 70px 150px; display: grid; grid-template-columns: .9fr 1.1fr; gap: 60px; align-items: center; }
        h1 { font-size: clamp(62px, 8vw, 118px); line-height: .86; letter-spacing: -.08em; margin: 24px 0; }
        p { color: #dbe3f0; font-size: 22px; line-height: 1.65; max-width: 720px; }
        .actions { display: flex; gap: 14px; margin-top: 32px; }
        .ritualScene { position: relative; height: 720px; }
        .halo { position: absolute; inset: 80px; border-radius: 999px; background: radial-gradient(circle, #f472b688, transparent 58%); filter: blur(8px); animation: glow 6s infinite; }
        .serumBottle { position: absolute; left: 38%; top: 18%; width: 310px; height: 520px; border-radius: 58px; display: grid; place-items: center; text-align: center; background: linear-gradient(145deg, rgba(255,255,255,.76), rgba(255,255,255,.1), #f472b688); border: 1px solid rgba(255,255,255,.32); backdrop-filter: blur(30px); transform: rotateY(-18deg) rotateX(8deg); animation: floaty 6s infinite; }
        .serumBottle small { letter-spacing: .28em; font-weight: 950; }
        .serumBottle strong { display: block; font-size: 46px; margin-top: 14px; }
        .ingredient { position: absolute; padding: 20px; border-radius: 28px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(22px); font-weight: 900; }
        .ingredient.one { left: 0; top: 120px; } .ingredient.two { right: 20px; bottom: 150px; }
        .editorialGrid { padding: 40px 80px 120px 150px; display: grid; grid-template-columns: 1.1fr .9fr; gap: 22px; }
        .editorialGrid > div { border-radius: 42px; padding: 40px; min-height: 260px; }
        .large { min-height: 520px !important; } .large h2 { font-size: 58px; line-height: .92; letter-spacing: -.06em; }
        .wide { grid-column: span 2; }
      `}</style>
    </main>
  );
}
