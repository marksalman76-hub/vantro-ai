from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "admin" / "page.tsx"

backup_dir = root / "backups" / f"admin_billing_static_display_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

old = '''                <div>
                  <label>Subscription tracking</label>
                  <h3>Active</h3>
                  <p>Last cycle: 22 May 2026</p>
                </div>
                <div>
                  <label>Monthly revenue</label>
                  <h3 className="gradient">$2,232</h3>
                  <p>8 active subscriptions</p>
                </div>'''

new = '''                <div>
                  <label>Subscription tracking</label>
                  <h3>{(runtime?.billing_summary?.subscriptions_active ?? 0) > 0 ? "Active" : "No live subscriptions"}</h3>
                  <p>Live subscription count: {runtime?.billing_summary?.subscriptions_active ?? 0}</p>
                </div>
                <div>
                  <label>Monthly revenue</label>
                  <h3 className="gradient">${runtime?.billing_summary?.monthly_revenue ?? 0}</h3>
                  <p>{runtime?.billing_summary?.subscriptions_active ?? 0} active subscriptions</p>
                </div>'''

if old not in text:
    raise SystemExit("Static billing display block not found.")

text = text.replace(old, new, 1)
target.write_text(text, encoding="utf-8")

print("ADMIN_BILLING_STATIC_DISPLAY_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")