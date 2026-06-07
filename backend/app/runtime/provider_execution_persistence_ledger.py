from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.runtime.durable_provider_execution_ledger import (
    create_provider_execution_record as durable_create_execution,
    get_provider_execution_record as durable_get_execution_record,
    get_provider_admin_summary,
    list_provider_dispatch_attempts,
    list_provider_execution_records as durable_list_execution_records,
    list_provider_job_events,
    list_provider_latency_metrics as durable_list_latency_metrics,
    list_provider_retry_history,
    record_provider_dispatch_attempt,
    record_provider_job_event,
    record_provider_latency,
    record_provider_retry,
    update_provider_execution_status,
    reset_dev_provider_ledger_for_tests,
)


def _safe_storage_mode(mode: str) -> str:
    return "in_memory_safe_fallback" if mode == "dev_memory" else mode


def _compat_execution_record(record: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(record or {})
    safe["provider_key"] = safe.get("provider_key") or safe.get("provider")
    safe["task_type"] = safe.get("task_type") or safe.get("capability") or safe.get("action_type")
    safe["execution_status"] = safe.get("execution_status") or safe.get("status")
    safe.setdefault("worker_job_id", "")
    safe.setdefault("provider_job_id", "")
    safe.setdefault("live_external_call_executed", False)
    safe.setdefault("customer_safe", True)
    safe["credential_values_exposed"] = False
    return safe


def _compat_event(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(event.get("payload") or {})
    details = dict(payload.get("details") or {})
    return {
        "ledger_id": event.get("event_id"),
        "event_id": event.get("event_id"),
        "tenant_id": payload.get("tenant_id"),
        "request_id": payload.get("request_id"),
        "execution_id": event.get("execution_id"),
        "worker_job_id": event.get("provider_job_id") or event.get("job_id"),
        "provider_key": payload.get("provider_key"),
        "event_type": event.get("event_type"),
        "status": payload.get("status"),
        "details": details,
        "payload": payload,
        "created_at": event.get("created_at"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def _compat_attempt(attempt: Dict[str, Any], *, tenant_id: str = "", request_id: str = "") -> Dict[str, Any]:
    safe = dict(attempt or {})
    safe["attempt_id"] = safe.get("attempt_id") or safe.get("dispatch_attempt_id")
    safe["worker_job_id"] = safe.get("worker_job_id") or safe.get("provider_job_id")
    safe["provider_key"] = safe.get("provider_key") or safe.get("provider")
    safe["result_status"] = safe.get("result_status") or safe.get("status")
    safe.setdefault("tenant_id", tenant_id)
    safe.setdefault("request_id", request_id)
    safe.setdefault("allowed_by_policy", None)
    safe.setdefault("live_external_call_executed", False)
    safe["credential_values_exposed"] = False
    safe["customer_safe"] = True
    return safe


def _compat_retry(retry: Dict[str, Any], *, tenant_id: str = "", request_id: str = "") -> Dict[str, Any]:
    safe = dict(retry or {})
    safe["worker_job_id"] = safe.get("worker_job_id") or safe.get("provider_job_id")
    safe["failure_code"] = safe.get("failure_code") or safe.get("retry_reason")
    safe.setdefault("tenant_id", tenant_id)
    safe.setdefault("request_id", request_id)
    safe.setdefault("retry_allowed", None)
    safe.setdefault("next_action", "")
    safe["credential_values_exposed"] = False
    safe["customer_safe"] = True
    return safe


def _compat_latency(metric: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(metric or {})
    safe["latency_id"] = safe.get("latency_id") or safe.get("metric_id")
    safe["provider_key"] = safe.get("provider_key") or safe.get("provider")
    safe["operation"] = safe.get("operation") or safe.get("capability") or safe.get("status")
    safe["credential_values_exposed"] = False
    safe["customer_safe"] = True
    return safe


def reset_provider_execution_ledger_for_tests() -> Dict[str, Any]:
    return reset_dev_provider_ledger_for_tests()


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
    result = durable_create_execution(
        tenant_id=tenant_id,
        provider=provider_key,
        action_type=task_type,
        capability=task_type,
        status=execution_status,
        request_payload={
            "request_id": request_id,
            "worker_job_id": worker_job_id,
            "provider_job_id": provider_job_id,
        },
        idempotency_key=f"{tenant_id}:{provider_key}:{request_id}:{task_type}",
        worker_job_id=worker_job_id or "",
        provider_job_id=provider_job_id or "",
    )
    record = _compat_execution_record(result.get("record") or {})
    record["task_type"] = task_type
    record["execution_status"] = record.get("status")
    record["worker_job_id"] = worker_job_id
    record["provider_job_id"] = provider_job_id
    record["request_id"] = request_id
    return record


def update_provider_execution_record(
    *,
    execution_id: str,
    execution_status: Optional[str] = None,
    worker_job_id: Optional[str] = None,
    provider_job_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    result = update_provider_execution_status(
        execution_id,
        execution_status or "updated",
        worker_job_id=worker_job_id,
        provider_job_id=provider_job_id,
        extra=extra,
    )
    record = dict(result.get("record") or {})
    if not record:
        return {
            "status": "not_found",
            "execution_id": execution_id,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    record["execution_status"] = record.get("status", result.get("status"))
    return _compat_execution_record(record)


def get_provider_execution_record(execution_id: str) -> Dict[str, Any]:
    result = durable_get_execution_record(execution_id)
    if result.get("success"):
        return _compat_execution_record(result.get("record") or {})
    return {
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
    listed = durable_list_execution_records(tenant_id=tenant_id or "", provider=provider_key or "", limit=limit)
    records = [_compat_execution_record(record) for record in listed.get("records", [])]
    return {"records": records, "count": len(records), "credential_values_exposed": False, "customer_safe": True}


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
    result = record_provider_job_event(
        provider_job_id=worker_job_id,
        execution_id=execution_id,
        event_type=event_type,
        payload={"tenant_id": tenant_id, "request_id": request_id, "provider_key": provider_key, "status": status, "details": details or {}},
    )
    return _compat_event(result.get("event") or {})


def list_worker_event_ledger(*, tenant_id: Optional[str] = None, execution_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    result = list_provider_job_events(tenant_id=tenant_id or "", execution_id=execution_id or "", limit=limit)
    entries = [_compat_event(event) for event in result.get("events", [])]
    return {"entries": entries, "count": len(entries), "credential_values_exposed": False, "customer_safe": True}


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
    result = record_provider_dispatch_attempt(
        execution_id=execution_id,
        provider_job_id=worker_job_id,
        provider=provider_key,
        status=result_status,
        idempotency_key=f"{tenant_id}:{provider_key}:{request_id}:{attempt_number}",
        error=reason,
        reason=reason,
        attempt_number=attempt_number,
        allowed_by_policy=allowed_by_policy,
    )
    return _compat_attempt(result.get("attempt") or {}, tenant_id=tenant_id, request_id=request_id)


def list_dispatch_attempt_records(*, tenant_id: Optional[str] = None, execution_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    result = list_provider_dispatch_attempts(tenant_id=tenant_id or "", execution_id=execution_id or "", limit=limit)
    records = [_compat_attempt(attempt, tenant_id=tenant_id or "") for attempt in result.get("records", [])]
    return {"records": records, "count": len(records), "credential_values_exposed": False, "customer_safe": True}


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
    result = record_provider_retry(
        provider_job_id=worker_job_id,
        execution_id=execution_id,
        retry_reason=failure_code,
        attempt_number=attempt_number,
        retry_allowed=retry_allowed,
        next_action=next_action,
    )
    return _compat_retry(result.get("retry") or {}, tenant_id=tenant_id, request_id=request_id)


def list_retry_history_records(*, tenant_id: Optional[str] = None, execution_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    result = list_provider_retry_history(tenant_id=tenant_id or "", execution_id=execution_id or "", limit=limit)
    records = [_compat_retry(retry, tenant_id=tenant_id or "") for retry in result.get("records", [])]
    return {"records": records, "count": len(records), "credential_values_exposed": False, "customer_safe": True}


def record_provider_latency_metric(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    provider_key: str,
    latency_ms: int,
    operation: str,
) -> Dict[str, Any]:
    result = record_provider_latency(
        provider=provider_key,
        capability=operation,
        latency_ms=latency_ms,
        status=operation,
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
    )
    return _compat_latency(result.get("metric") or {})


def list_provider_latency_metrics(*, tenant_id: Optional[str] = None, provider_key: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    result = durable_list_latency_metrics(tenant_id=tenant_id or "", provider=provider_key or "", limit=limit)
    records = [_compat_latency(metric) for metric in result.get("records", [])]
    return {
        "records": records,
        "count": len(records),
        "average_latency_ms": result.get("average_latency_ms"),
        "max_latency_ms": result.get("max_latency_ms"),
        "min_latency_ms": result.get("min_latency_ms"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def provider_execution_persistence_status() -> Dict[str, Any]:
    summary = get_provider_admin_summary()
    events = list_worker_event_ledger(limit=500)
    return {
        "persistence_runtime_ready": bool(summary.get("success")),
        "storage_mode": _safe_storage_mode(str(summary.get("storage_mode") or "")),
        "postgres_binding_ready": summary.get("durable", False),
        "canonical_durable_provider_ledger": True,
        "execution_record_count": summary.get("summary", {}).get("execution_record_count", 0),
        "worker_event_count": events.get("count", 0),
        "dispatch_attempt_count": summary.get("summary", {}).get("dispatch_attempt_count", 0),
        "retry_history_count": summary.get("summary", {}).get("retry_history_count", 0),
        "latency_metric_count": summary.get("summary", {}).get("latency_metric_count", 0),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
