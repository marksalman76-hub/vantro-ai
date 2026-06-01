from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "custom_website_generation_runtime.py"
BACKUP = ROOT / "backups" / f"custom_website_visual_capabilities_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "custom_website_generation_runtime.py")

s = TARGET.read_text(encoding="utf-8")

insert = r'''
def _visual_capabilities(task: str) -> Dict[str, Any]:
    lower = task.lower()
    requested = {
        "glassmorphism": any(x in lower for x in ["glass", "glassmorphism", "frosted"]),
        "three_d": any(x in lower for x in ["3d", "three dimensional", "depth", "orb", "floating"]),
        "animations": any(x in lower for x in ["animation", "animated", "motion", "interactive", "scroll effect"]),
        "dark_mode": any(x in lower for x in ["dark", "black", "neon"]),
        "luxury": any(x in lower for x in ["luxury", "premium", "high-end", "exclusive"]),
    }

    if requested["luxury"] and not any([requested["glassmorphism"], requested["three_d"], requested["animations"]]):
        requested["glassmorphism"] = True
        requested["three_d"] = True
        requested["animations"] = True

    return {
        "requested_capabilities": requested,
        "enabled_effects": [
            name for name, enabled in requested.items() if enabled
        ],
        "rendering_mode": "premium_interactive_static_export",
    }
'''

if "def _visual_capabilities" not in s:
    s = s.replace("def generate_custom_website_project(", insert + "\ndef generate_custom_website_project(")

s = s.replace(
'''    strategy = _site_strategy(task)
    brand = _brand(task)''',
'''    strategy = _site_strategy(task)
    visual_capabilities = _visual_capabilities(task)
    brand = _brand(task)'''
)

s = s.replace(
'''      background:
        radial-gradient(circle at 10% 12%,rgba(232,121,185,.32),transparent 34%),
        radial-gradient(circle at 88% 2%,rgba(217,154,43,.28),transparent 32%),
        linear-gradient(135deg,#fff,var(--cream) 48%,#fff1f7);''',
'''      background:
        radial-gradient(circle at 10% 12%,rgba(232,121,185,.32),transparent 34%),
        radial-gradient(circle at 88% 2%,rgba(217,154,43,.28),transparent 32%),
        radial-gradient(circle at 50% 80%,rgba(125,92,255,.16),transparent 35%),
        linear-gradient(135deg,#fff,var(--cream) 48%,#fff1f7);'''
)

s = s.replace(
'''    .visual {
      min-height:620px; border-radius:48px; position:relative; overflow:hidden;
      background:
        radial-gradient(circle at 30% 18%,#fff 0,#fff3c4 21%,#f7a8cf 56%,#190d22 100%);
      box-shadow:0 46px 120px rgba(54,14,41,.28);
      transform:rotate(1.2deg);
    }''',
'''    .visual {
      min-height:620px; border-radius:48px; position:relative; overflow:hidden;
      background:
        radial-gradient(circle at 30% 18%,#fff 0,#fff3c4 21%,#f7a8cf 56%,#190d22 100%);
      box-shadow:0 46px 120px rgba(54,14,41,.28);
      transform:rotate(1.2deg);
      perspective:1100px;
      isolation:isolate;
    }
    .visual::before,
    .visual::after {
      content:"";
      position:absolute;
      width:220px;
      height:220px;
      border-radius:999px;
      background:linear-gradient(135deg,rgba(255,255,255,.72),rgba(255,255,255,.12));
      filter:blur(.2px);
      border:1px solid rgba(255,255,255,.42);
      animation:floatOrb 7s ease-in-out infinite;
      z-index:0;
    }
    .visual::before { left:34px; top:44px; }
    .visual::after { right:-42px; bottom:80px; animation-delay:1.2s; }'''
)

s = s.replace(
'''      background:linear-gradient(145deg,rgba(255,255,255,.82),rgba(255,255,255,.22) 48%,rgba(91,23,62,.9));''',
'''      background:linear-gradient(145deg,rgba(255,255,255,.82),rgba(255,255,255,.22) 48%,rgba(91,23,62,.9));
      backdrop-filter:blur(22px);'''
)

s = s.replace(
'''      display:grid; place-items:center; text-align:center; color:white; padding:28px;
    }''',
'''      display:grid; place-items:center; text-align:center; color:white; padding:28px;
      transform:rotateY(-10deg) rotateX(6deg);
      animation:productFloat 5.5s ease-in-out infinite;
      z-index:2;
    }'''
)

s = s.replace(
'''    .float-card {
      position:absolute; background:rgba(255,255,255,.74); border:1px solid rgba(255,255,255,.55);
      box-shadow:0 18px 60px rgba(15,23,42,.16); backdrop-filter:blur(18px);
      border-radius:24px; padding:18px; max-width:230px;
    }''',
'''    .float-card {
      position:absolute; background:rgba(255,255,255,.58); border:1px solid rgba(255,255,255,.62);
      box-shadow:0 18px 60px rgba(15,23,42,.16); backdrop-filter:blur(22px);
      border-radius:24px; padding:18px; max-width:230px;
      animation:glassFloat 6s ease-in-out infinite;
      z-index:4;
    }'''
)

s = s.replace(
'''    footer { text-align:center; padding:60px 24px 90px; color:#667085; }''',
'''    footer { text-align:center; padding:60px 24px 90px; color:#667085; }
    @keyframes productFloat {
      0%,100% { transform:rotateY(-10deg) rotateX(6deg) translateY(0); }
      50% { transform:rotateY(-4deg) rotateX(9deg) translateY(-18px); }
    }
    @keyframes glassFloat {
      0%,100% { transform:translateY(0) scale(1); }
      50% { transform:translateY(-14px) scale(1.02); }
    }
    @keyframes floatOrb {
      0%,100% { transform:translate3d(0,0,0) scale(1); opacity:.68; }
      50% { transform:translate3d(18px,-22px,0) scale(1.08); opacity:.92; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation:none !important; scroll-behavior:auto !important; }
    }'''
)

s = s.replace(
'''        "design_system": {
            "style": "premium ecommerce editorial",
            "layout": "responsive long-form landing page",
            "sections": ["sticky nav", "hero", "benefits", "product/service architecture", "offer", "proof", "faq", "sticky cta"],
            "quality_level": "premium_generated_draft",
        },''',
'''        "design_system": {
            "style": "premium ecommerce editorial",
            "layout": "responsive long-form landing page",
            "sections": ["sticky nav", "hero", "animated 3D/glass visual", "benefits", "product/service architecture", "offer", "proof", "faq", "sticky cta"],
            "quality_level": "premium_generated_draft",
            "visual_capabilities": visual_capabilities,
        },'''
)

TARGET.write_text(s, encoding="utf-8")

print("CUSTOM_WEBSITE_VISUAL_CAPABILITIES_UPGRADED")
print("Backup:", BACKUP)
print("Updated:", TARGET)