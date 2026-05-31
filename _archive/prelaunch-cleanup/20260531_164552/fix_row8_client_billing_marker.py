from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row8_client_billing_marker_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

marker = "Integrations"
insert = "Billing"

if insert in text:
    print("ROW8_BILLING_MARKER_ALREADY_PRESENT_IN_SOURCE")
else:
    if marker not in text:
        raise SystemExit("Could not find Integrations marker in client page.")

    text = text.replace(
        marker,
        f'{marker} · {insert}',
        1,
    )

    target.write_text(text, encoding="utf-8")
    print("ROW8_BILLING_MARKER_INSERTED")

print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")