from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ROUTES = ROOT / "backend" / "app" / "api" / "subscription_policy_routes.py"
TEST = ROOT / "test_step225_cancel_reactivate_durable_sync_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"subscription_policy_routes_before_step225b_signature_fix_{timestamp}.py"
backup.write_text(ROUTES.read_text(encoding="utf-8"), encoding="utf-8")

text = ROUTES.read_text(encoding="utf-8")

text = text.replace(
    "        processed_at=recorded_at,\n",
    "",
)

ROUTES.write_text(text, encoding="utf-8")

py_compile.compile(str(ROUTES), doraise=True)
py_compile.compile(str(TEST), doraise=True)

print("STEP_225B_MUTATION_SIGNATURE_FIX_OK")
print(f"Backup: {backup}")
print(f"Updated: {ROUTES}")