from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "react_website_generation_runtime.py"
BACKUP = ROOT / "backups" / f"react_layout_blueprints_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "react_website_generation_runtime.py")

s = TARGET.read_text(encoding="utf-8")

s = s.replace(
'''            "visual": "PERFORMANCE",
            "accent": "cyan",''',
'''            "visual": "PERFORMANCE",
            "accent": "cyan",
            "layout_blueprint": "performance-studio-landing",'''
)

s = s.replace(
'''            "visual": "WATERFRONT",
            "accent": "gold",''',
'''            "visual": "WATERFRONT",
            "accent": "gold",
            "layout_blueprint": "luxury-property-showcase",'''
)

s = s.replace(
'''            "visual": "PLATFORM",
            "accent": "violet",''',
'''            "visual": "PLATFORM",
            "accent": "violet",
            "layout_blueprint": "saas-command-centre",'''
)

s = s.replace(
'''        "brand": "Aurelise",
        "industry": "luxury skincare",''',
'''        "brand": "Aurelise",
        "industry": "luxury skincare",
        "layout_blueprint": "beauty-editorial-commerce",'''
)

# Add legal blueprint branch before default skincare return
s = s.replace(
'''    return {
        "brand": "Aurelise",''',
'''    if "law" in lower or "legal" in lower:
        return {
            "brand": "Lexora",
            "industry": "legal services",
            "layout_blueprint": "legal-trust-conversion",
            "headline": "Clear Legal Guidance When The Stakes Matter.",
            "subheadline": "A trust-first legal website experience designed for confidential enquiries, service clarity, and consultation conversion.",
            "cta": "Request a Consultation",
            "secondary": "View Services",
            "visual": "TRUST",
            "accent": "gold",
            "sections": ["Confidential enquiry", "Practice areas", "Trust proof", "Consultation pathway"],
            "offer": "Consultation-ready legal page with service breakdown, trust signals, and enquiry flow.",
        }

    return {
        "brand": "Aurelise",'''
)

# Add blueprint to metadata
s = s.replace(
'''        "industry": strategy["industry"],
        "status": "react_project_created",''',
'''        "industry": strategy["industry"],
        "layout_blueprint": strategy.get("layout_blueprint", "beauty-editorial-commerce"),
        "status": "react_project_created",'''
)

# Add visual system proof
s = s.replace(
'''        "visual_system": [
            "glassmorphism",
            "3d_motion",
            "animated_layout",
            "premium_ui"
        ],''',
'''        "visual_system": [
            "glassmorphism",
            "3d_motion",
            "animated_layout",
            "premium_ui",
            strategy.get("layout_blueprint", "beauty-editorial-commerce")
        ],'''
)

TARGET.write_text(s, encoding="utf-8")
print("REACT_WEBSITE_LAYOUT_BLUEPRINTS_ADDED")
print("Blueprints added:")
print("- beauty-editorial-commerce")
print("- performance-studio-landing")
print("- luxury-property-showcase")
print("- saas-command-centre")
print("- legal-trust-conversion")
print("Backup:", BACKUP)