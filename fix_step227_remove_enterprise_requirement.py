from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
TEST = ROOT / "test_step227_live_stripe_env_readiness.py"
RUNTIME = ROOT / "backend" / "app" / "core" / "stripe_checkout_runtime.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in [TEST, RUNTIME]:
    backup = BACKUPS / f"{file.stem}_before_step227_remove_enterprise_{timestamp}{file.suffix}"
    backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

test_text = TEST.read_text(encoding="utf-8")
test_text = test_text.replace(
    '    "STRIPE_PRICE_ENTERPRISE_MONTHLY",\n',
    ""
)
TEST.write_text(test_text, encoding="utf-8")

runtime_text = RUNTIME.read_text(encoding="utf-8")
runtime_text = runtime_text.replace(
    '    "enterprise": "STRIPE_PRICE_ENTERPRISE_MONTHLY",\n',
    ""
)
RUNTIME.write_text(runtime_text, encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)
py_compile.compile(str(RUNTIME), doraise=True)

print("STEP_227_ENTERPRISE_REQUIREMENT_REMOVED")
print(f"Updated: {TEST}")
print(f"Updated: {RUNTIME}")