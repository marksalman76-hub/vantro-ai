from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "activate" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")

backup = BACKUP_DIR / f"activate_page_before_force_valid_flag_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

start = text.find("  const isValid =")
end = text.find("\n\n  return (", start)

if start == -1 or end == -1:
    raise SystemExit("ACTIVATION_IS_VALID_BLOCK_NOT_FOUND")

replacement = """  const isValid = Boolean(invite?.success === true && invite?.valid === true);"""

PAGE.write_text(text[:start] + replacement + text[end:], encoding="utf-8")

print("ACTIVATION_PAGE_FORCED_VALID_FLAG")
print(f"Backup: {backup}")