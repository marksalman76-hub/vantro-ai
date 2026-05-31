from pathlib import Path
from datetime import datetime

path = Path("backend/app/main.py")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("stripe_checkout_response_extraction_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "main.py"
backup.write_text(text, encoding="utf-8")

old = '''        session_id = None
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
'''

new = '''        session_payload = {}

        try:
            session_payload = dict(session)
        except Exception:
            session_payload = {}

        if not session_payload:
            try:
                session_payload = session.to_dict_recursive()
            except Exception:
                session_payload = {}

        if not session_payload:
            try:
                session_payload = session.to_dict()
            except Exception:
                session_payload = {}

        session_id = (
            session_payload.get("id")
            or getattr(session, "id", None)
        )

        checkout_url = (
            session_payload.get("url")
            or getattr(session, "url", None)
        )
'''

if old not in text:
    raise SystemExit("STRIPE_EXTRACTION_BLOCK_NOT_FOUND")

path.write_text(text.replace(old, new), encoding="utf-8")

print("STRIPE_CHECKOUT_RESPONSE_EXTRACTION_FIXED")
print("Backup:", backup)