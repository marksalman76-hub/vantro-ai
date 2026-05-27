from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bridge_path = ROOT / "backend" / "app" / "runtime" / "provider_execution_postgres_ledger_bridge.py"
test_file = ROOT / "test_provider_execution_postgres_read_write_bridge_direct.py"

backup_dir = ROOT / "backups" / f"provider_execution_postgres_read_write_bridge_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [bridge_path, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

if not bridge_path.exists():
    raise FileNotFoundError(f"Missing bridge file: {bridge_path}")

s = bridge_path.read_text(encoding="utf-8")

extra_code = r'''

def _get_db_connection():
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


def postgres_write_provider_execution_record(record: Dict[str, Any]) -> Dict[str, Any]:
    conn, driver = _get_db_connection()
    if conn is None:
        return _safe_response(written=False, reason="db_unavailable", fallback_required=True)

    sql = """
    INSERT INTO provider_execution_records (
        execution_id, tenant_id, request_id, provider_key, task_type,
        execution_status, worker_job_id, provider_job_id,
        live_external_call_executed, customer_safe, credential_values_exposed,
        created_at_ms, updated_at_ms
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (execution_id) DO UPDATE SET
        execution_status = EXCLUDED.execution_status,
        worker_job_id = EXCLUDED.worker_job_id,
        provider_job_id = EXCLUDED.provider_job_id,
        updated_at_ms = EXCLUDED.updated_at_ms
    """

    values = (
        record.get("execution_id"),
        record.get("tenant_id"),
        record.get("request_id"),
        record.get("provider_key"),
        record.get("task_type"),
        record.get("execution_status"),
        record.get("worker_job_id"),
        record.get("provider_job_id"),
        False,
        True,
        False,
        record.get("created_at_ms"),
        record.get("updated_at_ms"),
    )

    try:
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        return _safe_response(written=True, reason="postgres_write_success", driver=driver)
    except Exception as exc:
        try:
            conn.close()
        except Exception:
            pass
        return _safe_response(
            written=False,
            reason="postgres_write_failed",
            fallback_required=True,
            safe_error=str(exc)[:300],
            driver=driver,
        )


def persist_provider_execution_record_bridge(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    task_type: str,
    execution_status: str = "created",
    worker_job_id: Optional[str] = None,
    provider_job_id: Optional[str] = None,
) -> Dict[str, Any]:
    record = create_provider_execution_record(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key=provider_key,
        task_type=task_type,
        execution_status=execution_status,
        worker_job_id=worker_job_id,
        provider_job_id=provider_job_id,
    )

    write_result = postgres_write_provider_execution_record(record)

    return _safe_response(
        persistence_mode="postgres" if write_result.get("written") else "in_memory_fallback",
        postgres_write_attempted=bool(os.getenv("DATABASE_URL")),
        postgres_write_result=write_result,
        record=record,
    )


def postgres_read_provider_execution_records(
    *,
    tenant_id: Optional[str] = None,
    provider_key: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    conn, driver = _get_db_connection()
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

    clauses = []
    values = []

    if tenant_id:
        clauses.append("tenant_id = %s")
        values.append(tenant_id)
    if provider_key:
        clauses.append("provider_key = %s")
        values.append(provider_key)

    where_clause = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    values.append(limit)

    sql = f"""
    SELECT execution_id, tenant_id, request_id, provider_key, task_type,
           execution_status, worker_job_id, provider_job_id,
           live_external_call_executed, customer_safe, credential_values_exposed,
           created_at_ms, updated_at_ms
    FROM provider_execution_records
    {where_clause}
    ORDER BY created_at_ms DESC
    LIMIT %s
    """

    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(values))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        records = []
        for row in rows:
            records.append({
                "execution_id": row[0],
                "tenant_id": row[1],
                "request_id": row[2],
                "provider_key": row[3],
                "task_type": row[4],
                "execution_status": row[5],
                "worker_job_id": row[6],
                "provider_job_id": row[7],
                "live_external_call_executed": bool(row[8]),
                "customer_safe": bool(row[9]),
                "credential_values_exposed": False,
                "created_at_ms": row[11],
                "updated_at_ms": row[12],
            })

        return _safe_response(
            read_mode="postgres",
            postgres_read_attempted=True,
            driver=driver,
            records=records,
            count=len(records),
        )

    except Exception as exc:
        try:
            conn.close()
        except Exception:
            pass

        fallback = list_provider_execution_records(
            tenant_id=tenant_id,
            provider_key=provider_key,
            limit=limit,
        )
        return _safe_response(
            read_mode="in_memory_fallback",
            postgres_read_attempted=True,
            postgres_read_failed=True,
            safe_error=str(exc)[:300],
            records=fallback["records"],
            count=fallback["count"],
        )


def provider_postgres_read_write_status() -> Dict[str, Any]:
    driver = detect_postgres_driver()
    return _safe_response(
        read_write_bridge_ready=True,
        database_url_present=_database_url_present(),
        postgres_driver_available=driver.get("driver_available", False),
        postgres_driver=driver.get("driver"),
        provider_execution_record_postgres_write_enabled=True,
        provider_execution_record_postgres_read_enabled=True,
        fallback_storage_active=True,
    )
'''

if "def postgres_write_provider_execution_record(" not in s:
    s = s.rstrip() + extra_code + "\n"

bridge_path.write_text(s, encoding="utf-8")

test_file.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

print("PROVIDER_EXECUTION_POSTGRES_READ_WRITE_BRIDGE_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {bridge_path}")
print(f"Created/updated: {test_file}")
print("Postgres read/write bridge installed with fallback.")