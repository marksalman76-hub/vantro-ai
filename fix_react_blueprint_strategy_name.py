from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "react_website_generation_runtime.py"
BACKUP = ROOT / "backups" / f"react_blueprint_strategy_name_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "react_website_generation_runtime.py")

s = TARGET.read_text(encoding="utf-8")

s = s.replace('strategy.get("layout_blueprint", "beauty-editorial-commerce")', 'layout_blueprint')

if "layout_blueprint =" not in s:
    marker = '    site_id = f"{brand.lower()}-{uuid4().hex[:8]}"'
    s = s.replace(
        marker,
        '''    if industry == "fitness":
        layout_blueprint = "performance-studio-landing"
    elif industry == "real estate":
        layout_blueprint = "luxury-property-showcase"
    elif industry == "software":
        layout_blueprint = "saas-command-centre"
    elif industry == "legal services":
        layout_blueprint = "legal-trust-conversion"
    else:
        layout_blueprint = "beauty-editorial-commerce"

''' + marker
    )

TARGET.write_text(s, encoding="utf-8")

print("REACT_BLUEPRINT_STRATEGY_NAME_FIXED")
print("Backup:", BACKUP)