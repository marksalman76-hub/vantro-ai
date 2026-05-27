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
