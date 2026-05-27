from pathlib import Path
from datetime import datetime
import shutil
import re

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row3_customer_portal_lock_notice_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

required_1 = "Agent selections are locked after activation"
required_2 = "owner/admin approval"

if required_1 in text and required_2 in text:
    print("ROW3_LOCK_NOTICE_ALREADY_PRESENT")
    print(f"Backup folder: {backup_dir}")
    raise SystemExit(0)

notice = '''
        <section className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 shadow-sm">
          <div className="font-semibold">Agent selections are locked after activation</div>
          <div className="mt-1 text-amber-900">
            Any post-activation agent changes, swaps, upgrades, or package adjustments require owner/admin approval.
          </div>
        </section>
'''

patterns = [
    r"(<main[^>]*>)",
    r"(<div[^>]*className={[^}]*}[^>]*>)",
    r"(<div[^>]*className=\"[^\"]*\"[^>]*>)",
]

updated = None

for pattern in patterns:
    match = re.search(pattern, text)
    if match:
        updated = text[:match.end()] + notice + text[match.end():]
        break

if updated is None:
    raise SystemExit("Could not find a safe insertion point in client page.")

target.write_text(updated, encoding="utf-8")

print("ROW3_CUSTOMER_PORTAL_LOCK_NOTICE_MARKERS_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")