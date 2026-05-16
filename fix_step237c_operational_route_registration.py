from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()

MAIN = ROOT / "backend" / "app" / "main.py"
ROUTES = ROOT / "backend" / "app" / "api" / "operational_recovery_routes.py"

BACKUPS = ROOT / "backups"
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"main_before_step237c_{timestamp}.py"
backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

text = MAIN.read_text(encoding="utf-8")

IMPORT_BLOCK = '''
from backend.app.api.operational_recovery_routes import (
    router as operational_recovery_router,
)
'''

if "router as operational_recovery_router" not in text:
    subscription_anchor = "from backend.app.api.subscription_policy_routes import router as subscription_policy_router"
    if subscription_anchor not in text:
        raise RuntimeError("subscription_policy_router anchor not found")

    text = text.replace(
        subscription_anchor,
        subscription_anchor + "\n" + IMPORT_BLOCK.strip()
    )

FASTAPI_BLOCK = '''app = FastAPI(
    title="Ecommerce AI Agent Platform",
    version="1.1.0",
)
'''

ROUTER_LINE = "app.include_router(operational_recovery_router)"

if ROUTER_LINE not in text:
    if FASTAPI_BLOCK not in text:
        raise RuntimeError("FastAPI block not found")

    replacement = FASTAPI_BLOCK + "\n\n" + ROUTER_LINE + "\n"

    text = text.replace(
        FASTAPI_BLOCK,
        replacement
    )

MAIN.write_text(text, encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

checks = {
    "import_present": "router as operational_recovery_router" in main_text,
    "router_mount_present": ROUTER_LINE in main_text,
}

for name, passed in checks.items():
    print(name, passed)

failed = [k for k, v in checks.items() if not v]

if failed:
    raise RuntimeError(f"Verification failed: {failed}")

py_compile.compile(str(ROUTES), doraise=True)
py_compile.compile(str(MAIN), doraise=True)

print("STEP_237C_OPERATIONAL_ROUTE_REGISTRATION_OK")
print(f"Backup: {backup}")
print(f"Updated: {MAIN}")