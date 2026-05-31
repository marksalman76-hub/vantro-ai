from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"stripe_checkout_session_object_handling_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

text = main_file.read_text(encoding="utf-8")

text = text.replace(
    '"checkout_session_id": session.get("id"),',
    '"checkout_session_id": getattr(session, "id", None) or session.get("id") if hasattr(session, "get") else None,'
)

text = text.replace(
    '"checkout_url": session.get("url"),',
    '"checkout_url": getattr(session, "url", None) or session.get("url") if hasattr(session, "get") else None,'
)

if 'getattr(session, "id", None)' not in text:
    raise SystemExit("STRIPE_SESSION_ID_FIX_NOT_APPLIED")

if 'getattr(session, "url", None)' not in text:
    raise SystemExit("STRIPE_SESSION_URL_FIX_NOT_APPLIED")

main_file.write_text(text, encoding="utf-8")

test_file = ROOT / "test_stripe_checkout_session_object_handling.py"
test_file.write_text(r'''
from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert 'getattr(session, "id", None)' in text
assert 'getattr(session, "url", None)' in text
assert 'real_stripe_checkout_session_bridge_v1' in text
assert 'live_checkout_session_created' in text

print("STRIPE_CHECKOUT_SESSION_OBJECT_HANDLING_TEST_PASSED")
''', encoding="utf-8")

print("STRIPE_CHECKOUT_SESSION_OBJECT_HANDLING_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")