from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_remove_audio_icon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Remove audio toggle/button blocks.
s = re.sub(r'\s*<button[^>]*audio[^>]*>.*?</button>', '', s, flags=re.DOTALL | re.IGNORECASE)
s = re.sub(r'\s*<button[^>]*Audio[^>]*>.*?</button>', '', s, flags=re.DOTALL)
s = re.sub(r'\s*<button[^>]*sound[^>]*>.*?</button>', '', s, flags=re.DOTALL | re.IGNORECASE)

# Remove common icon-only audio control class blocks.
s = re.sub(r'\s*<div[^>]*className="[^"]*(audio|sound)[^"]*"[^>]*>.*?</div>', '', s, flags=re.DOTALL | re.IGNORECASE)

# Remove unused audio imports if present.
s = re.sub(r',\s*Volume2', '', s)
s = re.sub(r',\s*VolumeX', '', s)
s = re.sub(r'Volume2,\s*', '', s)
s = re.sub(r'VolumeX,\s*', '', s)

PAGE.write_text(s, encoding="utf-8")

print("AUDIO_ICON_REMOVED_FROM_LANDING")
print(f"Backup: {backup}")