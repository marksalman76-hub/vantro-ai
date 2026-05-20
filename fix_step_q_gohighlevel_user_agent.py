from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

target = ROOT / "backend" / "app" / "core" / "integration_live_adapter_registry.py"

backup = BACKUPS / f"integration_live_adapter_registry_before_step_q_user_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(target.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

s = target.read_text(encoding="utf-8", errors="ignore")

old = '''    if provider == "GoHighLevel":
        headers["Version"] = "2021-07-28"
        headers["Accept"] = "application/json"
'''

new = '''    if provider == "GoHighLevel":
        headers["Version"] = "2021-07-28"
        headers["Accept"] = "application/json"
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
'''

if old not in s:
    raise SystemExit("TARGET_GHL_HEADER_BLOCK_NOT_FOUND")

s = s.replace(old, new, 1)

target.write_text(s, encoding="utf-8")

print("STEP_Q_GHL_USER_AGENT_FIXED")
print(f"Backup: {backup}")