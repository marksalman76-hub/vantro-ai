
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4
import html
import json
import re

ROOT = Path(__file__).resolve().parents[3]
PUBLIC_GENERATED = ROOT / "frontend" / "public" / "generated-sites"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return cleaned[:48] or "generated-site"


def _brand(task: str) -> str:
    lower = task.lower()
    if "skincare" in lower:
        return "Luxe Radiance"
    if "fitness" in lower:
        return "PeakForm"
    if "real estate" in lower:
        return "PrimeNest"
    if "restaurant" in lower or "cafe" in lower:
        return "Maison Table"
    return "Premium Brand"


def generate_custom_website_project(
    *,
    task: str,
    tenant_id: str = "owner_admin",
    agent_id: str = "website_landing_apps_agent",
    connected_integrations: list[str] | None = None,
    owner_approved: bool = False,
) -> Dict[str, Any]:
    connected_integrations = connected_integrations or []
    brand = _brand(task)
    site_id = f"{_slug(brand)}-{uuid4().hex[:8]}"
    site_dir = PUBLIC_GENERATED / site_id
    site_dir.mkdir(parents=True, exist_ok=True)

    headline = "Luxury Skincare, Crafted for Timeless Radiance"
    subheadline = "A custom premium landing page built for Australian women aged 30–50 seeking glow, hydration, and an elevated skincare ritual."

    html_doc = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>__TITLE__</title>
  <meta name="description" content="__DESCRIPTION__" />
  <style>
    :root { --ink:#101827; --muted:#556070; --cream:#fff7ed; --panel:rgba(255,255,255,.84); }
    * { box-sizing:border-box; }
    body {
      margin:0;
      font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      color:var(--ink);
      background:radial-gradient(circle at 18% 12%,rgba(249,168,212,.42),transparent 34%),
                 radial-gradient(circle at 80% 6%,rgba(245,158,11,.28),transparent 32%),
                 linear-gradient(135deg,#fff,var(--cream));
    }
    .shell { max-width:1180px; margin:0 auto; padding:72px 24px; }
    .pill { display:inline-flex; padding:9px 14px; border-radius:999px; background:rgba(16,24,39,.08); font-weight:900; color:#7c2d12; }
    .hero { display:grid; grid-template-columns:1.08fr .92fr; gap:36px; align-items:center; }
    h1 { font-size:clamp(46px,7vw,84px); line-height:.95; letter-spacing:-.065em; margin:24px 0 20px; }
    .lead { font-size:22px; line-height:1.55; color:var(--muted); max-width:720px; }
    .cta-row { display:flex; gap:14px; flex-wrap:wrap; margin-top:32px; }
    .btn { text-decoration:none; border-radius:999px; padding:17px 24px; font-weight:950; }
    .btn-primary { background:var(--ink); color:white; }
    .btn-secondary { color:var(--ink); border:1px solid rgba(16,24,39,.18); }
    .visual {
      min-height:520px; border-radius:42px; position:relative; overflow:hidden;
      background:radial-gradient(circle at 28% 20%,#fff 0,#fde68a 22%,#f9a8d4 58%,#111827 100%);
      box-shadow:0 36px 100px rgba(16,24,39,.25);
    }
    .visual-card { position:absolute; inset:32px; border:1px solid rgba(255,255,255,.64); border-radius:34px; display:grid; place-items:center; text-align:center; color:white; padding:32px; }
    .brand-mark { font-size:22px; font-weight:950; text-transform:uppercase; letter-spacing:.16em; }
    .product-name { font-size:58px; font-weight:950; margin-top:20px; }
    .grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-top:46px; }
    .card { background:var(--panel); border:1px solid rgba(16,24,39,.08); border-radius:28px; padding:24px; box-shadow:0 18px 50px rgba(16,24,39,.08); }
    .dark { background:var(--ink); color:white; border-radius:38px; padding:44px; margin-top:54px; display:grid; grid-template-columns:1fr 1fr; gap:30px; }
    .dark p { color:#d1d5db; }
    .proof-item { padding:13px 0; border-bottom:1px solid rgba(255,255,255,.12); font-weight:800; }
    .faq { max-width:880px; margin:54px auto 0; }
    .faq h2,.dark h2 { font-size:44px; letter-spacing:-.04em; margin-top:0; }
    .faq-item { background:var(--panel); border:1px solid rgba(16,24,39,.08); border-radius:24px; padding:24px; margin-top:14px; }
    footer { text-align:center; padding:46px 24px 70px; color:var(--muted); }
    @media (max-width:900px) { .hero,.dark { grid-template-columns:1fr; } .grid { grid-template-columns:1fr 1fr; } .visual { min-height:420px; } }
    @media (max-width:560px) { .grid { grid-template-columns:1fr; } .shell { padding:42px 18px; } }
  </style>
</head>
<body>
  <main class="shell">
    <div class="hero">
      <section>
        <span class="pill">Custom Generated Landing Page · Draft Preview</span>
        <h1>__HEADLINE__</h1>
        <p class="lead">__SUBHEADLINE__</p>
        <div class="cta-row">
          <a class="btn btn-primary" href="#offer">Shop the Collection</a>
          <a class="btn btn-secondary" href="#faq">View Details</a>
        </div>
      </section>
      <section class="visual">
        <div class="visual-card">
          <div>
            <div class="brand-mark">__BRAND__</div>
            <div class="product-name">Radiance Ritual</div>
          </div>
        </div>
      </section>
    </div>

    <section class="grid">
      <div class="card"><h3>Deep Hydration</h3><p>Positioned around visible glow, elevated care, and daily ritual value.</p></div>
      <div class="card"><h3>Premium Trust</h3><p>Credibility blocks for ingredients, quality, and social proof.</p></div>
      <div class="card"><h3>Conversion Ready</h3><p>Hero, offer, FAQ, and CTA hierarchy designed for ecommerce conversion.</p></div>
      <div class="card"><h3>CMS Ready</h3><p>Generated as a draft preview with publish blocked until owner approval.</p></div>
    </section>

    <section id="offer" class="dark">
      <div>
        <h2>Launch Offer</h2>
        <p>15% off first purchase, complimentary luxury sample kit over $150, and free express shipping across Australia.</p>
      </div>
      <div>
        <h3>Trust & Proof Blocks</h3>
        <div class="proof-item">✓ Premium ingredient positioning</div>
        <div class="proof-item">✓ Visible-results messaging framework</div>
        <div class="proof-item">✓ Testimonial and credibility placeholders</div>
      </div>
    </section>

    <section id="faq" class="faq">
      <h2>Frequently Asked Questions</h2>
      <div class="faq-item"><strong>Who is this for?</strong><p>Women aged 30–50 looking for a premium skincare ritual focused on hydration, glow, and confidence.</p></div>
      <div class="faq-item"><strong>Is this page live?</strong><p>No. This is a generated draft preview. Publishing requires owner approval and a connected CMS/store integration.</p></div>
      <div class="faq-item"><strong>What was created?</strong><p>A custom landing page draft with visual layout, sections, SEO metadata, CTA structure, and previewable page files.</p></div>
    </section>
  </main>
  <footer>Generated by Website / Landing Page / Apps Agent · Draft ID __SITE_ID__</footer>
</body>
</html>"""

    html_doc = (
        html_doc
        .replace("__TITLE__", html.escape(headline))
        .replace("__DESCRIPTION__", html.escape(subheadline))
        .replace("__HEADLINE__", html.escape(headline))
        .replace("__SUBHEADLINE__", html.escape(subheadline))
        .replace("__BRAND__", html.escape(brand))
        .replace("__SITE_ID__", html.escape(site_id))
    )

    (site_dir / "index.html").write_text(html_doc, encoding="utf-8")

    metadata = {
        "site_id": site_id,
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "brand": brand,
        "task": task,
        "status": "draft_created",
        "preview_url": f"/generated-sites/{site_id}/index.html",
        "generated_files": [f"frontend/public/generated-sites/{site_id}/index.html"],
        "publish_status": "not_published",
        "publish_blocker": "Publishing requires owner approval and a live CMS/deploy integration.",
        "created_at": _now(),
    }

    (site_dir / "site.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return {
        "success": True,
        **metadata,
    }
