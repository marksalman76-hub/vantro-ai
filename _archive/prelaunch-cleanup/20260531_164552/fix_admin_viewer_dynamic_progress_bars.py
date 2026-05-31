from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/admin/live-execution/page.tsx")
backup = Path("backups") / f"admin_viewer_dynamic_progress_bars_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

anchor = '''  const completed = result?.success === true;
  const liveCall = adapter?.live_external_call_executed === true;'''

replacement = '''  const completed = result?.success === true;
  const failed = result && result?.success !== true;
  const liveCall = adapter?.live_external_call_executed === true;

  const progress = {
    generated: completed ? 100 : running ? 65 : failed ? 35 : 0,
    reviewed: completed ? 55 : running ? 15 : failed ? 10 : 0,
    approved: completed ? 25 : 0,
    pending: completed ? 0 : running ? 35 : failed ? 65 : 0,
  };'''

if anchor not in s:
    raise SystemExit("Could not find completed/liveCall anchor.")

s = s.replace(anchor, replacement)

old = '''                ["Generated", completed ? 100 : running ? 65 : 20],
                ["Reviewed", completed ? 55 : 15],
                ["Approved", completed ? 25 : 0],
                ["Pending", completed ? 65 : 35],'''

new = '''                ["Generated", progress.generated],
                ["Reviewed", progress.reviewed],
                ["Approved", progress.approved],
                ["Pending", progress.pending],'''

if old not in s:
    raise SystemExit("Could not find old progress block.")

s = s.replace(old, new)

p.write_text(s, encoding="utf-8")

print("ADMIN_VIEWER_DYNAMIC_PROGRESS_BARS_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {p}")