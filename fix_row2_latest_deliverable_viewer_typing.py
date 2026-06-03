from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row2_latest_deliverable_viewer_typing_fix_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

component = ROOT / "frontend" / "src" / "app" / "client" / "LatestDeliverableViewer.tsx"

if not component.exists():
    raise SystemExit("LatestDeliverableViewer.tsx not found")

shutil.copy2(component, backup / "LatestDeliverableViewer.tsx")

text = component.read_text(encoding="utf-8")
text = text.replace(
    'const asset = payload.asset || payload.result?.asset || payload.data?.asset || {};',
    'const asset: Record<string, unknown> = (payload.asset || payload.result?.asset || payload.data?.asset || {}) as Record<string, unknown>;'
)

component.write_text(text, encoding="utf-8")

print("ROW2_LATEST_DELIVERABLE_VIEWER_TYPING_FIX_APPLIED")
print(f"Backup: {backup}")
print(f"Updated: {component}")