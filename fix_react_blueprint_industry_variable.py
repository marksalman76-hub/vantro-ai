from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "react_website_generation_runtime.py"

BACKUP = ROOT / "backups" / f"react_blueprint_industry_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "react_website_generation_runtime.py")

s = TARGET.read_text(encoding="utf-8")

s = s.replace(
'''    if "fitness" in lower:
        brand = "PeakForm"
        headline = "Train Smarter. Move Stronger. Stay Consistent."
        subheadline = "Premium boutique fitness experience built for high-performance members."
        accent = "#22d3ee"''',
'''    if "fitness" in lower:
        brand = "PeakForm"
        industry = "fitness"
        headline = "Train Smarter. Move Stronger. Stay Consistent."
        subheadline = "Premium boutique fitness experience built for high-performance members."
        accent = "#22d3ee"'''
)

s = s.replace(
'''    elif "real estate" in lower or "property" in lower:
        brand = "PrimeNest"
        headline = "Luxury Waterfront Campaigns Built To Dominate Attention."
        subheadline = "High-conversion property campaign architecture for premium listings."
        accent = "#f5c76b"''',
'''    elif "real estate" in lower or "property" in lower:
        brand = "PrimeNest"
        industry = "real estate"
        headline = "Luxury Waterfront Campaigns Built To Dominate Attention."
        subheadline = "High-conversion property campaign architecture for premium listings."
        accent = "#f5c76b"'''
)

s = s.replace(
'''    else:
        brand = "Aurelise"
        headline = "Clinical Radiance, Reimagined As Luxury Ritual."
        subheadline = "Premium skincare experience with motion-driven luxury conversion design."
        accent = "#f472b6"''',
'''    elif "saas" in lower or "software" in lower or "platform" in lower:
        brand = "Nexora"
        industry = "software"
        headline = "A Smarter Platform Experience Built For Scale."
        subheadline = "A premium SaaS command-centre landing page with dashboard-style proof, workflow clarity, and demo conversion."
        accent = "#a78bfa"

    elif "law" in lower or "legal" in lower:
        brand = "Lexora"
        industry = "legal services"
        headline = "Clear Legal Guidance When The Stakes Matter."
        subheadline = "A trust-first legal website experience designed for confidential enquiries, service clarity, and consultation conversion."
        accent = "#f5c76b"

    else:
        brand = "Aurelise"
        industry = "luxury skincare"
        headline = "Clinical Radiance, Reimagined As Luxury Ritual."
        subheadline = "Premium skincare experience with motion-driven luxury conversion design."
        accent = "#f472b6"'''
)

s = s.replace(
'''        "brand": strategy["brand"],
        "industry": strategy["industry"],''',
'''        "brand": brand,
        "industry": industry,'''
)

TARGET.write_text(s, encoding="utf-8")

print("REACT_BLUEPRINT_INDUSTRY_VARIABLE_FIXED")
print("Backup:", BACKUP)