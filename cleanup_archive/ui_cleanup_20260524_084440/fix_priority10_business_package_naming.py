from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

FILES = [
    ROOT / "backend" / "app" / "core" / "marketplace_entitlement_runtime.py",
    ROOT / "backend" / "app" / "core" / "marketplace_commercial_bridge.py",
    ROOT / "backend" / "app" / "core" / "billing_automation_runtime.py",
    ROOT / "backend" / "app" / "core" / "stripe_production_hardening_runtime.py",
    ROOT / "backend" / "app" / "core" / "live_stripe_bridge_runtime.py",
    ROOT / "test_priority10_production_env_completion.py",
    ROOT / "test_priority10_billing_automation_runtime.py",
    ROOT / "test_priority10_stripe_production_hardening.py",
    ROOT / "test_priority10_live_stripe_bridge.py",
    ROOT / "test_priority9_commercial_marketplace_bridge.py",
]

for path in FILES:
    if not path.exists():
        print(f"SKIP missing: {path}")
        continue

    backup = BACKUP_DIR / f"{path.name}_before_business_package_rename_{timestamp}"
    backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    text = path.read_text(encoding="utf-8")

    replacements = {
        "professional": "business",
        "Professional": "Business",
        "PROFESSIONAL": "BUSINESS",
        "STRIPE_PRICE_PROFESSIONAL_MONTHLY": "STRIPE_PRICE_BUSINESS_MONTHLY",
        "Business automation package": "Business automation package",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    path.write_text(text, encoding="utf-8")

print("PRIORITY10_BUSINESS_PACKAGE_NAMING_FIXED")
print("Renamed professional package references to business")
print("Enterprise remains contact-us / owner-review only")