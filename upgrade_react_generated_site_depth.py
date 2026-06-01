from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "react_website_generation_runtime.py"
BACKUP = ROOT / "backups" / f"react_generated_site_depth_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "react_website_generation_runtime.py")

s = TARGET.read_text(encoding="utf-8")

s = s.replace(
'''      <section className="features">

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

      </section>''',
'''      <section className="features">

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
      </section>'''
)

s = s.replace(
'''        .features {{
          display:grid;
          grid-template-columns:repeat(4,1fr);
          gap:20px;
          padding:0 80px 120px;
        }}''',
'''        .features {{
          display:grid;
          grid-template-columns:repeat(4,1fr);
          gap:20px;
          padding:0 80px 80px;
        }}'''
)

s = s.replace(
'''        .feature p {{
          font-size:16px;
        }}''',
'''        .feature p {{
          font-size:16px;
        }}

        .deep-section {{
          max-width:1280px;
          margin:0 auto;
          padding:80px;
          display:grid;
          grid-template-columns:.85fr 1.15fr;
          gap:34px;
          align-items:start;
        }}

        .section-copy {{
          position:sticky;
          top:40px;
        }}

        .section-copy span,
        .showcase-card span,
        .faq-section span {{
          color:{accent};
          font-weight:900;
        }}

        .section-copy h2,
        .showcase-card h2,
        .faq-section h2 {{
          font-size:56px;
          line-height:.95;
          letter-spacing:-.055em;
          margin:16px 0;
        }}

        .architecture-grid {{
          display:grid;
          grid-template-columns:1fr 1fr;
          gap:18px;
        }}

        .architecture-grid div {{
          min-height:240px;
          padding:28px;
          border-radius:34px;
          background:rgba(255,255,255,.08);
          border:1px solid rgba(255,255,255,.14);
          backdrop-filter:blur(24px);
          box-shadow:0 30px 100px rgba(0,0,0,.22);
        }}

        .architecture-grid strong {{
          color:{accent};
          font-size:14px;
        }}

        .architecture-grid h3 {{
          font-size:26px;
          margin:18px 0 10px;
        }}

        .showcase {{
          max-width:1280px;
          margin:0 auto;
          padding:40px 80px 90px;
          display:grid;
          grid-template-columns:1.1fr .9fr;
          gap:24px;
        }}

        .showcase-card {{
          min-height:520px;
          border-radius:44px;
          padding:44px;
          background:
            radial-gradient(circle at 20% 20%,{accent}66,transparent 35%),
            linear-gradient(135deg,rgba(255,255,255,.18),rgba(255,255,255,.05));
          border:1px solid rgba(255,255,255,.18);
          backdrop-filter:blur(26px);
          box-shadow:0 40px 120px rgba(0,0,0,.32);
        }}

        .showcase-stack {{
          display:grid;
          gap:18px;
        }}

        .mini-panel {{
          padding:28px;
          border-radius:32px;
          background:rgba(255,255,255,.08);
          border:1px solid rgba(255,255,255,.14);
          backdrop-filter:blur(24px);
        }}

        .faq-section {{
          max-width:1120px;
          margin:0 auto 140px;
          padding:50px;
          border-radius:44px;
          background:rgba(255,255,255,.08);
          border:1px solid rgba(255,255,255,.14);
          backdrop-filter:blur(24px);
        }}

        .faq-list {{
          display:grid;
          gap:16px;
          margin-top:30px;
        }}

        .faq-list div {{
          padding:22px;
          border-radius:26px;
          background:rgba(255,255,255,.07);
          border:1px solid rgba(255,255,255,.1);
        }}'''
)

s = s.replace(
'''          .features {{
            grid-template-columns:1fr 1fr;
            padding:40px;
          }}''',
'''          .features {{
            grid-template-columns:1fr 1fr;
            padding:40px;
          }}

          .deep-section,
          .showcase {{
            grid-template-columns:1fr;
            padding:40px;
          }}

          .section-copy {{
            position:relative;
            top:auto;
          }}

          .architecture-grid {{
            grid-template-columns:1fr;
          }}'''
)

TARGET.write_text(s, encoding="utf-8")
print("REACT_GENERATED_SITE_DEPTH_UPGRADED")
print("Backup:", BACKUP)