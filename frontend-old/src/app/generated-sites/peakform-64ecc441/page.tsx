
export default function GeneratedSite() {
  return (
    <main className="shell">

      <section className="hero">

        <div className="left">

          <div className="eyebrow">
            Premium AI-generated React website
          </div>

          <h1>Train Smarter. Move Stronger. Stay Consistent.</h1>

          <p>Premium boutique fitness experience built for high-performance members.</p>

          <div className="actions">
            <button className="primary">
              Launch Experience
            </button>

            <button className="secondary">
              View Architecture
            </button>
          </div>

        </div>

        <div className="right">

          <div className="glass-card card-a"></div>
          <div className="glass-card card-b"></div>

          <div className="product-3d">
            <div className="product-inner">
              <span>PeakForm</span>
              <strong>PREMIUM</strong>
            </div>
          </div>

        </div>

      </section>

      <section className="features">

        <div className="feature">
          <h3>3D Motion</h3>
          <p>Animated premium visual architecture.</p>
        </div>

        <div className="feature">
          <h3>Glass UI</h3>
          <p>Glassmorphism layered conversion design.</p>
        </div>

        <div className="feature">
          <h3>Responsive</h3>
          <p>Desktop/mobile premium layouts.</p>
        </div>

        <div className="feature">
          <h3>React Generated</h3>
          <p>Dynamic generated Next.js route.</p>
        </div>

      </section>

      <section className="deep-section">

        <div className="section-copy">
          <span>Conversion Architecture</span>
          <h2>Built as a full buying journey, not a single hero block.</h2>
          <p>
            This generated website includes a structured path from premium positioning
            through proof, offer logic, objection handling, and final conversion.
          </p>
        </div>

        <div className="architecture-grid">
          <div>
            <strong>01</strong>
            <h3>Premium Positioning</h3>
            <p>Industry-specific headline, value promise, and visual direction.</p>
          </div>
          <div>
            <strong>02</strong>
            <h3>Offer System</h3>
            <p>Conversion-focused offer section ready for client-specific campaigns.</p>
          </div>
          <div>
            <strong>03</strong>
            <h3>Trust Proof</h3>
            <p>Review cards, credibility points, visual proof slots, and authority blocks.</p>
          </div>
          <div>
            <strong>04</strong>
            <h3>Action Path</h3>
            <p>Sticky CTA, section anchors, and final conversion prompts.</p>
          </div>
        </div>

      </section>

      <section className="showcase">

        <div className="showcase-card large">
          <span>Premium Visual Block</span>
          <h2>Generated brand scene with animated depth, glass surfaces, and motion hierarchy.</h2>
        </div>

        <div className="showcase-stack">
          <div className="mini-panel">
            <h3>Audience</h3>
            <p>High-intent buyers matched to the requested industry.</p>
          </div>
          <div className="mini-panel">
            <h3>Offer</h3>
            <p>Prepared launch offer and campaign structure.</p>
          </div>
          <div className="mini-panel">
            <h3>Proof</h3>
            <p>Trust blocks and testimonial placeholders.</p>
          </div>
        </div>

      </section>

      <section className="faq-section">
        <div>
          <span>Launch Readiness</span>
          <h2>Generated as a production-style React draft.</h2>
        </div>

        <div className="faq-list">
          <div>
            <h3>Is this static HTML?</h3>
            <p>No. This is a generated Next.js React route with page-level component structure.</p>
          </div>
          <div>
            <h3>Is it published live for a client?</h3>
            <p>No. It remains a draft until owner approval and deployment/CMS connection are confirmed.</p>
          </div>
          <div>
            <h3>Can it become multi-page?</h3>
            <p>Yes. The next runtime step can generate about, services, product, and contact pages.</p>
          </div>
        </div>
      </section>

      <style>{`

        * {
          box-sizing:border-box;
        }

        body {
          margin:0;
          background:#070b17;
          font-family:Inter,sans-serif;
        }

        .shell {
          min-height:100vh;
          overflow:hidden;
          color:white;

          background:
            radial-gradient(circle at top left,#22d3ee55,transparent 35%),
            radial-gradient(circle at bottom right,#ffffff22,transparent 25%),
            linear-gradient(135deg,#070b17,#111827,#1e0f2f);
        }

        .hero {
          display:grid;
          grid-template-columns:1fr 1fr;
          gap:40px;
          align-items:center;
          min-height:100vh;
          padding:80px;
        }

        .eyebrow {
          display:inline-block;
          padding:12px 18px;
          border-radius:999px;
          backdrop-filter:blur(20px);
          background:rgba(255,255,255,.08);
          border:1px solid rgba(255,255,255,.16);
          color:#22d3ee;
          font-weight:700;
        }

        h1 {
          font-size:92px;
          line-height:.88;
          letter-spacing:-0.06em;
          margin:24px 0;
          max-width:720px;
        }

        p {
          font-size:22px;
          line-height:1.7;
          color:#dbe3f0;
          max-width:700px;
        }

        .actions {
          display:flex;
          gap:16px;
          margin-top:34px;
        }

        button {
          border:none;
          cursor:pointer;
          border-radius:999px;
          font-weight:800;
          padding:18px 28px;
          font-size:16px;
        }

        .primary {
          background:white;
          color:black;
        }

        .secondary {
          background:rgba(255,255,255,.08);
          border:1px solid rgba(255,255,255,.16);
          color:white;
          backdrop-filter:blur(20px);
        }

        .right {
          position:relative;
          height:760px;
          perspective:1400px;
        }

        .glass-card {
          position:absolute;
          border-radius:40px;
          backdrop-filter:blur(26px);
          background:rgba(255,255,255,.10);
          border:1px solid rgba(255,255,255,.16);
          box-shadow:0 40px 120px rgba(0,0,0,.35);
        }

        .card-a {
          width:520px;
          height:520px;
          right:40px;
          top:80px;
          animation:floatA 8s ease-in-out infinite;
        }

        .card-b {
          width:240px;
          height:240px;
          left:0;
          bottom:80px;
          animation:floatB 6s ease-in-out infinite;
        }

        .product-3d {
          position:absolute;
          left:50%;
          top:50%;
          transform:
            translate(-50%,-50%)
            rotateY(-18deg)
            rotateX(10deg);

          width:320px;
          height:520px;

          border-radius:42px;

          background:
            linear-gradient(
              145deg,
              rgba(255,255,255,.8),
              rgba(255,255,255,.08)
            );

          backdrop-filter:blur(30px);

          border:1px solid rgba(255,255,255,.24);

          box-shadow:0 60px 160px rgba(0,0,0,.45);

          animation:productFloat 6s ease-in-out infinite;
        }

        .product-inner {
          height:100%;
          display:flex;
          flex-direction:column;
          justify-content:center;
          align-items:center;
          text-align:center;
        }

        .product-inner span {
          letter-spacing:.3em;
          font-weight:900;
          margin-bottom:20px;
        }

        .product-inner strong {
          font-size:64px;
          line-height:.9;
        }

        .features {
          display:grid;
          grid-template-columns:repeat(4,1fr);
          gap:20px;
          padding:0 80px 80px;
        }

        .feature {
          padding:28px;
          border-radius:30px;
          backdrop-filter:blur(24px);
          background:rgba(255,255,255,.08);
          border:1px solid rgba(255,255,255,.12);
        }

        .feature h3 {
          margin-top:0;
          font-size:24px;
        }

        .feature p {
          font-size:16px;
        }

        .deep-section {
          max-width:1280px;
          margin:0 auto;
          padding:80px;
          display:grid;
          grid-template-columns:.85fr 1.15fr;
          gap:34px;
          align-items:start;
        }

        .section-copy {
          position:sticky;
          top:40px;
        }

        .section-copy span,
        .showcase-card span,
        .faq-section span {
          color:#22d3ee;
          font-weight:900;
        }

        .section-copy h2,
        .showcase-card h2,
        .faq-section h2 {
          font-size:56px;
          line-height:.95;
          letter-spacing:-.055em;
          margin:16px 0;
        }

        .architecture-grid {
          display:grid;
          grid-template-columns:1fr 1fr;
          gap:18px;
        }

        .architecture-grid div {
          min-height:240px;
          padding:28px;
          border-radius:34px;
          background:rgba(255,255,255,.08);
          border:1px solid rgba(255,255,255,.14);
          backdrop-filter:blur(24px);
          box-shadow:0 30px 100px rgba(0,0,0,.22);
        }

        .architecture-grid strong {
          color:#22d3ee;
          font-size:14px;
        }

        .architecture-grid h3 {
          font-size:26px;
          margin:18px 0 10px;
        }

        .showcase {
          max-width:1280px;
          margin:0 auto;
          padding:40px 80px 90px;
          display:grid;
          grid-template-columns:1.1fr .9fr;
          gap:24px;
        }

        .showcase-card {
          min-height:520px;
          border-radius:44px;
          padding:44px;
          background:
            radial-gradient(circle at 20% 20%,#22d3ee66,transparent 35%),
            linear-gradient(135deg,rgba(255,255,255,.18),rgba(255,255,255,.05));
          border:1px solid rgba(255,255,255,.18);
          backdrop-filter:blur(26px);
          box-shadow:0 40px 120px rgba(0,0,0,.32);
        }

        .showcase-stack {
          display:grid;
          gap:18px;
        }

        .mini-panel {
          padding:28px;
          border-radius:32px;
          background:rgba(255,255,255,.08);
          border:1px solid rgba(255,255,255,.14);
          backdrop-filter:blur(24px);
        }

        .faq-section {
          max-width:1120px;
          margin:0 auto 140px;
          padding:50px;
          border-radius:44px;
          background:rgba(255,255,255,.08);
          border:1px solid rgba(255,255,255,.14);
          backdrop-filter:blur(24px);
        }

        .faq-list {
          display:grid;
          gap:16px;
          margin-top:30px;
        }

        .faq-list div {
          padding:22px;
          border-radius:26px;
          background:rgba(255,255,255,.07);
          border:1px solid rgba(255,255,255,.1);
        }

        @keyframes productFloat {
          0%,100% {
            transform:
              translate(-50%,-50%)
              rotateY(-18deg)
              rotateX(10deg)
              translateY(0px);
          }

          50% {
            transform:
              translate(-50%,-50%)
              rotateY(-8deg)
              rotateX(16deg)
              translateY(-26px);
          }
        }

        @keyframes floatA {
          0%,100% { transform:translateY(0px); }
          50% { transform:translateY(-24px); }
        }

        @keyframes floatB {
          0%,100% { transform:translateY(0px); }
          50% { transform:translateY(18px); }
        }

        @media (max-width:980px) {

          .hero {
            grid-template-columns:1fr;
            padding:40px;
          }

          h1 {
            font-size:64px;
          }

          .features {
            grid-template-columns:1fr 1fr;
            padding:40px;
          }

          .deep-section,
          .showcase {
            grid-template-columns:1fr;
            padding:40px;
          }

          .section-copy {
            position:relative;
            top:auto;
          }

          .architecture-grid {
            grid-template-columns:1fr;
          }

        }

      `}</style>

    </main>
  )
}
