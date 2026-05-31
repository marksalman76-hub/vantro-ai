from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_execution_postgres_read_write_routes_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_read_write_routes_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

if not main_path.exists():
    raise FileNotFoundError(f"Missing main.py: {main_path}")

main_text = main_path.read_text(encoding="utf-8")
(backup_dir / "main.py").write_text(main_text, encoding="utf-8")

if test_file.exists():
    (backup_dir / test_file.name).write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")

route_block = r'''

# ---------------------------------------------------------------------------
# Provider execution Postgres read/write bridge routes
# Added by wire_provider_execution_postgres_read_write_routes.py
# Purpose:
# - expose DB-capable execution record write/read bridge
# - keep safe fallback active when DB is unavailable
# - never expose credentials
# ---------------------------------------------------------------------------

try:
    from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
        persist_provider_execution_record_bridge,
        postgres_read_provider_execution_records,
        provider_postgres_read_write_status,
    )
except Exception:  # pragma: no cover
    persist_provider_execution_record_bridge = None
    postgres_read_provider_execution_records = None
    provider_postgres_read_write_status = None


@app.get("/provider-postgres-read-write/status")
def provider_postgres_read_write_status_route():
    if provider_postgres_read_write_status is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_read_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }
    return provider_postgres_read_write_status()


@app.post("/provider-postgres-read-write/execution-record")
async def provider_postgres_read_write_execution_record_route(payload: dict):
    if persist_provider_execution_record_bridge is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_read_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    safe_payload = dict(payload or {})
    return persist_provider_execution_record_bridge(
        tenant_id=safe_payload.get("tenant_id") or "unknown-tenant",
        request_id=safe_payload.get("request_id") or "unknown-request",
        provider_key=safe_payload.get("provider_key") or "unknown-provider",
        task_type=safe_payload.get("task_type") or "provider_generation",
        execution_status=safe_payload.get("execution_status") or "created",
        worker_job_id=safe_payload.get("worker_job_id"),
        provider_job_id=safe_payload.get("provider_job_id"),
    )


@app.get("/provider-postgres-read-write/execution-records")
def provider_postgres_read_write_execution_records_route(
    tenant_id: str = "",
    provider_key: str = "",
    limit: int = 50,
):
    if postgres_read_provider_execution_records is None:
        return {
            "status": "unavailable",
            "reason": "provider_postgres_read_write_runtime_not_loaded",
            "credential_values_exposed": False,
        }

    return postgres_read_provider_execution_records(
        tenant_id=tenant_id or None,
        provider_key=provider_key or None,
        limit=limit,
    )
'''

marker = "# Provider execution Postgres read/write bridge routes"
if marker in main_text:
    print("PROVIDER_POSTGRES_READ_WRITE_ROUTES_ALREADY_PRESENT")
else:
    main_path.write_text(main_text.rstrip() + "\n" + route_block + "\n", encoding="utf-8")
    print("PROVIDER_POSTGRES_READ_WRITE_ROUTES_WIRED")

test_file.write_text(r'''
import os
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

os.environ.pop("DATABASE_URL", None)

status_no_db = client.get("/provider-postgres-read-write/status").json()
assert status_no_db["read_write_bridge_ready"] is True
assert status_no_db["database_url_present"] is False
assert status_no_db["fallback_storage_active"] is True
assert status_no_db["credential_values_exposed"] is False

record_no_db = client.post(
    "/provider-postgres-read-write/execution-record",
    json={
        "tenant_id": "tenant-test",
        "request_id": "request-test",
        "provider_key": "openai",
        "task_type": "image_generation",
        "execution_status": "created",
        "worker_job_id": "worker-123",
    },
).json()
assert record_no_db["persistence_mode"] == "in_memory_fallback"
assert record_no_db["postgres_write_attempted"] is False
assert record_no_db["record"]["execution_status"] == "created"
assert record_no_db["credential_values_exposed"] is False

read_no_db = client.get(
    "/provider-postgres-read-write/execution-records?tenant_id=tenant-test"
).json()
assert read_no_db["read_mode"] == "in_memory_fallback"
assert read_no_db["postgres_read_attempted"] is False
assert read_no_db["count"] >= 1
assert read_no_db["credential_values_exposed"] is False

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

status_with_db = client.get("/provider-postgres-read-write/status").json()
assert status_with_db["database_url_present"] is True
assert status_with_db["credential_values_exposed"] is False

record_with_bad_db = client.post(
    "/provider-postgres-read-write/execution-record",
    json={
        "tenant_id": "tenant-test-db",
        "request_id": "request-test-db",
        "provider_key": "openai",
        "task_type": "image_generation",
        "execution_status": "created",
        "worker_job_id": "worker-456",
    },
).json()
assert record_with_bad_db["postgres_write_attempted"] is True
assert record_with_bad_db["persistence_mode"] in {"postgres", "in_memory_fallback"}
assert record_with_bad_db["credential_values_exposed"] is False

read_with_bad_db = client.get(
    "/provider-postgres-read-write/execution-records?tenant_id=tenant-test-db"
).json()
assert read_with_bad_db["read_mode"] in {"postgres", "in_memory_fallback"}
assert read_with_bad_db["postgres_read_attempted"] is True
assert read_with_bad_db["credential_values_exposed"] is False

print("PROVIDER_POSTGRES_READ_WRITE_ROUTES_DIRECT_TESTS_PASSED")
print("status_no_db", status_no_db["database_url_present"], status_no_db["fallback_storage_active"])
print("record_no_db", record_no_db["persistence_mode"], record_no_db["postgres_write_attempted"])
print("read_no_db", read_no_db["read_mode"], read_no_db["count"])
print("status_with_db", status_with_db["database_url_present"], status_with_db["postgres_driver_available"])
print("record_with_bad_db", record_with_bad_db["persistence_mode"], record_with_bad_db["postgres_write_attempted"])
print("read_with_bad_db", read_with_bad_db["read_mode"], read_with_bad_db["postgres_read_attempted"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_POSTGRES_READ_WRITE_ROUTES_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {main_path}")
print(f"Created/updated: {test_file}")