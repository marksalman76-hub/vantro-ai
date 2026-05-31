from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / "production" / f"controlled_live_execution_whitelist_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

MAIN = ROOT / "backend" / "app" / "main.py"

if not MAIN.exists():
    raise SystemExit("backend/app/main.py not found")

target = BACKUP / "backend" / "app" / "main.py"
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(MAIN, target)

text = MAIN.read_text(encoding="utf-8", errors="ignore")

marker = "# CONTROLLED_LIVE_EXECUTION_WHITELIST_V1"

if marker not in text:
    inject = '''
# CONTROLLED_LIVE_EXECUTION_WHITELIST_V1
CONTROLLED_OWNER_APPROVED_LIVE_EXECUTION_PATHS = {
    "/admin/provider-activation-visibility/evaluate",
}

def _is_controlled_owner_approved_live_execution_path(path: str) -> bool:
    return path in CONTROLLED_OWNER_APPROVED_LIVE_EXECUTION_PATHS
'''

    # Place near app/runtime helpers if possible, otherwise append safely.
    if "app = FastAPI" in text:
        text = text.replace("app = FastAPI", inject + "\\n\\napp = FastAPI", 1)
    else:
        text += "\\n\\n" + inject + "\\n"

# Patch common production security block condition safely.
if "security_enforcement_blocked" in text and "_is_controlled_owner_approved_live_execution_path" in text:
    text = text.replace(
        'return JSONResponse(status_code=403, content={"success": False, "error": "security_enforcement_blocked", "message": "Request blocked by production security enforcement.", "security_profile": "priority5_security_audit_enforcement_v1"})',
        'if not _is_controlled_owner_approved_live_execution_path(str(request.url.path)):\\n            return JSONResponse(status_code=403, content={"success": False, "error": "security_enforcement_blocked", "message": "Request blocked by production security enforcement.", "security_profile": "priority5_security_audit_enforcement_v1"})'
    )

MAIN.write_text(text, encoding="utf-8")

print("CONTROLLED_LIVE_EXECUTION_WHITELIST_INSTALLED")
print("Backup:", BACKUP)