from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "provider_execution_persistence_ledger.py"
test_file = ROOT / "test_provider_execution_persistence_ledger_direct.py"
backup_dir = ROOT / "backups" / f"provider_execution_persistence_ledger_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional


_PROVIDER_EXECUTION_RECORDS: Dict[str, Dict[str, Any]] = {}
_WORKER_EVENT_LEDGER: List[Dict[str, Any]] = []
_DISPATCH_ATTEMPT_RECORDS: List[Dict[str, Any]] = []
_RETRY_HISTORY_RECORDS: List[Dict[str, Any]] = []
_PROVIDER_LATENCY_RECORDS: List[Dict[str, Any]] = []


def _now_ms() -> int:
    return int(time.time() * 1000)


def reset_provider_execution_ledger_for_tests() -> Dict[str, Any]:
    _PROVIDER_EXECUTION_RECORDS.clear()
    _WORKER_EVENT_LEDGER.clear()
    _DISPATCH_ATTEMPT_RECORDS.clear()
    _RETRY_HISTORY_RECORDS.clear()
    _PROVIDER_LATENCY_RECORDS.clear()

    return {
        "reset": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def create_provider_execution_record(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    task_type: str,
    execution_status: str = "created",
    worker_job_id: Optional[str] = None,
    provider_job_id: Optional[str] = None,
) -> Dict[str, Any]:
    execution_id = f"provider_execution_{uuid.uuid4().hex[:16]}"
    now = _now_ms()

    record = {
        "execution_id": execution_id,
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "task_type": task_type,
        "execution_status": execution_status,
        "worker_job_id": worker_job_id,
        "provider_job_id": provider_job_id,
        "created_at_ms": now,
        "updated_at_ms": now,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _PROVIDER_EXECUTION_RECORDS[execution_id] = record
    return record


def update_provider_execution_record(
    *,
    execution_id: str,
    execution_status: Optional[str] = None,
    worker_job_id: Optional[str] = None,
    provider_job_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    record = _PROVIDER_EXECUTION_RECORDS.get(execution_id)
    if not record:
        return {
            "status": "not_found",
            "execution_id": execution_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if execution_status is not None:
        record["execution_status"] = execution_status
    if worker_job_id is not None:
        record["worker_job_id"] = worker_job_id
    if provider_job_id is not None:
        record["provider_job_id"] = provider_job_id
    if extra:
        safe_extra = {
            k: v for k, v in extra.items()
            if "secret" not in str(k).lower()
            and "token" not in str(k).lower()
            and "key" not in str(k).lower()
        }
        record["extra"] = safe_extra

    record["updated_at_ms"] = _now_ms()
    record["credential_values_exposed"] = False
    record["customer_safe"] = True
    return record


def get_provider_execution_record(execution_id: str) -> Dict[str, Any]:
    return _PROVIDER_EXECUTION_RECORDS.get(execution_id) or {
        "status": "not_found",
        "execution_id": execution_id,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_provider_execution_records(
    *,
    tenant_id: Optional[str] = None,
    provider_key: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    records = list(_PROVIDER_EXECUTION_RECORDS.values())

    if tenant_id:
        records = [r for r in records if r.get("tenant_id") == tenant_id]
    if provider_key:
        records = [r for r in records if r.get("provider_key") == provider_key]

    records = sorted(records, key=lambda r: r.get("created_at_ms", 0), reverse=True)[:limit]

    return {
        "records": records,
        "count": len(records),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def append_worker_event_ledger_entry(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    worker_job_id: str,
    provider_key: str,
    event_type: str,
    status: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    safe_details = {}
    for k, v in (details or {}).items():
        key_lower = str(k).lower()
        if "secret" in key_lower or "token" in key_lower or "api_key" in key_lower:
            continue
        safe_details[k] = v

    entry = {
        "ledger_id": f"provider_ledger_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "request_id": request_id,
        "execution_id": execution_id,
        "worker_job_id": worker_job_id,
        "provider_key": provider_key,
        "event_type": event_type,
        "status": status,
        "details": safe_details,
        "created_at_ms": _now_ms(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    _WORKER_EVENT_LEDGER.append(entry)
    return entry


def list_worker_event_ledger(
    *,
    tenant_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    entries = list(_WORKER_EVENT_LEDGER)

    if tenant_id:
        entries = [e for e in entries if e.get("tenant_id") == tenant_id]
    if execution_id:
        entries = [e for e in entries if e.get("execution_id") == execution_id]

    entries = sorted(entries, key=lambda e: e.get("created_at_ms", 0), reverse=True)[:limit]

    return {
        "entries": entries,
        "count": len(entries),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def record_dispatch_attempt(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    worker_job_id: str,
    provider_key: str,
    attempt_number: int,
    allowed_by_policy: bool,
    result_status: str,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    attempt = {
        "attempt_id": f"provider_attempt_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "request_id": request_id,
        "execution_id": execution_id,
        "worker_job_id": worker_job_id,
        "provider_key": provider_key,
        "attempt_number": attempt_number,
        "allowed_by_policy": bool(allowed_by_policy),
        "result_status": result_status,
        "reason": reason,
        "live_external_call_executed": False,
        "created_at_ms": _now_ms(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    _DISPATCH_ATTEMPT_RECORDS.append(attempt)
    return attempt


def list_dispatch_attempt_records(
    *,
    tenant_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    records = list(_DISPATCH_ATTEMPT_RECORDS)

    if tenant_id:
        records = [r for r in records if r.get("tenant_id") == tenant_id]
    if execution_id:
        records = [r for r in records if r.get("execution_id") == execution_id]

    records = sorted(records, key=lambda r: r.get("created_at_ms", 0), reverse=True)[:limit]

    return {
        "records": records,
        "count": len(records),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def record_retry_history(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    worker_job_id: str,
    provider_key: str,
    attempt_number: int,
    failure_code: str,
    retry_allowed: bool,
    next_action: str,
) -> Dict[str, Any]:
    record = {
        "retry_id": f"provider_retry_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "request_id": request_id,
        "execution_id": execution_id,
        "worker_job_id": worker_job_id,
        "provider_key": provider_key,
        "attempt_number": attempt_number,
        "failure_code": failure_code,
        "retry_allowed": bool(retry_allowed),
        "next_action": next_action,
        "created_at_ms": _now_ms(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    _RETRY_HISTORY_RECORDS.append(record)
    return record


def list_retry_history_records(
    *,
    tenant_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    records = list(_RETRY_HISTORY_RECORDS)

    if tenant_id:
        records = [r for r in records if r.get("tenant_id") == tenant_id]
    if execution_id:
        records = [r for r in records if r.get("execution_id") == execution_id]

    records = sorted(records, key=lambda r: r.get("created_at_ms", 0), reverse=True)[:limit]

    return {
        "records": records,
        "count": len(records),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def record_provider_latency_metric(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    provider_key: str,
    latency_ms: int,
    operation: str,
) -> Dict[str, Any]:
    record = {
        "latency_id": f"provider_latency_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "request_id": request_id,
        "execution_id": execution_id,
        "provider_key": provider_key,
        "latency_ms": int(latency_ms),
        "operation": operation,
        "created_at_ms": _now_ms(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    _PROVIDER_LATENCY_RECORDS.append(record)
    return record


def list_provider_latency_metrics(
    *,
    tenant_id: Optional[str] = None,
    provider_key: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    records = list(_PROVIDER_LATENCY_RECORDS)

    if tenant_id:
        records = [r for r in records if r.get("tenant_id") == tenant_id]
    if provider_key:
        records = [r for r in records if r.get("provider_key") == provider_key]

    records = sorted(records, key=lambda r: r.get("created_at_ms", 0), reverse=True)[:limit]

    if records:
        avg_latency = round(sum(r["latency_ms"] for r in records) / len(records))
        max_latency = max(r["latency_ms"] for r in records)
        min_latency = min(r["latency_ms"] for r in records)
    else:
        avg_latency = None
        max_latency = None
        min_latency = None

    return {
        "records": records,
        "count": len(records),
        "average_latency_ms": avg_latency,
        "max_latency_ms": max_latency,
        "min_latency_ms": min_latency,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def provider_execution_persistence_status() -> Dict[str, Any]:
    return {
        "persistence_runtime_ready": True,
        "storage_mode": "in_memory_safe_fallback",
        "postgres_binding_ready": False,
        "execution_record_count": len(_PROVIDER_EXECUTION_RECORDS),
        "worker_event_count": len(_WORKER_EVENT_LEDGER),
        "dispatch_attempt_count": len(_DISPATCH_ATTEMPT_RECORDS),
        "retry_history_count": len(_RETRY_HISTORY_RECORDS),
        "latency_metric_count": len(_PROVIDER_LATENCY_RECORDS),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.provider_execution_persistence_ledger import (
    append_worker_event_ledger_entry,
    create_provider_execution_record,
    get_provider_execution_record,
    list_dispatch_attempt_records,
    list_provider_execution_records,
    list_provider_latency_metrics,
    list_retry_history_records,
    list_worker_event_ledger,
    provider_execution_persistence_status,
    record_dispatch_attempt,
    record_provider_latency_metric,
    record_retry_history,
    reset_provider_execution_ledger_for_tests,
    update_provider_execution_record,
)

reset = reset_provider_execution_ledger_for_tests()
assert reset["reset"] is True
assert reset["credential_values_exposed"] is False

created = create_provider_execution_record(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_key="openai",
    task_type="image_generation",
    execution_status="created",
    worker_job_id="worker-123",
)
assert created["execution_status"] == "created"
assert created["live_external_call_executed"] is False
assert created["credential_values_exposed"] is False

updated = update_provider_execution_record(
    execution_id=created["execution_id"],
    execution_status="dispatch_blocked",
    provider_job_id="provider-job-123",
    extra={
        "safe_note": "ok",
        "api_key": "must-not-store",
        "token": "must-not-store",
    },
)
assert updated["execution_status"] == "dispatch_blocked"
assert updated["provider_job_id"] == "provider-job-123"
assert "api_key" not in updated.get("extra", {})
assert "token" not in updated.get("extra", {})

fetched = get_provider_execution_record(created["execution_id"])
assert fetched["execution_id"] == created["execution_id"]

listed = list_provider_execution_records(tenant_id="tenant-test")
assert listed["count"] == 1
assert listed["records"][0]["provider_key"] == "openai"

ledger = append_worker_event_ledger_entry(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    event_type="worker_prepared",
    status="dispatch_blocked",
    details={"safe": True, "secret": "must-not-store"},
)
assert ledger["event_type"] == "worker_prepared"
assert "secret" not in ledger["details"]
assert ledger["credential_values_exposed"] is False

ledger_list = list_worker_event_ledger(execution_id=created["execution_id"])
assert ledger_list["count"] == 1

attempt = record_dispatch_attempt(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    allowed_by_policy=False,
    result_status="blocked",
    reason="real_provider_http_dispatch_globally_disabled",
)
assert attempt["allowed_by_policy"] is False
assert attempt["live_external_call_executed"] is False

attempts = list_dispatch_attempt_records(execution_id=created["execution_id"])
assert attempts["count"] == 1

retry = record_retry_history(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    worker_job_id="worker-123",
    provider_key="openai",
    attempt_number=1,
    failure_code="provider_timeout",
    retry_allowed=True,
    next_action="queue_retry",
)
assert retry["retry_allowed"] is True
assert retry["next_action"] == "queue_retry"

retries = list_retry_history_records(execution_id=created["execution_id"])
assert retries["count"] == 1

latency1 = record_provider_latency_metric(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    provider_key="openai",
    latency_ms=1000,
    operation="request_build",
)
latency2 = record_provider_latency_metric(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id=created["execution_id"],
    provider_key="openai",
    latency_ms=2000,
    operation="dispatch_prepare",
)
assert latency1["latency_ms"] == 1000
assert latency2["latency_ms"] == 2000

latencies = list_provider_latency_metrics(tenant_id="tenant-test", provider_key="openai")
assert latencies["count"] == 2
assert latencies["average_latency_ms"] == 1500
assert latencies["max_latency_ms"] == 2000
assert latencies["min_latency_ms"] == 1000

status = provider_execution_persistence_status()
assert status["persistence_runtime_ready"] is True
assert status["storage_mode"] == "in_memory_safe_fallback"
assert status["execution_record_count"] == 1
assert status["worker_event_count"] == 1
assert status["dispatch_attempt_count"] == 1
assert status["retry_history_count"] == 1
assert status["latency_metric_count"] == 2
assert status["credential_values_exposed"] is False

print("PROVIDER_EXECUTION_PERSISTENCE_LEDGER_DIRECT_TESTS_PASSED")
print("execution_id", created["execution_id"])
print("execution_status", updated["execution_status"])
print("ledger_count", ledger_list["count"])
print("attempt_count", attempts["count"])
print("retry_count", retries["count"])
print("latency_average", latencies["average_latency_ms"])
print("storage_mode", status["storage_mode"])
'''.lstrip(), encoding="utf-8")

print("PROVIDER_EXECUTION_PERSISTENCE_LEDGER_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")
print("Safe in-memory persistence ledger foundation installed.")