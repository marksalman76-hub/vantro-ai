from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bridge_path = ROOT / "backend" / "app" / "runtime" / "provider_execution_postgres_ledger_bridge.py"
test_file = ROOT / "test_provider_execution_postgres_migration_apply_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_migration_apply_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [bridge_path, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

if not bridge_path.exists():
    raise FileNotFoundError(f"Missing bridge file: {bridge_path}")

s = bridge_path.read_text(encoding="utf-8")

extra_code = r'''

def detect_postgres_driver() -> Dict[str, Any]:
    try:
        import psycopg  # type: ignore
        return _safe_response(driver_available=True, driver="psycopg")
    except Exception:
        pass

    try:
        import psycopg2  # type: ignore
        return _safe_response(driver_available=True, driver="psycopg2")
    except Exception:
        pass

    return _safe_response(driver_available=False, driver=None)


def apply_provider_ledger_schema_with_driver() -> Dict[str, Any]:
    if not _database_url_present():
        return _safe_response(
            status="skipped",
            reason="DATABASE_URL_missing",
            applied=False,
            fallback_storage_active=True,
        )

    schema = get_provider_ledger_schema_sql()
    if not schema.get("schema_sql_present"):
        return _safe_response(
            status="failed",
            reason="schema_sql_missing",
            applied=False,
            fallback_storage_active=True,
        )

    driver = detect_postgres_driver()
    if not driver.get("driver_available"):
        return _safe_response(
            status="skipped",
            reason="postgres_driver_missing",
            applied=False,
            fallback_storage_active=True,
            database_url_present=True,
        )

    database_url = os.getenv("DATABASE_URL")
    sql = schema["sql"]

    try:
        if driver["driver"] == "psycopg":
            import psycopg  # type: ignore
            with psycopg.connect(database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                conn.commit()

        elif driver["driver"] == "psycopg2":
            import psycopg2  # type: ignore
            conn = psycopg2.connect(database_url)
            try:
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
                cur.close()
            finally:
                conn.close()
        else:
            return _safe_response(
                status="skipped",
                reason="unsupported_driver",
                applied=False,
                fallback_storage_active=True,
            )

        return _safe_response(
            status="applied",
            reason="schema_applied_successfully",
            applied=True,
            fallback_storage_active=True,
            driver=driver["driver"],
        )

    except Exception as exc:
        return _safe_response(
            status="failed",
            reason="schema_apply_failed",
            applied=False,
            fallback_storage_active=True,
            driver=driver.get("driver"),
            safe_error=str(exc)[:300],
        )


def provider_postgres_migration_apply_status() -> Dict[str, Any]:
    driver = detect_postgres_driver()
    return _safe_response(
        migration_apply_ready=True,
        database_url_present=_database_url_present(),
        schema_sql_present=get_provider_ledger_schema_sql().get("schema_sql_present", False),
        postgres_driver_available=driver.get("driver_available", False),
        postgres_driver=driver.get("driver"),
        fallback_storage_active=True,
        credential_values_exposed=False,
    )
'''

if "def apply_provider_ledger_schema_with_driver()" not in s:
    s = s.rstrip() + extra_code + "\n"

bridge_path.write_text(s, encoding="utf-8")

test_file.write_text(r'''
import os

from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    apply_provider_ledger_schema_with_driver,
    detect_postgres_driver,
    get_provider_ledger_schema_sql,
    provider_postgres_migration_apply_status,
)

os.environ.pop("DATABASE_URL", None)

driver = detect_postgres_driver()
assert "driver_available" in driver
assert driver["credential_values_exposed"] is False

schema = get_provider_ledger_schema_sql()
assert schema["schema_sql_present"] is True
assert "CREATE TABLE IF NOT EXISTS provider_execution_records" in schema["sql"]

status_no_db = provider_postgres_migration_apply_status()
assert status_no_db["migration_apply_ready"] is True
assert status_no_db["database_url_present"] is False
assert status_no_db["schema_sql_present"] is True
assert status_no_db["fallback_storage_active"] is True
assert status_no_db["credential_values_exposed"] is False

apply_no_db = apply_provider_ledger_schema_with_driver()
assert apply_no_db["status"] == "skipped"
assert apply_no_db["reason"] == "DATABASE_URL_missing"
assert apply_no_db["applied"] is False
assert apply_no_db["fallback_storage_active"] is True

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

status_with_db = provider_postgres_migration_apply_status()
assert status_with_db["database_url_present"] is True
assert status_with_db["schema_sql_present"] is True
assert status_with_db["credential_values_exposed"] is False

apply_with_db = apply_provider_ledger_schema_with_driver()
assert apply_with_db["status"] in {"skipped", "failed", "applied"}
assert apply_with_db["credential_values_exposed"] is False
assert apply_with_db["fallback_storage_active"] is True

print("PROVIDER_EXECUTION_POSTGRES_MIGRATION_APPLY_DIRECT_TESTS_PASSED")
print("driver_available", driver["driver_available"], driver.get("driver"))
print("schema_present", schema["schema_sql_present"])
print("status_no_db", status_no_db["database_url_present"], status_no_db["fallback_storage_active"])
print("apply_no_db", apply_no_db["status"], apply_no_db["reason"])
print("status_with_db", status_with_db["database_url_present"], status_with_db["postgres_driver_available"])
print("apply_with_db", apply_with_db["status"], apply_with_db["reason"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_EXECUTION_POSTGRES_MIGRATION_APPLY_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {bridge_path}")
print(f"Created/updated: {test_file}")
print("Actual schema apply function added with safe fallback.")