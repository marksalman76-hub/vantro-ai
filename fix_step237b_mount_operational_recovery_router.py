from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
ROUTES = ROOT / "backend" / "app" / "api" / "operational_recovery_routes.py"
RUNTIME = ROOT / "backend" / "app" / "core" / "operational_recovery_runtime.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"main_before_step237b_mount_operational_recovery_{timestamp}.py"
backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

text = MAIN.read_text(encoding="utf-8")

import_block = """from backend.app.api.operational_recovery_routes import (
    router as operational_recovery_router,
)
"""

if "operational_recovery_router" not in text:
    anchor = "from backend.app.api.subscription_policy_routes import router as subscription_policy_router\n"
    if anchor not in text:
        raise RuntimeError("Expected subscription_policy_router import anchor not found.")
    text = text.replace(anchor, anchor + import_block + "\n")

include_line = "app.include_router(operational_recovery_router)\n"

if include_line not in text:
    app_anchor = '''app = FastAPI(
    title="Ecommerce AI Agent Platform",
    version="1.1.0",
)
'''
    if app_anchor not in text:
        raise RuntimeError("Expected FastAPI app anchor not found.")
    text = text.replace(app_anchor, app_anchor + "\n" + include_line)

MAIN.write_text(text, encoding="utf-8")

py_compile.compile(str(RUNTIME), doraise=True)
py_compile.compile(str(ROUTES), doraise=True)
py_compile.compile(str(MAIN), doraise=True)

print("STEP_237B_OPERATIONAL_RECOVERY_ROUTER_MOUNT_OK")
print(f"Backup: {backup}")
print(f"Updated: {MAIN}")
print(f"Verified: {ROUTES}")
print(f"Verified: {RUNTIME}")