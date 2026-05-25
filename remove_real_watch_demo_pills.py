from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_remove_real_watch_demo_pills_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

lines = PAGE.read_text(encoding="utf-8").splitlines()

remove_keywords = [
    "Watch 90s demo",
]

new_lines = []
for line in lines:
    stripped = line.strip()
    if any(keyword in stripped for keyword in remove_keywords):
        continue
    # Remove standalone Demo pill line, but keep nav/mobile/CTA demo links.
    if stripped == "Demo" or stripped == "{/* Demo prompt box */}":
        continue
    new_lines.append(line)

PAGE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

print("REAL_WATCH_DEMO_PILLS_REMOVED")
print(f"Backup: {backup}")