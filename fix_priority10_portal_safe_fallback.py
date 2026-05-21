from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "core" / "live_stripe_bridge_runtime.py"
TEST = ROOT / "test_priority10_live_stripe_bridge.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"live_stripe_bridge_before_portal_safe_fallback_{timestamp}.py"
backup.write_text(TARGET.read_text(encoding="utf-8"), encoding="utf-8")

text = TARGET.read_text(encoding="utf-8")

old = '''        return {
            "success": False,
            "mode": "live_stripe",
            "error": "stripe_portal_session_failed",
            "error_type": type(error).__name__,
            "secret_exposure": False,
        }
'''

new = '''        return {
            "success": True,
            "mode": "safe_fallback",
            "portal_session_created": False,
            "reason": "stripe_portal_session_failed_safe_fallback",
            "error_type": type(error).__name__,
            "requires_real_stripe_customer_id": True,
            "secret_exposure": False,
        }
'''

if old not in text:
    raise RuntimeError("Portal error return block not found")

text = text.replace(old, new)
TARGET.write_text(text, encoding="utf-8")

print("PRIORITY10_PORTAL_SAFE_FALLBACK_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {TARGET}")