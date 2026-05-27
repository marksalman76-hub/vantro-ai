from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

TARGET_FILES = [
    ROOT / "install_batch_i_production_launch_pack.py",
    ROOT / "PRODUCTION_ENVIRONMENT_TEMPLATE_DO_NOT_COMMIT_SECRETS.env",
]

REPLACEMENTS = [
    ("STRIPE_PRICE_ENTERPRISE", "STRIPE_PRICE_BUSINESS"),
    ("enterprise", "business"),
    ("Enterprise", "Business"),
]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

updated = []

for file in TARGET_FILES:
    if not file.exists():
        continue

    backup = BACKUPS / f"{file.stem}_before_batch_j_{timestamp}{file.suffix}"
    shutil.copy2(file, backup)

    text = file.read_text(encoding="utf-8", errors="ignore")

    original = text

    for old, new in REPLACEMENTS:
        text = text.replace(old, new)

    if file.name.endswith(".env"):
        if "STRIPE_PRICE_BUSINESS=" not in text:
            text += "\nSTRIPE_PRICE_BUSINESS=\n"

    if text != original:
        file.write_text(text, encoding="utf-8")
        updated.append(str(file.relative_to(ROOT)))

print("BATCH_J_STRIPE_STANDARDISATION_COMPLETE")
print("UPDATED_FILES")
for item in updated:
    print(item)