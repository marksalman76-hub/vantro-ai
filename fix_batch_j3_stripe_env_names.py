from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

file = ROOT / "backend" / "app" / "core" / "stripe_checkout_runtime.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"stripe_checkout_runtime_before_batch_j3_{timestamp}.py"
shutil.copy2(file, backup)

text = file.read_text(encoding="utf-8")

text = text.replace('"STRIPE_PRICE_STARTER_MONTHLY"', '"STRIPE_PRICE_STARTER"')
text = text.replace('"STRIPE_PRICE_GROWTH_MONTHLY"', '"STRIPE_PRICE_GROWTH"')
text = text.replace('"STRIPE_PRICE_PRO_MONTHLY"', '"STRIPE_PRICE_BUSINESS"')
text = text.replace('{"business", "business", "full", "full_access"}', '{"business", "full", "full_access"}')

file.write_text(text, encoding="utf-8")

print("BATCH_J3_STRIPE_ENV_NAMES_FIXED")
print(f"Backup: {backup}")