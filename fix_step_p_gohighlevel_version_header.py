from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

p = ROOT / "backend" / "app" / "core" / "integration_live_adapter_registry.py"
backup = BACKUPS / f"integration_live_adapter_registry_before_step_p_ghl_version_header_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(p.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

s = p.read_text(encoding="utf-8", errors="ignore")

old = '''    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
'''

new = '''    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    if provider == "GoHighLevel":
        headers["Version"] = "2021-07-28"
        headers["Accept"] = "application/json"
'''

if old not in s:
    raise SystemExit("TARGET_HEADER_BLOCK_NOT_FOUND")

s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")

print("STEP_P_GHL_VERSION_HEADER_FIXED")
print(f"Backup: {backup}")