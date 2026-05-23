from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_initials_business_profile_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

old = '''  const clientDisplayName =
    accountAny?.company_name ||
    accountAny?.business_name ||
    accountAny?.client_name ||
    accountAny?.contact_name ||
    accountAny?.full_name ||
    accountAny?.email ||
    "Client";'''

new = '''  const businessProfileAny = businessProfile as any;
  const clientDisplayName =
    businessProfileAny?.business_name ||
    businessProfileAny?.company_name ||
    businessProfileAny?.brand_name ||
    businessProfileAny?.business_niche ||
    accountAny?.company_name ||
    accountAny?.business_name ||
    accountAny?.client_name ||
    accountAny?.contact_name ||
    accountAny?.full_name ||
    accountAny?.email ||
    "Client";'''

if old not in text:
    raise RuntimeError("Current clientDisplayName block not found. No changes written.")

text = text.replace(old, new, 1)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_INITIALS_BUSINESS_PROFILE_FIXED")
print(f"Backup: {backup}")