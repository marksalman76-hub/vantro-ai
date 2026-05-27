from pathlib import Path

p = Path("backend/app/runtime/provider_execution_postgres_ledger_bridge.py")
s = p.read_text(encoding="utf-8")

old = '''def _get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None, None

    driver = detect_postgres_driver()
    if not driver.get("driver_available"):
        return None, None

    if driver["driver"] == "psycopg":
        import psycopg  # type: ignore
        return psycopg.connect(database_url), "psycopg"

    if driver["driver"] == "psycopg2":
        import psycopg2  # type: ignore
        return psycopg2.connect(database_url), "psycopg2"

    return None, None
'''

new = '''def _get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None, None

    driver = detect_postgres_driver()
    if not driver.get("driver_available"):
        return None, None

    try:
        if driver["driver"] == "psycopg":
            import psycopg  # type: ignore
            return psycopg.connect(database_url), "psycopg"

        if driver["driver"] == "psycopg2":
            import psycopg2  # type: ignore
            return psycopg2.connect(database_url), "psycopg2"
    except Exception:
        return None, driver.get("driver")

    return None, None
'''

if old not in s:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

p.write_text(s.replace(old, new), encoding="utf-8")
print("POSTGRES_READ_WRITE_DB_CONNECTION_SAFE_FALLBACK_FIXED")