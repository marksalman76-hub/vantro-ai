from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
TEST = ROOT / "test_step246_paid_checkout_smoke_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"test_step246_before_step246c_{timestamp}.py"
backup.write_text(TEST.read_text(encoding="utf-8"), encoding="utf-8")

text = TEST.read_text(encoding="utf-8")

old = '''session_id = checkout.get("checkout_session_id") or checkout.get("session_id")'''

new = '''session_id = (
    checkout.get("checkout_session_id")
    or checkout.get("session_id")
    or checkout.get("stripe_checkout_session_id")
)'''

if old not in text:
    raise RuntimeError("session_id assignment block not found")

text = text.replace(old, new)

TEST.write_text(text, encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_246C_ACCEPT_STRIPE_SESSION_ID_FIELD_OK")
print(f"Backup: {backup}")
print(f"Updated: {TEST}")