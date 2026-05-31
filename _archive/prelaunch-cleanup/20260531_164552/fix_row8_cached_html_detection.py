from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "live_verify_integrations_client_connections_hub.py"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row8_cached_html_detection_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "live_verify_integrations_client_connections_hub.py")

text = target.read_text(encoding="utf-8")

old = '''
    prerender_cache = str(r.get("cache", "")).upper() == "PRERENDER"

    if prerender_cache:
        continue
'''

new = '''
    cache_value = str(r.get("cache", "")).upper()
    body_sample = str(r.get("body_sample", ""))

    cached_static_html = (
        cache_value in ["PRERENDER", "HIT"]
        and "<!DOCTYPE html>" in body_sample
    )

    if cached_static_html:
        continue
'''

if old not in text:
    raise SystemExit("Expected prerender cache block not found.")

text = text.replace(old, new, 1)

target.write_text(text, encoding="utf-8")

print("ROW8_CACHED_HTML_DETECTION_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")