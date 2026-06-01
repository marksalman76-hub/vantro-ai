from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "react_website_generation_runtime.py"
BACKUP = ROOT / "backups" / f"distinct_react_blueprint_generators_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "react_website_generation_runtime.py")

s = TARGET.read_text(encoding="utf-8")

insert = r'''
def _blueprint_personality(layout_blueprint: str, accent: str) -> dict:
    if layout_blueprint == "performance-studio-landing":
        return {
            "theme": "performance_dark",
            "hero_shape": "split-performance-scoreboard",
            "visual_label": "TRAINING SYSTEM",
            "section_label": "Training Blocks",
            "tone": "energetic",
            "background": f"radial-gradient(circle at 20% 20%, {accent}66, transparent 28%), linear-gradient(135deg,#020617,#07111f,#111827)",
        }

    if layout_blueprint == "luxury-property-showcase":
        return {
            "theme": "property_editorial",
            "hero_shape": "wide-property-showcase",
            "visual_label": "WATERFRONT",
            "section_label": "Property Campaign",
            "tone": "prestige",
            "background": f"radial-gradient(circle at 80% 10%, {accent}55, transparent 30%), linear-gradient(135deg,#0b0906,#1c160d,#111827)",
        }

    if layout_blueprint == "saas-command-centre":
        return {
            "theme": "dashboard_command",
            "hero_shape": "product-dashboard-orbit",
            "visual_label": "COMMAND OS",
            "section_label": "Platform Modules",
            "tone": "technical",
            "background": f"radial-gradient(circle at 15% 15%, {accent}66, transparent 30%), linear-gradient(135deg,#050816,#111827,#1e1b4b)",
        }

    if layout_blueprint == "legal-trust-conversion":
        return {
            "theme": "legal_trust",
            "hero_shape": "trust-led-consultation",
            "visual_label": "TRUST",
            "section_label": "Client Confidence",
            "tone": "calm",
            "background": f"radial-gradient(circle at 75% 15%, {accent}44, transparent 28%), linear-gradient(135deg,#080807,#17120a,#111827)",
        }

    return {
        "theme": "beauty_editorial",
        "hero_shape": "cinematic-product-ritual",
        "visual_label": "RADIANCE",
        "section_label": "Luxury Ritual",
        "tone": "luxury",
        "background": f"radial-gradient(circle at 20% 10%, {accent}66, transparent 35%), linear-gradient(135deg,#070b17,#111827,#1e0f2f)",
    }
'''

if "def _blueprint_personality" not in s:
    s = s.replace("def generate_react_website_project(", insert + "\ndef generate_react_website_project(")

s = s.replace(
'''    site_id = f"{brand.lower()}-{uuid4().hex[:8]}"''',
'''    blueprint = _blueprint_personality(layout_blueprint, accent)
    site_id = f"{brand.lower()}-{uuid4().hex[:8]}"'''
)

s = s.replace(
'''            Premium AI-generated React website''',
'''            {blueprint["section_label"]} · {blueprint["theme"]}'''
)

s = s.replace(
'''              <strong>PREMIUM</strong>''',
'''              <strong>{blueprint["visual_label"]}</strong>'''
)

s = s.replace(
'''          <h3>3D Motion</h3>
          <p>Animated premium visual architecture.</p>''',
'''          <h3>{blueprint["section_label"]}</h3>
          <p>Blueprint-specific generated structure, not a shared template shell.</p>'''
)

s = s.replace(
'''            linear-gradient(135deg,#070b17,#111827,#1e0f2f);''',
'''            {blueprint["background"]};'''
)

s = s.replace(
'''        "visual_system": [
            "glassmorphism",
            "3d_motion",
            "animated_layout",
            "premium_ui",
            layout_blueprint
        ],''',
'''        "visual_system": [
            "glassmorphism",
            "3d_motion",
            "animated_layout",
            "premium_ui",
            layout_blueprint,
            blueprint["theme"],
            blueprint["hero_shape"],
            blueprint["tone"]
        ],'''
)

s = s.replace(
'''        "created_at": datetime.now(timezone.utc).isoformat()''',
'''        "layout_blueprint": layout_blueprint,
        "blueprint_theme": blueprint["theme"],
        "hero_shape": blueprint["hero_shape"],
        "created_at": datetime.now(timezone.utc).isoformat()'''
)

TARGET.write_text(s, encoding="utf-8")
print("DISTINCT_REACT_BLUEPRINT_GENERATORS_INSTALLED")
print("Backup:", BACKUP)