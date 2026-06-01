from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "react_website_generation_runtime.py"
BACKUP = ROOT / "backups" / f"distinct_layout_engine_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "react_website_generation_runtime.py")

code = r'''
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[3]
GENERATED_ROOT = ROOT / "frontend" / "src" / "app" / "generated-sites"


def _pick_strategy(task: str):
    lower = task.lower()

    if "fitness" in lower or "gym" in lower:
        return {
            "brand": "PeakForm",
            "industry": "fitness",
            "layout_blueprint": "performance-studio-landing",
            "accent": "#22d3ee",
            "headline": "Train Smarter. Move Stronger. Stay Consistent.",
            "subheadline": "A kinetic studio landing page built around trial bookings, coaching confidence, and performance progression.",
            "cta": "Book Trial Session",
        }

    if "real estate" in lower or "property" in lower or "waterfront" in lower:
        return {
            "brand": "PrimeNest",
            "industry": "real estate",
            "layout_blueprint": "luxury-property-showcase",
            "accent": "#f5c76b",
            "headline": "Waterfront Prestige, Presented To Command Attention.",
            "subheadline": "A cinematic property showcase for premium listings, appraisal enquiries, suburb authority, and high-value buyer conversion.",
            "cta": "Book Appraisal",
        }

    if "saas" in lower or "software" in lower or "platform" in lower:
        return {
            "brand": "Nexora",
            "industry": "software",
            "layout_blueprint": "saas-command-centre",
            "accent": "#a78bfa",
            "headline": "Your Operating System For Scalable Execution.",
            "subheadline": "A dashboard-led SaaS site designed around workflow clarity, operational visibility, automation proof, and demo conversion.",
            "cta": "Book Demo",
        }

    if "legal" in lower or "law" in lower:
        return {
            "brand": "Lexora",
            "industry": "legal services",
            "layout_blueprint": "legal-trust-conversion",
            "accent": "#f5c76b",
            "headline": "Clear Legal Guidance When The Stakes Matter.",
            "subheadline": "A calm trust-first legal site for confidential enquiries, service clarity, consultation requests, and authority building.",
            "cta": "Request Consultation",
        }

    return {
        "brand": "Aurelise",
        "industry": "luxury skincare",
        "layout_blueprint": "beauty-editorial-commerce",
        "accent": "#f472b6",
        "headline": "Clinical Radiance, Reimagined As Luxury Ritual.",
        "subheadline": "A cinematic beauty ecommerce experience built around ingredient science, luxury ritual, proof, and premium launch conversion.",
        "cta": "Shop Launch Collection",
    }


def _common_css(accent: str):
    return f"""
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; background: #050713; }}
      .page {{ min-height: 100vh; color: white; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; overflow-x: hidden; }}
      .pill {{ display: inline-flex; padding: 10px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.08); color: {accent}; font-weight: 900; }}
      .btn {{ border: none; border-radius: 999px; padding: 17px 24px; font-weight: 950; background: white; color: #020617; cursor: pointer; }}
      .ghost {{ background: rgba(255,255,255,.08); color: white; border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(20px); }}
      .glass {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14); backdrop-filter: blur(24px); box-shadow: 0 30px 100px rgba(0,0,0,.28); }}
      @keyframes floaty {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-22px); }} }}
      @keyframes glow {{ 0%,100% {{ opacity: .55; transform: scale(1); }} 50% {{ opacity: .92; transform: scale(1.08); }} }}
      @keyframes slide {{ 0% {{ transform: translateX(-20px); opacity: .45; }} 50% {{ transform: translateX(20px); opacity: 1; }} 100% {{ transform: translateX(-20px); opacity: .45; }} }}
    """


def _beauty(strategy):
    a = strategy["accent"]
    return f"""
export default function GeneratedSite() {{
  return (
    <main className="page beauty">
      <aside className="sideRail"><span>{strategy["brand"]}</span><i>01 / Ritual</i><i>02 / Science</i><i>03 / Proof</i></aside>
      <section className="beautyHero">
        <div className="copy">
          <div className="pill">Beauty editorial commerce</div>
          <h1>{strategy["headline"]}</h1>
          <p>{strategy["subheadline"]}</p>
          <div className="actions"><button className="btn">{strategy["cta"]}</button><button className="btn ghost">Explore Science</button></div>
        </div>
        <div className="ritualScene">
          <div className="halo"></div><div className="serumBottle"><small>{strategy["brand"]}</small><strong>RADIANCE</strong></div>
          <div className="ingredient one">Peptide Complex</div><div className="ingredient two">Barrier Repair</div>
        </div>
      </section>
      <section className="editorialGrid">
        <div className="large glass"><span>Ingredient Science</span><h2>Clinical-grade formulation presented as an elevated daily ritual.</h2></div>
        <div className="tall glass"><h3>Before / After Proof</h3><p>Generated visual proof section for customer transformation storytelling.</p></div>
        <div className="wide glass"><h3>Launch Offer</h3><p>15% off first order, free express shipping, complimentary sample ritual over $150.</p></div>
      </section>
      <style>{{`
        {_common_css(a)}
        .beauty {{ background: radial-gradient(circle at 25% 10%, {a}55, transparent 34%), linear-gradient(135deg,#090712,#17101f,#040712); }}
        .sideRail {{ position: fixed; left: 0; top: 0; bottom: 0; width: 92px; border-right: 1px solid rgba(255,255,255,.12); display: flex; flex-direction: column; gap: 34px; align-items: center; padding: 28px 12px; writing-mode: vertical-rl; font-weight: 900; color: #fff9; }}
        .beautyHero {{ min-height: 100vh; padding: 90px 80px 70px 150px; display: grid; grid-template-columns: .9fr 1.1fr; gap: 60px; align-items: center; }}
        h1 {{ font-size: clamp(62px, 8vw, 118px); line-height: .86; letter-spacing: -.08em; margin: 24px 0; }}
        p {{ color: #dbe3f0; font-size: 22px; line-height: 1.65; max-width: 720px; }}
        .actions {{ display: flex; gap: 14px; margin-top: 32px; }}
        .ritualScene {{ position: relative; height: 720px; }}
        .halo {{ position: absolute; inset: 80px; border-radius: 999px; background: radial-gradient(circle, {a}88, transparent 58%); filter: blur(8px); animation: glow 6s infinite; }}
        .serumBottle {{ position: absolute; left: 38%; top: 18%; width: 310px; height: 520px; border-radius: 58px; display: grid; place-items: center; text-align: center; background: linear-gradient(145deg, rgba(255,255,255,.76), rgba(255,255,255,.1), {a}88); border: 1px solid rgba(255,255,255,.32); backdrop-filter: blur(30px); transform: rotateY(-18deg) rotateX(8deg); animation: floaty 6s infinite; }}
        .serumBottle small {{ letter-spacing: .28em; font-weight: 950; }}
        .serumBottle strong {{ display: block; font-size: 46px; margin-top: 14px; }}
        .ingredient {{ position: absolute; padding: 20px; border-radius: 28px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(22px); font-weight: 900; }}
        .ingredient.one {{ left: 0; top: 120px; }} .ingredient.two {{ right: 20px; bottom: 150px; }}
        .editorialGrid {{ padding: 40px 80px 120px 150px; display: grid; grid-template-columns: 1.1fr .9fr; gap: 22px; }}
        .editorialGrid > div {{ border-radius: 42px; padding: 40px; min-height: 260px; }}
        .large {{ min-height: 520px !important; }} .large h2 {{ font-size: 58px; line-height: .92; letter-spacing: -.06em; }}
        .wide {{ grid-column: span 2; }}
      `}}</style>
    </main>
  );
}}
"""


def _fitness(strategy):
    a = strategy["accent"]
    return f"""
export default function GeneratedSite() {{
  return (
    <main className="page fitness">
      <section className="scoreHero">
        <div className="metricWall">
          <div className="metric big">07<span>DAY TRIAL</span></div><div className="metric">1:1<span>GOAL MAP</span></div><div className="metric">24/7<span>BOOKINGS</span></div>
        </div>
        <div className="fitnessCopy">
          <div className="pill">Performance studio landing</div><h1>{strategy["headline"]}</h1><p>{strategy["subheadline"]}</p>
          <button className="btn">{strategy["cta"]}</button>
        </div>
      </section>
      <section className="programs">
        <div className="program glass"><h3>Strength Track</h3><p>Progressive training blocks.</p></div>
        <div className="program glass"><h3>Conditioning</h3><p>Kinetic class schedule module.</p></div>
        <div className="program glass"><h3>Recovery</h3><p>Premium retention and habit loop.</p></div>
      </section>
      <style>{{`
        {_common_css(a)}
        .fitness {{ background: radial-gradient(circle at 18% 22%, {a}55, transparent 28%), linear-gradient(135deg,#020617,#07111f,#111827); }}
        .scoreHero {{ min-height: 100vh; display: grid; grid-template-columns: .9fr 1.1fr; gap: 40px; padding: 80px; align-items: center; }}
        .metricWall {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; transform: rotate(-2deg); }}
        .metric {{ min-height: 220px; border-radius: 34px; display: flex; flex-direction: column; justify-content: center; padding: 30px; background: #071827; border: 1px solid {a}66; font-size: 56px; font-weight: 950; box-shadow: 0 30px 90px rgba(0,0,0,.36); animation: floaty 7s infinite; }}
        .metric.big {{ grid-column: span 2; min-height: 300px; font-size: 120px; color: {a}; }}
        .metric span {{ display: block; font-size: 16px; letter-spacing: .22em; color: #dbeafe; }}
        h1 {{ font-size: clamp(62px, 8vw, 112px); line-height: .86; letter-spacing: -.08em; }}
        p {{ color: #cbd5e1; font-size: 22px; line-height: 1.6; max-width: 700px; }}
        .programs {{ padding: 30px 80px 120px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }}
        .program {{ padding: 34px; border-radius: 34px; min-height: 280px; }}
      `}}</style>
    </main>
  );
}}
"""


def _property(strategy):
    a = strategy["accent"]
    return f"""
export default function GeneratedSite() {{
  return (
    <main className="page property">
      <section className="propertyHero">
        <div className="listingPanel"><span>Featured Waterfront Campaign</span><h1>{strategy["headline"]}</h1><p>{strategy["subheadline"]}</p><button className="btn">{strategy["cta"]}</button></div>
        <div className="gallery">
          <div className="photo main"></div><div className="photo side"></div><div className="valuation glass">Appraisal pathway ready</div>
        </div>
      </section>
      <section className="propertyProof">
        <div><strong>01</strong><h3>Prestige Story</h3></div><div><strong>02</strong><h3>Buyer Enquiry Flow</h3></div><div><strong>03</strong><h3>Suburb Authority</h3></div>
      </section>
      <style>{{`
        {_common_css(a)}
        .property {{ background: radial-gradient(circle at 80% 10%, {a}44, transparent 30%), linear-gradient(135deg,#0b0906,#1c160d,#111827); }}
        .propertyHero {{ min-height: 100vh; display: grid; grid-template-columns: .72fr 1.28fr; gap: 42px; padding: 90px; align-items: center; }}
        .listingPanel {{ border-left: 3px solid {a}; padding-left: 34px; }}
        h1 {{ font-size: clamp(56px, 7vw, 96px); line-height: .9; letter-spacing: -.07em; }}
        p {{ color: #e7dfd0; font-size: 21px; line-height: 1.65; }}
        .gallery {{ position: relative; height: 700px; }}
        .photo {{ position: absolute; border-radius: 42px; background: linear-gradient(135deg,#2a2418,#8c6b34,#0f172a); border: 1px solid rgba(255,255,255,.16); box-shadow: 0 40px 110px rgba(0,0,0,.42); }}
        .photo.main {{ inset: 20px 100px 120px 20px; }} .photo.side {{ right: 10px; bottom: 40px; width: 360px; height: 320px; animation: floaty 7s infinite; }}
        .valuation {{ position: absolute; right: 80px; top: 70px; padding: 24px; border-radius: 28px; font-weight: 900; }}
        .propertyProof {{ padding: 0 90px 120px; display: grid; grid-template-columns: repeat(3,1fr); gap: 18px; }}
        .propertyProof div {{ min-height: 230px; padding: 30px; border-radius: 32px; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14); }}
        .propertyProof strong {{ color: {a}; }}
      `}}</style>
    </main>
  );
}}
"""


def _saas(strategy):
    a = strategy["accent"]
    return f"""
export default function GeneratedSite() {{
  return (
    <main className="page saas">
      <section className="dashboardHero">
        <div><div className="pill">SaaS command centre</div><h1>{strategy["headline"]}</h1><p>{strategy["subheadline"]}</p><button className="btn">{strategy["cta"]}</button></div>
        <div className="dashboard glass">
          <div className="topbar"></div><div className="chart"></div><div className="modules"><i></i><i></i><i></i><i></i></div>
        </div>
      </section>
      <section className="orbitModules"><div>Automation</div><div>Analytics</div><div>Security</div><div>Workflow</div></section>
      <style>{{`
        {_common_css(a)}
        .saas {{ background: radial-gradient(circle at 15% 15%, {a}55, transparent 30%), linear-gradient(135deg,#050816,#111827,#1e1b4b); }}
        .dashboardHero {{ min-height: 100vh; display: grid; grid-template-columns: .9fr 1.1fr; gap: 50px; padding: 80px; align-items: center; }}
        h1 {{ font-size: clamp(60px, 8vw, 110px); line-height: .86; letter-spacing: -.08em; }}
        p {{ color: #dbe3f0; font-size: 22px; line-height: 1.6; }}
        .dashboard {{ height: 620px; border-radius: 38px; padding: 28px; display: grid; grid-template-rows: 60px 1fr 160px; gap: 20px; animation: floaty 7s infinite; }}
        .topbar,.chart,.modules i {{ border-radius: 22px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.14); }}
        .chart {{ background: radial-gradient(circle at 30% 30%, {a}66, transparent 40%), rgba(255,255,255,.08); }}
        .modules {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; }}
        .orbitModules {{ padding: 0 80px 120px; display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; }}
        .orbitModules div {{ padding: 30px; border-radius: 30px; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14); font-weight: 900; }}
      `}}</style>
    </main>
  );
}}
"""


def _legal(strategy):
    a = strategy["accent"]
    return f"""
export default function GeneratedSite() {{
  return (
    <main className="page legal">
      <section className="legalHero">
        <div className="trustMark">LEX</div>
        <div><div className="pill">Legal trust conversion</div><h1>{strategy["headline"]}</h1><p>{strategy["subheadline"]}</p><button className="btn">{strategy["cta"]}</button></div>
      </section>
      <section className="consultationFlow"><div>Confidential Enquiry</div><div>Case Assessment</div><div>Clear Next Step</div></section>
      <section className="legalProof glass"><h2>Built for authority, privacy, and calm decision-making.</h2><p>Service clarity, trust signals, and consultation conversion without aggressive sales styling.</p></section>
      <style>{{`
        {_common_css(a)}
        .legal {{ background: radial-gradient(circle at 75% 15%, {a}33, transparent 28%), linear-gradient(135deg,#080807,#17120a,#111827); }}
        .legalHero {{ min-height: 100vh; display: grid; grid-template-columns: .55fr 1fr; gap: 60px; padding: 90px; align-items: center; }}
        .trustMark {{ width: 360px; height: 520px; border-radius: 40px; display: grid; place-items: center; font-size: 96px; font-weight: 950; color: {a}; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.06); box-shadow: 0 40px 120px rgba(0,0,0,.36); }}
        h1 {{ font-size: clamp(58px, 7vw, 104px); line-height: .9; letter-spacing: -.07em; }}
        p {{ color: #e5e7eb; font-size: 22px; line-height: 1.65; }}
        .consultationFlow {{ padding: 0 90px 60px; display: grid; grid-template-columns: repeat(3,1fr); gap: 18px; }}
        .consultationFlow div {{ padding: 30px; border-radius: 28px; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14); font-weight: 900; }}
        .legalProof {{ margin: 0 90px 120px; border-radius: 40px; padding: 50px; }}
        .legalProof h2 {{ font-size: 54px; line-height: .95; letter-spacing: -.05em; }}
      `}}</style>
    </main>
  );
}}
"""


def generate_react_website_project(
    task,
    tenant_id="owner_admin",
    agent_id="website_landing_apps_agent",
    connected_integrations=None,
    owner_approved=False
):
    strategy = _pick_strategy(task)
    site_id = f"{strategy['brand'].lower()}-{uuid4().hex[:8]}"
    site_dir = GENERATED_ROOT / site_id
    site_dir.mkdir(parents=True, exist_ok=True)

    blueprint = strategy["layout_blueprint"]

    if blueprint == "performance-studio-landing":
        page = _fitness(strategy)
    elif blueprint == "luxury-property-showcase":
        page = _property(strategy)
    elif blueprint == "saas-command-centre":
        page = _saas(strategy)
    elif blueprint == "legal-trust-conversion":
        page = _legal(strategy)
    else:
        page = _beauty(strategy)

    (site_dir / "page.tsx").write_text(page, encoding="utf-8")

    metadata = {
        "success": True,
        "site_id": site_id,
        "preview_url": f"/generated-sites/{site_id}",
        "generated_files": [f"frontend/src/app/generated-sites/{site_id}/page.tsx"],
        "framework": "Next.js React",
        "status": "react_project_created",
        "publish_status": "not_published",
        "publish_blocker": "Publishing requires owner approval and deploy/CMS integration.",
        "brand": strategy["brand"],
        "industry": strategy["industry"],
        "layout_blueprint": blueprint,
        "visual_system": ["distinct_jsx_generator", blueprint, "glassmorphism", "motion", "premium_ui"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    (site_dir / "site.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata
'''

TARGET.write_text(code, encoding="utf-8")
print("DISTINCT_LAYOUT_ENGINE_REPLACED")
print("Backup:", BACKUP)