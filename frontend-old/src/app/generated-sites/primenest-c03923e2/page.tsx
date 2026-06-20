
export default function GeneratedSite() {
  return (
    <main className="page property">
      <section className="propertyHero">
        <div className="listingPanel"><span>Featured Waterfront Campaign</span><h1>Waterfront Prestige, Presented To Command Attention.</h1><p>A cinematic property showcase for premium listings, appraisal enquiries, suburb authority, and high-value buyer conversion.</p><button className="btn">Book Appraisal</button></div>
        <div className="gallery">
          <div className="photo main"></div><div className="photo side"></div><div className="valuation glass">Appraisal pathway ready</div>
        </div>
      </section>
      <section className="propertyProof">
        <div><strong>01</strong><h3>Prestige Story</h3></div><div><strong>02</strong><h3>Buyer Enquiry Flow</h3></div><div><strong>03</strong><h3>Suburb Authority</h3></div>
      </section>
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
    
        .property { background: radial-gradient(circle at 80% 10%, #f5c76b44, transparent 30%), linear-gradient(135deg,#0b0906,#1c160d,#111827); }
        .propertyHero { min-height: 100vh; display: grid; grid-template-columns: .72fr 1.28fr; gap: 42px; padding: 90px; align-items: center; }
        .listingPanel { border-left: 3px solid #f5c76b; padding-left: 34px; }
        h1 { font-size: clamp(56px, 7vw, 96px); line-height: .9; letter-spacing: -.07em; }
        p { color: #e7dfd0; font-size: 21px; line-height: 1.65; }
        .gallery { position: relative; height: 700px; }
        .photo { position: absolute; border-radius: 42px; background: linear-gradient(135deg,#2a2418,#8c6b34,#0f172a); border: 1px solid rgba(255,255,255,.16); box-shadow: 0 40px 110px rgba(0,0,0,.42); }
        .photo.main { inset: 20px 100px 120px 20px; } .photo.side { right: 10px; bottom: 40px; width: 360px; height: 320px; animation: floaty 7s infinite; }
        .valuation { position: absolute; right: 80px; top: 70px; padding: 24px; border-radius: 28px; font-weight: 900; }
        .propertyProof { padding: 0 90px 120px; display: grid; grid-template-columns: repeat(3,1fr); gap: 18px; }
        .propertyProof div { min-height: 230px; padding: 30px; border-radius: 32px; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14); }
        .propertyProof strong { color: #f5c76b; }
      `}</style>
    </main>
  );
}
