from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FILE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"client_page_before_account_type_credits_{stamp}.tsx"
shutil.copy2(FILE, backup)

s = FILE.read_text(encoding="utf-8")

old = '''  paid_agents?: string[];
};'''

new = '''  paid_agents?: string[];
  credits_remaining?: number;
  credits_monthly?: number;
  credits_used?: number;
};'''

if old not in s:
    raise SystemExit("ACCOUNT_TYPE_TARGET_NOT_FOUND")

s = s.replace(old, new, 1)

FILE.write_text(s, encoding="utf-8")

print("CLIENT_ACCOUNT_TYPE_CREDITS_FIXED")
print(f"Backup: {backup}")