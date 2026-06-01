
export default function GeneratedSite() {
  return (
    <main className="shell">

      <section className="hero">

        <div className="left">

          <div className="eyebrow">
            Premium AI-generated React website
          </div>

          <h1>Clinical Radiance, Reimagined As Luxury Ritual.</h1>

          <p>Premium skincare experience with motion-driven luxury conversion design.</p>

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
              <span>Aurelise</span>
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
            radial-gradient(circle at top left,#f472b655,transparent 35%),
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
          color:#f472b6;
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
          padding:0 80px 120px;
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

        }

      `}</style>

    </main>
  )
}
