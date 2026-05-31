from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_save_profile_badge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

old = '''setBusinessProfileSaved(Boolean(cleanedProfile.business_name));'''
new = '''setBusinessProfileSaved(true);'''

count = s.count(old)
if count == 0:
    raise SystemExit("FAILED: saved badge marker not found")

s = s.replace(old, new)

old2 = '''setBusinessProfileSaved(Boolean(savedProfile.business_name));'''
new2 = '''setBusinessProfileSaved(true);'''

s = s.replace(old2, new2)

TARGET.write_text(s, encoding="utf-8")

print("SAVE_PROFILE_SAVED_BADGE_FIXED")
print(f"Replacements: {count}")
print(f"Backup: {backup}")