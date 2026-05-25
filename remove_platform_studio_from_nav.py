from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_remove_platform_studio_nav_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Remove exact nav anchor patterns.
patterns = [
    r'\s*<a\s+href="#platform"[^>]*>\s*Platform\s*</a>',
    r'\s*<a\s+href="/#platform"[^>]*>\s*Platform\s*</a>',
    r'\s*<a\s+href="/platform"[^>]*>\s*Platform\s*</a>',
    r'\s*<Link\s+href="#platform"[^>]*>\s*Platform\s*</Link>',
    r'\s*<Link\s+href="/#platform"[^>]*>\s*Platform\s*</Link>',
    r'\s*<Link\s+href="/platform"[^>]*>\s*Platform\s*</Link>',
    r'\s*<a\s+href="#studio"[^>]*>\s*Studio\s*</a>',
    r'\s*<a\s+href="/#studio"[^>]*>\s*Studio\s*</a>',
    r'\s*<a\s+href="/studio"[^>]*>\s*Studio\s*</a>',
    r'\s*<Link\s+href="#studio"[^>]*>\s*Studio\s*</Link>',
    r'\s*<Link\s+href="/#studio"[^>]*>\s*Studio\s*</Link>',
    r'\s*<Link\s+href="/studio"[^>]*>\s*Studio\s*</Link>',
]

for pattern in patterns:
    s = re.sub(pattern, "", s, flags=re.IGNORECASE)

# Remove possible array/object nav entries.
s = re.sub(r'\s*\{\s*label:\s*"Platform"\s*,\s*href:\s*"[^"]*"\s*\}\s*,?', "", s)
s = re.sub(r'\s*\{\s*label:\s*"Studio"\s*,\s*href:\s*"[^"]*"\s*\}\s*,?', "", s)
s = re.sub(r'\s*\["Platform"\s*,\s*"[^"]*"\]\s*,?', "", s)
s = re.sub(r'\s*\["Studio"\s*,\s*"[^"]*"\]\s*,?', "", s)

PAGE.write_text(s, encoding="utf-8")

print("PLATFORM_AND_STUDIO_REMOVED_FROM_NAV")
print(f"Backup: {backup}")