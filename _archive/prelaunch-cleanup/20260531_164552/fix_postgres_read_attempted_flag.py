from pathlib import Path

p = Path("backend/app/runtime/provider_execution_postgres_ledger_bridge.py")
s = p.read_text(encoding="utf-8")

old = '''    conn, driver = _get_db_connection()
    if conn is None:
        fallback = list_provider_execution_records(
            tenant_id=tenant_id,
            provider_key=provider_key,
            limit=limit,
        )
        return _safe_response(
            read_mode="in_memory_fallback",
            postgres_read_attempted=False,
            records=fallback["records"],
            count=fallback["count"],
        )
'''

new = '''    conn, driver = _get_db_connection()
    db_url_present = bool(os.getenv("DATABASE_URL"))
    if conn is None:
        fallback = list_provider_execution_records(
            tenant_id=tenant_id,
            provider_key=provider_key,
            limit=limit,
        )
        return _safe_response(
            read_mode="in_memory_fallback",
            postgres_read_attempted=db_url_present,
            postgres_connection_available=False,
            records=fallback["records"],
            count=fallback["count"],
        )
'''

if old not in s:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

p.write_text(s.replace(old, new), encoding="utf-8")
print("POSTGRES_READ_ATTEMPTED_FLAG_FIXED")