from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_pd_remaining_identity_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

text = text.replace(
'''              >
                PD
              </summary>''',
'''              >
                {clientInitials}
              </summary>''',
1
)

text = text.replace(
'''<div style={{ fontWeight: 800, color: "var(--color-dark)" }}>{clientInitials}</div>''',
'''<div style={{ fontWeight: 800, color: "var(--color-dark)" }}>{clientDisplayName}</div>''',
1
)

PAGE.write_text(text, encoding="utf-8")

print("PD_REMAINING_IDENTITY_FIXED")
print(f"Backup: {backup}")