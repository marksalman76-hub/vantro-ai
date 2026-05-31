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
