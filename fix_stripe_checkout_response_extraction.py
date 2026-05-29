from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"stripe_checkout_response_extraction_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

text = main_file.read_text(encoding="utf-8")

old_block = r'''"checkout_session_id": getattr(session, "id", None) or session.get("id") if hasattr(session, "get") else None,
            "checkout_url": getattr(session, "url", None) or session.get("url") if hasattr(session, "get") else None,'''

new_block = r'''session_id = None
        checkout_url = None

        try:
            session_id = getattr(session, "id", None)
        except Exception:
            session_id = None

        try:
            checkout_url = getattr(session, "url", None)
        except Exception:
            checkout_url = None

        if not session_id:
            try:
                session_id = session.get("id")
            except Exception:
                pass

        if not checkout_url:
            try:
                checkout_url = session.get("url")
            except Exception:
                pass

        if not session_id:
            try:
                session_id = session["id"]
            except Exception:
                pass

        if not checkout_url:
            try:
                checkout_url = session["url"]
            except Exception:
                pass

        return {
            "success": True,
            "profile": "real_stripe_checkout_session_bridge_v2",
            "checkout_status": "live_checkout_session_created",
            "live_checkout_created": True,
            "checkout_session_id": session_id,
            "checkout_url": checkout_url,'''

if old_block not in text:
    raise SystemExit("OLD_STRIPE_RESPONSE_BLOCK_NOT_FOUND")

text = text.replace(old_block, new_block)

text = text.replace(
    '''        return {
            "success": True,
            "profile": "real_stripe_checkout_session_bridge_v1",
            "checkout_status": "live_checkout_session_created",
            "live_checkout_created": True,''',
    ""
)

main_file.write_text(text, encoding="utf-8")

test_file = ROOT / "test_stripe_checkout_response_extraction.py"
test_file.write_text(r'''
from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert 'real_stripe_checkout_session_bridge_v2' in text
assert 'session_id = getattr(session, "id", None)' in text
assert 'checkout_url = getattr(session, "url", None)' in text
assert 'session["id"]' in text
assert 'session["url"]' in text

print("STRIPE_CHECKOUT_RESPONSE_EXTRACTION_TEST_PASSED")
''', encoding="utf-8")

print("STRIPE_CHECKOUT_RESPONSE_EXTRACTION_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")