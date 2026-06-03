from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"admin_sidebar_creative_assets_link_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

shutil.copy2(ADMIN_PAGE, BACKUP / "page.tsx")

text = ADMIN_PAGE.read_text(encoding="utf-8", errors="ignore")

if "/admin/creative-assets" not in text:
    marker = 'href="#runtime-health"'
    idx = text.find(marker)

    if idx == -1:
        marker = "Runtime Health"
        idx = text.find(marker)

    if idx == -1:
        raise RuntimeError("Could not find sidebar insertion point")

    line_start = text.rfind("\n", 0, idx)
    block_start = text.rfind("<", 0, idx)
    insert_at = line_start if line_start != -1 else block_start

    sidebar_link = '''
            <a href="/admin/creative-assets" className="navLink">
              Creative Media Assets
            </a>
'''

    text = text[:insert_at] + sidebar_link + text[insert_at:]

ADMIN_PAGE.write_text(text, encoding="utf-8", newline="\n")

print("ADMIN_SIDEBAR_CREATIVE_ASSETS_LINK_PATCHED")
print(f"Backup: {BACKUP}")
print(f"Updated: {ADMIN_PAGE}")