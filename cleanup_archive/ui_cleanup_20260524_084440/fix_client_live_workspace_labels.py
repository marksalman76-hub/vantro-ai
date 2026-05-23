from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FILE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"client_page_before_live_workspace_labels_{stamp}.tsx"
shutil.copy2(FILE, backup)

s = FILE.read_text(encoding="utf-8")

replacements = {
    "const creditsRemaining = 500;": "const creditsRemaining = account?.credits_remaining ?? 0;",
    'const accountPackage = account?.package_name || account?.package || "Premium workspace";': 'const accountPackage = account?.package_name || account?.package || "Active workspace";',
    "Premium Demo Ecommerce Store": "{account?.company_name || account?.contact_email || \"Client Workspace\"}",
    "Luxury skincare launch campaign": "Latest client deliverable",
    "Create premium ecommerce campaign assets for a luxury skincare product launch.": "Create premium ecommerce campaign assets for this business using the saved business profile, active agents, and selected execution requirements.",
    "Luxury skincare, supplements, fashion, pet products": "Describe your ecommerce niche, product category, and market position",
    "Luxury skincare": "Client ecommerce business",
    "Premium ecommerce buyers": "Target customers from the saved business profile",
    "Commercial-grade premium launch campaign": "Commercial-grade client-specific campaign",
}

for old, new in replacements.items():
    s = s.replace(old, new)

FILE.write_text(s, encoding="utf-8")

print("CLIENT_LIVE_WORKSPACE_LABELS_FIXED")
print(f"Backup: {backup}")