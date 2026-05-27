from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_execution_postgres_migration_apply_routes_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_migration_apply_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

if test_file.exists():
    (backup_dir / test_file.name).write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider execution Postgres migration apply routes
# Added by wire_provider_execution_postgres_migration_apply_routes.py
# Purpose:
# - expose DB driver/schema apply readiness
# - apply schema only when DATABASE_URL and driver are available
# - keep safe fallback active on failure
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
        apply_provider_ledger_schema_with_driver,
        detect_postgres_driver,
        provider_postgres_migration_apply_status,
    )
except Exception:  # pragma: no cover
    apply_provider_ledger_schema_with_driver = None
    detect_postgres_driver = None
    provider_postgres_migration_apply_status = None


@app.get("/provider-postgres-migration/status")
def provider_postgres_migration_status_route():
    if provider_postgres_migration_apply_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_migration_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_migration_apply_status()


@app.get("/provider-postgres-migration/driver")
def provider_postgres_migration_driver_route():
    if detect_postgres_driver is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_migration_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return detect_postgres_driver()


@app.post("/provider-postgres-migration/apply")
async def provider_postgres_migration_apply_route():
    if apply_provider_ledger_schema_with_driver is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_migration_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return apply_provider_ledger_schema_with_driver()
'''

marker = "# Provider execution Postgres migration apply routes"
if marker in main_text:
    print("PROVIDER_POSTGRES_MIGRATION_APPLY_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_POSTGRES_MIGRATION_APPLY_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("DATABASE_URL", None)

driver = client.get("/provider-postgres-migration/driver").json()
assert "driver_available" in driver
assert driver["credential_values_exposed"] is False

status_no_db = client.get("/provider-postgres-migration/status").json()
assert status_no_db["migration_apply_ready"] is True
assert status_no_db["database_url_present"] is False
assert status_no_db["schema_sql_present"] is True
assert status_no_db["fallback_storage_active"] is True
assert status_no_db["credential_values_exposed"] is False

apply_no_db = client.post("/provider-postgres-migration/apply").json()
assert apply_no_db["status"] == "skipped"
assert apply_no_db["reason"] == "DATABASE_URL_missing"
assert apply_no_db["applied"] is False
assert apply_no_db["fallback_storage_active"] is True
assert apply_no_db["credential_values_exposed"] is False

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

status_with_db = client.get("/provider-postgres-migration/status").json()
assert status_with_db["database_url_present"] is True
assert status_with_db["schema_sql_present"] is True
assert status_with_db["credential_values_exposed"] is False

apply_with_db = client.post("/provider-postgres-migration/apply").json()
assert apply_with_db["status"] in {"skipped", "failed", "applied"}
assert apply_with_db["credential_values_exposed"] is False
assert apply_with_db["fallback_storage_active"] is True

print("PROVIDER_POSTGRES_MIGRATION_APPLY_ROUTES_DIRECT_TESTS_PASSED")
print("driver_available", driver["driver_available"], driver.get("driver"))
print("status_no_db", status_no_db["database_url_present"], status_no_db["fallback_storage_active"])
print("apply_no_db", apply_no_db["status"], apply_no_db["reason"])
print("status_with_db", status_with_db["database_url_present"], status_with_db["postgres_driver_available"])
print("apply_with_db", apply_with_db["status"], apply_with_db["reason"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_POSTGRES_MIGRATION_APPLY_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")
print("Migration apply routes installed safely.")