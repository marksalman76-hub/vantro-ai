from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
RUNTIME = ROOT / "backend" / "app" / "core" / "postgres_account_runtime.py"

text = RUNTIME.read_text(encoding="utf-8")

old = '''def database_readiness():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row = cur.fetchone()

        return {
            "success": True,
            "database_available": True,
            "startup_status": POSTGRES_STARTUP_STATUS,
            "test_result": row[0] if row else None,
        }
    except Exception as exc:
        return {
            "success": False,
            "database_available": False,
            "startup_status": POSTGRES_STARTUP_STATUS,
            "error": str(exc),
        }
'''

new = '''def database_readiness():
    from urllib.parse import urlparse

    parsed = urlparse(DATABASE_URL or "")

    safe_url_details = {
        "database_url_present": bool(DATABASE_URL),
        "scheme": parsed.scheme,
        "username": parsed.username,
        "password_present": bool(parsed.password),
        "password_length": len(parsed.password or ""),
        "host": parsed.hostname,
        "port": parsed.port,
        "database": parsed.path.lstrip("/") if parsed.path else None,
        "contains_placeholder": "[YOUR-PASSWORD]" in (DATABASE_URL or ""),
        "contains_spaces": " " in (DATABASE_URL or ""),
    }

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row = cur.fetchone()

        return {
            "success": True,
            "database_available": True,
            "startup_status": POSTGRES_STARTUP_STATUS,
            "database_url_details": safe_url_details,
            "test_result": row[0] if row else None,
        }
    except Exception as exc:
        return {
            "success": False,
            "database_available": False,
            "startup_status": POSTGRES_STARTUP_STATUS,
            "database_url_details": safe_url_details,
            "error": str(exc),
        }
'''

if old not in text:
    raise SystemExit("database_readiness block not found")

text = text.replace(old, new)

RUNTIME.write_text(text, encoding="utf-8")

print("STEP_178_DATABASE_URL_DIAGNOSTICS_INSTALLED")
print("STEP_178_OK")