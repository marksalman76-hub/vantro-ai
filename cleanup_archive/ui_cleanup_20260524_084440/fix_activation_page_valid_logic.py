from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "activate" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")

backup = BACKUP_DIR / f"activate_page_before_valid_logic_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old = """  const isValid =
    invite &&
    invite.success === true &&
    invite.expired === false &&
    invite.used === false;
"""

new = """  const isValid =
    invite &&
    invite.success === true &&
    (
      invite.valid === true ||
      (invite.expired === false && invite.used === false)
    );
"""

if old not in text:
    raise SystemExit("ACTIVATION_VALID_LOGIC_TARGET_NOT_FOUND")

PAGE.write_text(text.replace(old, new), encoding="utf-8")

print("ACTIVATION_PAGE_VALID_LOGIC_FIXED")
print(f"Backup: {backup}")