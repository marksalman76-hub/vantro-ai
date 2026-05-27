from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row3_render_customer_lock_notice_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

if "customerPortalSelectionLockedNotice()" not in text:
    raise SystemExit("customerPortalSelectionLockedNotice function missing.")

render_block = """
        <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 shadow-sm">
          <div className="font-semibold">
            Agent selections are locked after activation
          </div>

          <div className="mt-1 text-amber-900">
            Package changes, swaps, upgrades, or added agents require owner/admin approval.
          </div>
        </div>
"""

anchor = '<div className="space-y-6">'

if anchor not in text:
    raise SystemExit("Could not locate stable render anchor.")

updated = text.replace(anchor, anchor + "\n" + render_block, 1)

target.write_text(updated, encoding="utf-8")

print("ROW3_RENDER_LOCK_NOTICE_LIVE_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")