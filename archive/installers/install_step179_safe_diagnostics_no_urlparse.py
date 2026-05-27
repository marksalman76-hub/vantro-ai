from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
RUNTIME = ROOT / "backend" / "app" / "core" / "postgres_account_runtime.py"

text = RUNTIME.read_text(encoding="utf-8")

start = text.index("def database_readiness():")
end = text.index("\n\nsafe_initialise_tables()", start)

new_block = r'''def database_readiness():
    raw = DATABASE_URL or ""

    safe_url_details = {
        "database_url_present": bool(raw),
        "length": len(raw),
        "starts_with_postgresql": raw.startswith("postgresql://"),
        "contains_placeholder": "[YOUR-PASSWORD]" in raw,
        "contains_spaces": " " in raw,
        "contains_pooler_host": "pooler.supabase.com" in raw,
        "contains_project_ref_username": "postgres.udcvkzgxojklwwdocokv" in raw,
        "contains_direct_host": "db.udcvkzgxojklwwdocokv.supabase.co" in raw,
        "contains_at_symbol": "@" in raw,
        "contains_database_suffix": raw.endswith("/postgres"),
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

text = text[:start] + new_block + text[end:]

RUNTIME.write_text(text, encoding="utf-8")

print("STEP_179_SAFE_DIAGNOSTICS_NO_URLPARSE_INSTALLED")
print("STEP_179_OK")