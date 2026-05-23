from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

file = ROOT / "backend" / "app" / "core" / "stripe_checkout_runtime.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"stripe_checkout_runtime_before_batch_j2_{timestamp}.py"
shutil.copy2(file, backup)

text = file.read_text(encoding="utf-8")

text = text.replace(
    '    if value in {"enterprise", "full", "full_access"}:\n        return "enterprise"',
    '    if value in {"business", "enterprise", "full", "full_access"}:\n        return "business"',
)

text = text.replace(
    '"enterprise"',
    '"business"',
)

text = text.replace(
    "'enterprise'",
    "'business'",
)

file.write_text(text, encoding="utf-8")

print("BATCH_J2_ACTIVE_STRIPE_RUNTIME_BUSINESS_PACKAGE_FIXED")
print(f"Backup: {backup}")