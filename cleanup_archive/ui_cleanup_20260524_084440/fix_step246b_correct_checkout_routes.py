from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
TEST = ROOT / "test_step246_paid_checkout_smoke_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"test_step246_before_step246b_{timestamp}.py"
backup.write_text(TEST.read_text(encoding="utf-8"), encoding="utf-8")

text = TEST.read_text(encoding="utf-8")

text = text.replace(
    'get_json("/admin/stripe/checkout-readiness")',
    'get_json("/admin/billing/stripe-checkout-readiness")'
)

text = text.replace(
    'post_json("/admin/stripe/create-checkout-session", payload)',
    'post_json("/admin/billing/create-checkout-session", payload)'
)

TEST.write_text(text, encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_246B_CORRECT_CHECKOUT_ROUTES_OK")
print(f"Backup: {backup}")
print(f"Updated: {TEST}")