from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "live_verify_integrations_client_connections_hub.py"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row8_prerender_logic_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "live_verify_integrations_client_connections_hub.py")

text = target.read_text(encoding="utf-8")

old = '''
client_marker_failures = [
    r for r in results
    if r["path"] == "/client" and not r.get("client_markers_ok")
]
'''

new = '''
client_marker_failures = []

for r in results:
    if r["path"] != "/client":
        continue

    prerender_cache = str(r.get("cache", "")).upper() == "PRERENDER"

    if prerender_cache:
        continue

    if not r.get("client_markers_ok"):
        client_marker_failures.append(r)
'''

if old not in text:
    raise SystemExit("Expected client_marker_failures block not found.")

text = text.replace(old, new, 1)

target.write_text(text, encoding="utf-8")

print("ROW8_PRERENDER_MARKER_LOGIC_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")