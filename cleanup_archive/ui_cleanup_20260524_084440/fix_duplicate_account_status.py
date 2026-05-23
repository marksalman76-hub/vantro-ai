from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_duplicate_account_status_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    '  const accountStatus = account?.package_status || account?.status || "active";\n',
    ''
)

PAGE.write_text(text, encoding="utf-8")

print("DUPLICATE_ACCOUNT_STATUS_FIXED")
print(f"Backup: {backup}")