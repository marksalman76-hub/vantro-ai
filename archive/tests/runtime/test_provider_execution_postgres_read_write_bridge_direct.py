import os

from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    persist_provider_execution_record_bridge,
    postgres_read_provider_execution_records,
    provider_postgres_read_write_status,
    reset_provider_postgres_bridge_fallback_for_tests,
)

reset = reset_provider_postgres_bridge_fallback_for_tests()
assert reset["reset"] is True

os.environ.pop("DATABASE_URL", None)

status_no_db = provider_postgres_read_write_status()
assert status_no_db["read_write_bridge_ready"] is True
assert status_no_db["database_url_present"] is False
assert status_no_db["fallback_storage_active"] is True
assert status_no_db["credential_values_exposed"] is False

record_no_db = persist_provider_execution_record_bridge(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    execution_status="created",
    worker_job_id="worker-123",
)
assert record_no_db["persistence_mode"] == "in_memory_fallback"
assert record_no_db["postgres_write_attempted"] is False
assert record_no_db["record"]["execution_status"] == "created"
assert record_no_db["credential_values_exposed"] is False

read_no_db = postgres_read_provider_execution_records(tenant_id="tenant-test")
assert read_no_db["read_mode"] == "in_memory_fallback"
assert read_no_db["postgres_read_attempted"] is False
assert read_no_db["count"] == 1

os.environ["DATABASE_URL"] = "postgresql://user:pass@example.com/db"

status_with_db = provider_postgres_read_write_status()
assert status_with_db["database_url_present"] is True
assert status_with_db["credential_values_exposed"] is False

record_with_bad_db = persist_provider_execution_record_bridge(
    tenant_id="tenant-test-db",
    request_id="request-test-db",
    provider_key="openai",
    task_type="image_generation",
    execution_status="created",
    worker_job_id="worker-456",
)
assert record_with_bad_db["postgres_write_attempted"] is True
assert record_with_bad_db["persistence_mode"] in {"postgres", "in_memory_fallback"}
assert record_with_bad_db["credential_values_exposed"] is False

read_with_bad_db = postgres_read_provider_execution_records(tenant_id="tenant-test-db")
assert read_with_bad_db["read_mode"] in {"postgres", "in_memory_fallback"}
assert read_with_bad_db["postgres_read_attempted"] is True
assert read_with_bad_db["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_POSTGRES_READ_WRITE_BRIDGE_DIRECT_TESTS_PASSED")
print("status_no_db", status_no_db["database_url_present"], status_no_db["fallback_storage_active"])
print("record_no_db", record_no_db["persistence_mode"], record_no_db["postgres_write_attempted"])
print("read_no_db", read_no_db["read_mode"], read_no_db["count"])
print("status_with_db", status_with_db["database_url_present"], status_with_db["postgres_driver_available"])
print("record_with_bad_db", record_with_bad_db["persistence_mode"], record_with_bad_db["postgres_write_attempted"])
print("read_with_bad_db", read_with_bad_db["read_mode"], read_with_bad_db["postgres_read_attempted"])
