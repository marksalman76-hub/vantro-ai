from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_remove_pd_alerts_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

text = text.replace('alert("Settings panel selected.");', "")
text = text.replace('alert("Profile panel selected.");', "")
text = text.replace('alert("Password reset selected.");', "")
text = text.replace('alert("2FA selected.");', "")

PAGE.write_text(text, encoding="utf-8")

print("PD_MENU_ALERTS_REMOVED")
print(f"Backup: {backup}")