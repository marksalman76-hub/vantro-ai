from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


DURABLE_MANUAL_REVIEW_RECOVERY_PROFILE = "durable_manual_review_recovery_runtime_v1"

OPEN_REVIEW_STATUSES = {
    "pending",
    "pending_owner_review",
    "manual_review_required",
    "owner_approval_required",
    "queued_for_owner_approval",
    "escalated",
}

DECISION_STATUS_MAP = {
    "retry": "retry_requested",
    "mark_resolved": "resolved",
    "resolved": "resolved",
    "retry_requested": "retry_requested",
    "rejected": "rejected",
    "reject": "rejected",
    "escalated": "escalated",
    "escalate": "escalated",
    "owner_approved": "owner_approved",
    "owner_rejected": "owner_rejected",
}

ALLOWED_DECISIONS = set(DECISION_STATUS_MAP)

_DEV_REVIEW_ITEMS: Dict[str, Dict[str, Any]] = {}
_DEV_DECISIONS: Dict[str, Dict[str, Any]] = {}
_DEV_DEAD_LETTERS: Dict[str, Dict[str, Any]] = {}
_DEV_RECOVERY_ACTIONS: Dict[str, Dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


def _database_url() -> str:
    return os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or ""


def _is_production() -> bool:
    values = [
        os.getenv("ENVIRONMENT"),
        os.getenv("APP_ENV"),
        os.getenv("FASTAPI_ENV"),
        os.getenv("NODE_ENV"),
        os.getenv("RENDER"),
        os.getenv("VERCEL_ENV"),
        os.getenv("PRODUCTION"),
    ]
    return any(str(value or "").strip().lower() in {"1", "true", "prod", "production"} for value in values)


def _psycopg():
    try:
        import psycopg  # type: ignore

        return psycopg
    except Exception:
        return None


def _connect():
    psycopg = _psycopg()
    if psycopg is None:
        raise RuntimeError("psycopg_unavailable")
    if not _database_url():
        raise RuntimeError("DATABASE_URL_missing")
    timeout = max(1, min(int(os.getenv("MANUAL_REVIEW_CONNECT_TIMEOUT_SECONDS") or 2), 10))
    return psycopg.connect(_database_url(), connect_timeout=timeout)


def _safe_response(**payload: Any) -> Dict[str, Any]:
    result = dict(payload)
    result.setdefault("manual_review_recovery_profile", DURABLE_MANUAL_REVIEW_RECOVERY_PROFILE)
    result.setdefault("credential_values_exposed", False)
    result.setdefault("customer_safe", True)
    return result


def _unavailable(reason: str) -> Dict[str, Any]:
    return _safe_response(
        success=False,
        status="manual_review_recovery_store_unavailable",
        manual_review_recovery_ready=False,
        durable=False,
        storage_mode="postgres_unavailable",
        production_fail_closed=_is_production(),
        dev_only=False,
        not_production_durable=False,
        reason=reason,
    )


def _using_dev(readiness: Dict[str, Any]) -> bool:
    return readiness.get("storage_mode") == "dev_memory"


def _json(data: Optional[Dict[str, Any]]) -> str:
    return json.dumps(_scrub_sensitive(deepcopy(data or {})), ensure_ascii=False, sort_keys=True)


def _parse_json(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return _scrub_sensitive(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return _scrub_sensitive(parsed) if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _dt(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


def _limit(value: int, default: int = 50, maximum: int = 500) -> int:
    try:
        parsed = int(value or default)
    except Exception:
        parsed = default
    return max(1, min(parsed, maximum))


def _scrub_sensitive(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for key, value in (data or {}).items():
        key_lower = str(key).lower()
        if any(marker in key_lower for marker in ("secret", "token", "api_key", "password", "credential")):
            continue
        if isinstance(value, dict):
            safe[key] = _scrub_sensitive(value)
            continue
        if isinstance(value, list):
            safe[key] = [_scrub_sensitive(item) if isinstance(item, dict) else item for item in value]
            continue
        safe[key] = value
    return safe


def _coerce_id(value: Any) -> str:
    return str(value or "").strip()


def _review_columns() -> List[str]:
    return [
        "review_id",
        "tenant_id",
        "project_id",
        "source_type",
        "source_id",
        "provider_job_id",
        "provider_execution_id",
        "orchestration_id",
        "orchestration_step_id",
        "queue_job_id",
        "packet_id",
        "routing_id",
        "execution_id",
        "review_type",
        "status",
        "priority",
        "reason",
        "summary",
        "payload_json",
        "created_at",
        "updated_at",
        "resolved_at",
        "credential_values_exposed",
    ]


def _decision_columns() -> List[str]:
    return ["decision_id", "review_id", "tenant_id", "decision", "decided_by", "actor_role", "reason", "payload_json", "created_at"]


def _dead_letter_columns() -> List[str]:
    return [
        "dead_letter_id",
        "tenant_id",
        "project_id",
        "source_type",
        "source_id",
        "queue_job_id",
        "provider_job_id",
        "orchestration_id",
        "orchestration_step_id",
        "reason",
        "error_summary",
        "payload_json",
        "status",
        "created_at",
        "updated_at",
        "resolved_at",
    ]


def _recovery_action_columns() -> List[str]:
    return [
        "recovery_action_id",
        "tenant_id",
        "project_id",
        "review_id",
        "dead_letter_id",
        "orchestration_id",
        "provider_job_id",
        "queue_job_id",
        "action_type",
        "status",
        "payload_json",
        "created_at",
        "updated_at",
        "completed_at",
        "failed_at",
    ]


def _row_to_record(row: Any, columns: List[str]) -> Dict[str, Any]:
    data = dict(zip(columns, row))
    if "payload_json" in data:
        data["payload"] = _parse_json(data.pop("payload_json", None))
    for key, value in list(data.items()):
        data[key] = _dt(value)
    data["credential_values_exposed"] = False
    data["customer_safe"] = True
    return data


def ensure_manual_review_recovery_tables() -> Dict[str, Any]:
    if not _database_url():
        if _is_production():
            return _unavailable("DATABASE_URL_missing")
        return _safe_response(
            success=True,
            status="dev_only_manual_review_recovery_ready",
            manual_review_recovery_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
        )

    if _psycopg() is None:
        if _is_production():
            return _unavailable("psycopg_unavailable")
        return _safe_response(
            success=True,
            status="dev_only_manual_review_recovery_ready",
            manual_review_recovery_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
            postgres_configured_but_driver_unavailable=True,
        )

    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS manual_review_items (
                        review_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        source_type TEXT NOT NULL DEFAULT 'unknown',
                        source_id TEXT,
                        provider_job_id TEXT,
                        provider_execution_id TEXT,
                        orchestration_id TEXT,
                        orchestration_step_id TEXT,
                        queue_job_id TEXT,
                        packet_id TEXT,
                        routing_id TEXT,
                        execution_id TEXT,
                        review_type TEXT NOT NULL DEFAULT 'manual_review',
                        status TEXT NOT NULL DEFAULT 'pending',
                        priority TEXT NOT NULL DEFAULT 'medium',
                        reason TEXT,
                        summary TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        resolved_at TIMESTAMPTZ,
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_review_items_tenant_status ON manual_review_items (tenant_id, status, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_review_items_source ON manual_review_items (tenant_id, source_type, source_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_review_items_provider_job ON manual_review_items (provider_job_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_review_items_orchestration ON manual_review_items (orchestration_id, orchestration_step_id)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS manual_review_decisions (
                        decision_id TEXT PRIMARY KEY,
                        review_id TEXT NOT NULL,
                        tenant_id TEXT NOT NULL,
                        decision TEXT NOT NULL,
                        decided_by TEXT,
                        actor_role TEXT NOT NULL,
                        reason TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_review_decisions_review ON manual_review_decisions (review_id, created_at DESC)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS dead_letter_records (
                        dead_letter_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        source_type TEXT NOT NULL DEFAULT 'unknown',
                        source_id TEXT,
                        queue_job_id TEXT,
                        provider_job_id TEXT,
                        orchestration_id TEXT,
                        orchestration_step_id TEXT,
                        reason TEXT,
                        error_summary TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        status TEXT NOT NULL DEFAULT 'dead_lettered',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        resolved_at TIMESTAMPTZ,
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_dead_letter_records_tenant_status ON dead_letter_records (tenant_id, status, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_dead_letter_records_source ON dead_letter_records (tenant_id, source_type, source_id)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS recovery_actions (
                        recovery_action_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        review_id TEXT,
                        dead_letter_id TEXT,
                        orchestration_id TEXT,
                        provider_job_id TEXT,
                        queue_job_id TEXT,
                        action_type TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'requested',
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        completed_at TIMESTAMPTZ,
                        failed_at TIMESTAMPTZ,
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_recovery_actions_review ON recovery_actions (review_id, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_recovery_actions_tenant_status ON recovery_actions (tenant_id, status, created_at DESC)")
            conn.commit()
        return _safe_response(
            success=True,
            status="manual_review_recovery_ready",
            manual_review_recovery_ready=True,
            durable=True,
            storage_mode="postgres",
            persistence_mode="postgres",
            dev_only=False,
            not_production_durable=False,
        )
    except Exception as exc:
        if _is_production():
            return _unavailable(str(exc))
        return _safe_response(
            success=True,
            status="dev_only_manual_review_recovery_ready",
            manual_review_recovery_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
            postgres_error=str(exc),
        )


def _source_identity(record: Dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(record.get("tenant_id") or "unknown"),
        str(record.get("source_type") or "unknown"),
        str(record.get("source_id") or ""),
        str(record.get("review_type") or "manual_review"),
    )


def _find_dev_review_by_source(tenant_id: str, source_type: str, source_id: str, review_type: str) -> Optional[Dict[str, Any]]:
    if not source_id:
        return None
    for item in _DEV_REVIEW_ITEMS.values():
        if _source_identity(item) == (tenant_id, source_type, source_id, review_type) and str(item.get("status")) in OPEN_REVIEW_STATUSES:
            return deepcopy(item)
    return None


def create_manual_review_item(
    *,
    tenant_id: str,
    project_id: str = "default_project",
    source_type: str = "manual_review",
    source_id: str = "",
    provider_job_id: str = "",
    provider_execution_id: str = "",
    orchestration_id: str = "",
    orchestration_step_id: str = "",
    queue_job_id: str = "",
    packet_id: str = "",
    routing_id: str = "",
    execution_id: str = "",
    review_type: str = "manual_review",
    status: str = "pending_owner_review",
    priority: str = "medium",
    reason: str = "",
    summary: str = "",
    payload: Optional[Dict[str, Any]] = None,
    review_id: str = "",
) -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness

    item = {
        "review_id": _coerce_id(review_id) or f"review_{uuid.uuid4().hex[:16]}",
        "tenant_id": _coerce_id(tenant_id) or "unknown",
        "project_id": _coerce_id(project_id) or "default_project",
        "source_type": _coerce_id(source_type) or "manual_review",
        "source_id": _coerce_id(source_id),
        "provider_job_id": _coerce_id(provider_job_id),
        "provider_execution_id": _coerce_id(provider_execution_id),
        "orchestration_id": _coerce_id(orchestration_id),
        "orchestration_step_id": _coerce_id(orchestration_step_id),
        "queue_job_id": _coerce_id(queue_job_id),
        "packet_id": _coerce_id(packet_id),
        "routing_id": _coerce_id(routing_id),
        "execution_id": _coerce_id(execution_id),
        "review_type": _coerce_id(review_type) or "manual_review",
        "status": _coerce_id(status) or "pending_owner_review",
        "priority": _coerce_id(priority) or "medium",
        "reason": str(reason or ""),
        "summary": str(summary or "")[:2000],
        "payload": _scrub_sensitive(payload or {}),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "resolved_at": None,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    existing_source_id = item["source_id"] or item["provider_job_id"] or item["queue_job_id"] or item["orchestration_step_id"] or item["packet_id"] or item["execution_id"]
    item["source_id"] = item["source_id"] or existing_source_id

    if _using_dev(readiness):
        existing = _find_dev_review_by_source(item["tenant_id"], item["source_type"], item["source_id"], item["review_type"])
        if existing:
            return _safe_response(success=True, status=existing.get("status"), item=existing, review_item=existing, review_id=existing["review_id"], idempotent_replay=True, storage_mode="dev_memory", dev_only=True)
        _DEV_REVIEW_ITEMS[item["review_id"]] = deepcopy(item)
        return _safe_response(success=True, status=item["status"], item=deepcopy(item), review_item=deepcopy(item), review_id=item["review_id"], idempotent_replay=False, storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            if item["source_id"]:
                cur.execute(
                    """
                    SELECT review_id, tenant_id, project_id, source_type, source_id,
                           provider_job_id, provider_execution_id, orchestration_id,
                           orchestration_step_id, queue_job_id, packet_id, routing_id,
                           execution_id, review_type, status, priority, reason, summary,
                           payload_json, created_at, updated_at, resolved_at,
                           credential_values_exposed
                    FROM manual_review_items
                    WHERE tenant_id = %s
                      AND source_type = %s
                      AND source_id = %s
                      AND review_type = %s
                      AND status IN ('pending', 'pending_owner_review', 'manual_review_required',
                                     'owner_approval_required', 'queued_for_owner_approval', 'escalated')
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (item["tenant_id"], item["source_type"], item["source_id"], item["review_type"]),
                )
                row = cur.fetchone()
                if row:
                    existing = _row_to_record(row, _review_columns())
                    conn.commit()
                    return _safe_response(success=True, status=existing.get("status"), item=existing, review_item=existing, review_id=existing["review_id"], idempotent_replay=True, storage_mode="postgres", durable=True)
            cur.execute(
                """
                INSERT INTO manual_review_items
                (review_id, tenant_id, project_id, source_type, source_id,
                 provider_job_id, provider_execution_id, orchestration_id,
                 orchestration_step_id, queue_job_id, packet_id, routing_id,
                 execution_id, review_type, status, priority, reason, summary,
                 payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING review_id, tenant_id, project_id, source_type, source_id,
                          provider_job_id, provider_execution_id, orchestration_id,
                          orchestration_step_id, queue_job_id, packet_id, routing_id,
                          execution_id, review_type, status, priority, reason, summary,
                          payload_json, created_at, updated_at, resolved_at,
                          credential_values_exposed
                """,
                (
                    item["review_id"],
                    item["tenant_id"],
                    item["project_id"],
                    item["source_type"],
                    item["source_id"] or None,
                    item["provider_job_id"] or None,
                    item["provider_execution_id"] or None,
                    item["orchestration_id"] or None,
                    item["orchestration_step_id"] or None,
                    item["queue_job_id"] or None,
                    item["packet_id"] or None,
                    item["routing_id"] or None,
                    item["execution_id"] or None,
                    item["review_type"],
                    item["status"],
                    item["priority"],
                    item["reason"] or None,
                    item["summary"] or None,
                    _json(item["payload"]),
                ),
            )
            row = cur.fetchone()
        conn.commit()
    record = _row_to_record(row, _review_columns())
    return _safe_response(success=True, status=record["status"], item=record, review_item=record, review_id=record["review_id"], idempotent_replay=False, storage_mode="postgres", durable=True)


def get_manual_review_item(review_id: str) -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness
    clean_id = _coerce_id(review_id)
    if _using_dev(readiness):
        item = _DEV_REVIEW_ITEMS.get(clean_id)
        if not item:
            return _safe_response(success=False, status="review_not_found", review_id=clean_id, storage_mode="dev_memory", dev_only=True)
        return _safe_response(success=True, status="found", item=deepcopy(item), review_item=deepcopy(item), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT review_id, tenant_id, project_id, source_type, source_id,
                       provider_job_id, provider_execution_id, orchestration_id,
                       orchestration_step_id, queue_job_id, packet_id, routing_id,
                       execution_id, review_type, status, priority, reason, summary,
                       payload_json, created_at, updated_at, resolved_at,
                       credential_values_exposed
                FROM manual_review_items
                WHERE review_id = %s
                """,
                (clean_id,),
            )
            row = cur.fetchone()
    if not row:
        return _safe_response(success=False, status="review_not_found", review_id=clean_id, storage_mode="postgres", durable=True)
    item = _row_to_record(row, _review_columns())
    return _safe_response(success=True, status="found", item=item, review_item=item, storage_mode="postgres", durable=True)


def list_manual_review_items(*, tenant_id: str = "", status: str = "", review_type: str = "", limit: int = 50) -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        items = list(_DEV_REVIEW_ITEMS.values())
        if tenant_id:
            items = [item for item in items if item.get("tenant_id") == tenant_id]
        if status:
            items = [item for item in items if item.get("status") == status]
        if review_type:
            items = [item for item in items if item.get("review_type") == review_type]
        items = sorted(items, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", count=len(items), items=deepcopy(items), manual_review_items=deepcopy(items), storage_mode="dev_memory", dev_only=True)
    clauses: List[str] = []
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if status:
        clauses.append("status = %s")
        params.append(status)
    if review_type:
        clauses.append("review_type = %s")
        params.append(review_type)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT review_id, tenant_id, project_id, source_type, source_id,
                       provider_job_id, provider_execution_id, orchestration_id,
                       orchestration_step_id, queue_job_id, packet_id, routing_id,
                       execution_id, review_type, status, priority, reason, summary,
                       payload_json, created_at, updated_at, resolved_at,
                       credential_values_exposed
                FROM manual_review_items
                {where}
                ORDER BY created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    items = [_row_to_record(row, _review_columns()) for row in rows]
    return _safe_response(success=True, status="listed", count=len(items), items=items, manual_review_items=items, storage_mode="postgres", durable=True)


def _find_existing_decision(review_id: str, decision: str) -> Optional[Dict[str, Any]]:
    for existing in _DEV_DECISIONS.values():
        if existing.get("review_id") == review_id and existing.get("decision") == decision:
            return deepcopy(existing)
    return None


def _apply_linked_state_transition(item: Dict[str, Any], final_status: str, reason: str) -> Dict[str, Any]:
    updates: List[Dict[str, Any]] = []
    provider_job_id = _coerce_id(item.get("provider_job_id"))
    queue_job_id = _coerce_id(item.get("queue_job_id"))
    orchestration_step_id = _coerce_id(item.get("orchestration_step_id"))
    orchestration_id = _coerce_id(item.get("orchestration_id"))
    tenant_id = _coerce_id(item.get("tenant_id")) or "unknown"

    if provider_job_id and final_status in {"retry_requested", "rejected", "owner_rejected"}:
        try:
            from backend.app.runtime.provider_job_persistence_runtime import update_provider_job_status

            provider_status = "queued" if final_status == "retry_requested" else "cancelled"
            updates.append({"target": "provider_job", "result": update_provider_job_status(provider_job_id, provider_status, error=reason or final_status)})
        except Exception as exc:
            updates.append({"target": "provider_job", "success": False, "error": str(exc)})

    if queue_job_id and final_status == "retry_requested":
        try:
            from backend.app.runtime.durable_execution_queue_runtime import retry_execution_job

            updates.append({"target": "queue_job", "result": retry_execution_job(queue_job_id, error=reason or final_status, retry_delay_seconds=0)})
        except Exception as exc:
            updates.append({"target": "queue_job", "success": False, "error": str(exc)})

    if orchestration_step_id and final_status in {"resolved", "retry_requested", "rejected", "escalated", "owner_approved", "owner_rejected"}:
        try:
            from backend.app.runtime.durable_orchestration_state_runtime import update_orchestration_step_status

            step_status = {
                "resolved": "review_resolved",
                "retry_requested": "retry_requested",
                "rejected": "review_rejected",
                "escalated": "escalated",
                "owner_approved": "owner_approved",
                "owner_rejected": "owner_rejected",
            }[final_status]
            updates.append(
                {
                    "target": "orchestration_step",
                    "result": update_orchestration_step_status(
                        step_id=orchestration_step_id,
                        orchestration_id=orchestration_id,
                        tenant_id=tenant_id,
                        status=step_status,
                        last_error=reason,
                    ),
                }
            )
        except Exception as exc:
            updates.append({"target": "orchestration_step", "success": False, "error": str(exc)})

    return _safe_response(success=True, status="linked_state_transition_applied", updates=updates)


def record_manual_review_decision(
    *,
    review_id: str,
    decision: str,
    decided_by: str = "",
    actor_role: str,
    reason: str = "",
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    clean_decision = _coerce_id(decision).lower()
    if clean_decision not in ALLOWED_DECISIONS:
        return _safe_response(success=False, status="blocked", reason="unsupported_or_high_risk_decision", allowed_decisions=sorted(ALLOWED_DECISIONS), no_autonomous_spend_or_scaling=True)
    if _coerce_id(actor_role) not in {"owner", "admin", "owner_admin"}:
        return _safe_response(success=False, status="blocked", reason="manual_review_decision_requires_owner_or_admin")

    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness

    final_status = DECISION_STATUS_MAP[clean_decision]
    item_result = get_manual_review_item(review_id)
    if not item_result.get("success"):
        return item_result
    item = item_result["item"]

    if _using_dev(readiness):
        existing = _find_existing_decision(item["review_id"], final_status)
        if existing:
            return _safe_response(success=True, status="decision_recorded", decision=existing, idempotent_replay=True, item=deepcopy(_DEV_REVIEW_ITEMS[item["review_id"]]), storage_mode="dev_memory", dev_only=True)
        decision_record = {
            "decision_id": f"decision_{uuid.uuid4().hex[:16]}",
            "review_id": item["review_id"],
            "tenant_id": item["tenant_id"],
            "decision": final_status,
            "decided_by": _coerce_id(decided_by) or _coerce_id(actor_role),
            "actor_role": _coerce_id(actor_role),
            "reason": str(reason or ""),
            "payload": _scrub_sensitive(payload or {}),
            "created_at": _now_iso(),
            "credential_values_exposed": False,
            "customer_safe": True,
        }
        _DEV_DECISIONS[decision_record["decision_id"]] = deepcopy(decision_record)
        item["status"] = final_status
        item["updated_at"] = _now_iso()
        if final_status in {"resolved", "rejected", "owner_approved", "owner_rejected"}:
            item["resolved_at"] = item["updated_at"]
        _DEV_REVIEW_ITEMS[item["review_id"]] = deepcopy(item)
        recovery = create_recovery_action(
            tenant_id=item["tenant_id"],
            project_id=item.get("project_id") or "default_project",
            review_id=item["review_id"],
            orchestration_id=item.get("orchestration_id") or "",
            provider_job_id=item.get("provider_job_id") or "",
            queue_job_id=item.get("queue_job_id") or "",
            action_type=final_status,
            status="requested",
            payload={"decision_id": decision_record["decision_id"], "reason": reason},
        )
        linked = _apply_linked_state_transition(item, final_status, reason)
        return _safe_response(success=True, status="decision_recorded", decision=deepcopy(decision_record), item=deepcopy(item), recovery_action=recovery.get("recovery_action"), linked_state_updates=linked.get("updates", []), storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT decision_id, review_id, tenant_id, decision, decided_by,
                       actor_role, reason, payload_json, created_at
                FROM manual_review_decisions
                WHERE review_id = %s AND decision = %s
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (item["review_id"], final_status),
            )
            existing_row = cur.fetchone()
            if existing_row:
                existing = _row_to_record(existing_row, _decision_columns())
                conn.commit()
                return _safe_response(success=True, status="decision_recorded", decision=existing, idempotent_replay=True, item=item, storage_mode="postgres", durable=True)

            decision_id = f"decision_{uuid.uuid4().hex[:16]}"
            cur.execute(
                """
                INSERT INTO manual_review_decisions
                (decision_id, review_id, tenant_id, decision, decided_by,
                 actor_role, reason, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING decision_id, review_id, tenant_id, decision, decided_by,
                          actor_role, reason, payload_json, created_at
                """,
                (decision_id, item["review_id"], item["tenant_id"], final_status, decided_by or actor_role, actor_role, reason or None, _json(payload)),
            )
            decision_row = cur.fetchone()
            resolved_sql = "NOW()" if final_status in {"resolved", "rejected", "owner_approved", "owner_rejected"} else "resolved_at"
            cur.execute(
                f"""
                UPDATE manual_review_items
                SET status = %s, updated_at = NOW(), resolved_at = {resolved_sql}
                WHERE review_id = %s
                RETURNING review_id, tenant_id, project_id, source_type, source_id,
                          provider_job_id, provider_execution_id, orchestration_id,
                          orchestration_step_id, queue_job_id, packet_id, routing_id,
                          execution_id, review_type, status, priority, reason, summary,
                          payload_json, created_at, updated_at, resolved_at,
                          credential_values_exposed
                """,
                (final_status, item["review_id"]),
            )
            item_row = cur.fetchone()
        conn.commit()
    decision_record = _row_to_record(decision_row, _decision_columns())
    updated_item = _row_to_record(item_row, _review_columns())
    recovery = create_recovery_action(
        tenant_id=updated_item["tenant_id"],
        project_id=updated_item.get("project_id") or "default_project",
        review_id=updated_item["review_id"],
        orchestration_id=updated_item.get("orchestration_id") or "",
        provider_job_id=updated_item.get("provider_job_id") or "",
        queue_job_id=updated_item.get("queue_job_id") or "",
        action_type=final_status,
        status="requested",
        payload={"decision_id": decision_record["decision_id"], "reason": reason},
    )
    linked = _apply_linked_state_transition(updated_item, final_status, reason)
    return _safe_response(success=True, status="decision_recorded", decision=decision_record, item=updated_item, recovery_action=recovery.get("recovery_action"), linked_state_updates=linked.get("updates", []), storage_mode="postgres", durable=True)


def resolve_manual_review_item(review_id: str, *, reason: str = "manual_review_resolved", actor_role: str = "admin") -> Dict[str, Any]:
    return record_manual_review_decision(review_id=review_id, decision="resolved", actor_role=actor_role, reason=reason)


def create_dead_letter_record(
    *,
    tenant_id: str,
    project_id: str = "default_project",
    source_type: str = "dead_letter",
    source_id: str = "",
    queue_job_id: str = "",
    provider_job_id: str = "",
    orchestration_id: str = "",
    orchestration_step_id: str = "",
    reason: str = "",
    error_summary: str = "",
    payload: Optional[Dict[str, Any]] = None,
    status: str = "dead_lettered",
    dead_letter_id: str = "",
    create_review: bool = True,
) -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness
    record = {
        "dead_letter_id": _coerce_id(dead_letter_id) or f"dlq_{uuid.uuid4().hex[:16]}",
        "tenant_id": _coerce_id(tenant_id) or "unknown",
        "project_id": _coerce_id(project_id) or "default_project",
        "source_type": _coerce_id(source_type) or "dead_letter",
        "source_id": _coerce_id(source_id) or _coerce_id(queue_job_id) or _coerce_id(provider_job_id) or _coerce_id(orchestration_step_id),
        "queue_job_id": _coerce_id(queue_job_id),
        "provider_job_id": _coerce_id(provider_job_id),
        "orchestration_id": _coerce_id(orchestration_id),
        "orchestration_step_id": _coerce_id(orchestration_step_id),
        "reason": str(reason or "dead_lettered"),
        "error_summary": str(error_summary or reason or "dead_lettered")[:2000],
        "payload": _scrub_sensitive(payload or {}),
        "status": _coerce_id(status) or "dead_lettered",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "resolved_at": None,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    if _using_dev(readiness):
        for existing in _DEV_DEAD_LETTERS.values():
            if record["source_id"] and existing.get("tenant_id") == record["tenant_id"] and existing.get("source_type") == record["source_type"] and existing.get("source_id") == record["source_id"] and existing.get("status") != "resolved":
                item = deepcopy(existing)
                return _safe_response(success=True, status=item["status"], dead_letter=deepcopy(item), dead_letter_id=item["dead_letter_id"], idempotent_replay=True, storage_mode="dev_memory", dev_only=True)
        _DEV_DEAD_LETTERS[record["dead_letter_id"]] = deepcopy(record)
        review = None
        if create_review:
            review = create_manual_review_item(
                tenant_id=record["tenant_id"],
                project_id=record["project_id"],
                source_type="dead_letter",
                source_id=record["dead_letter_id"],
                provider_job_id=record["provider_job_id"],
                orchestration_id=record["orchestration_id"],
                orchestration_step_id=record["orchestration_step_id"],
                queue_job_id=record["queue_job_id"],
                review_type="dead_letter_review",
                status="pending_owner_review",
                priority="high",
                reason=record["reason"],
                summary=record["error_summary"],
                payload={"dead_letter_id": record["dead_letter_id"], **record["payload"]},
            )
        return _safe_response(success=True, status=record["status"], dead_letter=deepcopy(record), dead_letter_id=record["dead_letter_id"], review_item=(review or {}).get("item"), storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            if record["source_id"]:
                cur.execute(
                    """
                    SELECT dead_letter_id, tenant_id, project_id, source_type, source_id,
                           queue_job_id, provider_job_id, orchestration_id,
                           orchestration_step_id, reason, error_summary, payload_json,
                           status, created_at, updated_at, resolved_at
                    FROM dead_letter_records
                    WHERE tenant_id = %s AND source_type = %s AND source_id = %s AND status <> 'resolved'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (record["tenant_id"], record["source_type"], record["source_id"]),
                )
                row = cur.fetchone()
                if row:
                    existing = _row_to_record(row, _dead_letter_columns())
                    conn.commit()
                    return _safe_response(success=True, status=existing["status"], dead_letter=existing, dead_letter_id=existing["dead_letter_id"], idempotent_replay=True, storage_mode="postgres", durable=True)
            cur.execute(
                """
                INSERT INTO dead_letter_records
                (dead_letter_id, tenant_id, project_id, source_type, source_id,
                 queue_job_id, provider_job_id, orchestration_id, orchestration_step_id,
                 reason, error_summary, payload_json, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                RETURNING dead_letter_id, tenant_id, project_id, source_type, source_id,
                          queue_job_id, provider_job_id, orchestration_id,
                          orchestration_step_id, reason, error_summary, payload_json,
                          status, created_at, updated_at, resolved_at
                """,
                (
                    record["dead_letter_id"],
                    record["tenant_id"],
                    record["project_id"],
                    record["source_type"],
                    record["source_id"] or None,
                    record["queue_job_id"] or None,
                    record["provider_job_id"] or None,
                    record["orchestration_id"] or None,
                    record["orchestration_step_id"] or None,
                    record["reason"],
                    record["error_summary"],
                    _json(record["payload"]),
                    record["status"],
                ),
            )
            row = cur.fetchone()
        conn.commit()
    dead_letter = _row_to_record(row, _dead_letter_columns())
    review = None
    if create_review:
        review = create_manual_review_item(
            tenant_id=dead_letter["tenant_id"],
            project_id=dead_letter["project_id"],
            source_type="dead_letter",
            source_id=dead_letter["dead_letter_id"],
            provider_job_id=dead_letter.get("provider_job_id") or "",
            orchestration_id=dead_letter.get("orchestration_id") or "",
            orchestration_step_id=dead_letter.get("orchestration_step_id") or "",
            queue_job_id=dead_letter.get("queue_job_id") or "",
            review_type="dead_letter_review",
            status="pending_owner_review",
            priority="high",
            reason=dead_letter.get("reason") or "",
            summary=dead_letter.get("error_summary") or "",
            payload={"dead_letter_id": dead_letter["dead_letter_id"], **dead_letter.get("payload", {})},
        )
    return _safe_response(success=True, status=dead_letter["status"], dead_letter=dead_letter, dead_letter_id=dead_letter["dead_letter_id"], review_item=(review or {}).get("item"), storage_mode="postgres", durable=True)


def get_dead_letter_record(dead_letter_id: str) -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness
    clean_id = _coerce_id(dead_letter_id)
    if _using_dev(readiness):
        item = _DEV_DEAD_LETTERS.get(clean_id)
        if not item:
            return _safe_response(success=False, status="dead_letter_not_found", dead_letter_id=clean_id, storage_mode="dev_memory", dev_only=True)
        return _safe_response(success=True, status="found", dead_letter=deepcopy(item), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT dead_letter_id, tenant_id, project_id, source_type, source_id,
                       queue_job_id, provider_job_id, orchestration_id,
                       orchestration_step_id, reason, error_summary, payload_json,
                       status, created_at, updated_at, resolved_at
                FROM dead_letter_records
                WHERE dead_letter_id = %s
                """,
                (clean_id,),
            )
            row = cur.fetchone()
    if not row:
        return _safe_response(success=False, status="dead_letter_not_found", dead_letter_id=clean_id, storage_mode="postgres", durable=True)
    return _safe_response(success=True, status="found", dead_letter=_row_to_record(row, _dead_letter_columns()), storage_mode="postgres", durable=True)


def list_dead_letter_records(*, tenant_id: str = "", status: str = "", limit: int = 50) -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        rows = list(_DEV_DEAD_LETTERS.values())
        if tenant_id:
            rows = [row for row in rows if row.get("tenant_id") == tenant_id]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        rows = sorted(rows, key=lambda row: str(row.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", count=len(rows), dead_letters=deepcopy(rows), items=deepcopy(rows), storage_mode="dev_memory", dev_only=True)
    clauses: List[str] = []
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if status:
        clauses.append("status = %s")
        params.append(status)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT dead_letter_id, tenant_id, project_id, source_type, source_id,
                       queue_job_id, provider_job_id, orchestration_id,
                       orchestration_step_id, reason, error_summary, payload_json,
                       status, created_at, updated_at, resolved_at
                FROM dead_letter_records
                {where}
                ORDER BY created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    records = [_row_to_record(row, _dead_letter_columns()) for row in rows]
    return _safe_response(success=True, status="listed", count=len(records), dead_letters=records, items=records, storage_mode="postgres", durable=True)


def resolve_dead_letter_record(dead_letter_id: str, *, reason: str = "dead_letter_resolved") -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness
    clean_id = _coerce_id(dead_letter_id)
    if _using_dev(readiness):
        record = _DEV_DEAD_LETTERS.get(clean_id)
        if not record:
            return _safe_response(success=False, status="dead_letter_not_found", dead_letter_id=clean_id, storage_mode="dev_memory", dev_only=True)
        if record.get("status") == "resolved":
            return _safe_response(success=True, status="resolved", dead_letter=deepcopy(record), idempotent_replay=True, storage_mode="dev_memory", dev_only=True)
        record["status"] = "resolved"
        record["updated_at"] = _now_iso()
        record["resolved_at"] = record["updated_at"]
        record["resolution_reason"] = reason
        _DEV_DEAD_LETTERS[clean_id] = deepcopy(record)
        return _safe_response(success=True, status="resolved", dead_letter=deepcopy(record), storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE dead_letter_records
                SET status = 'resolved', updated_at = NOW(), resolved_at = COALESCE(resolved_at, NOW())
                WHERE dead_letter_id = %s
                RETURNING dead_letter_id, tenant_id, project_id, source_type, source_id,
                          queue_job_id, provider_job_id, orchestration_id,
                          orchestration_step_id, reason, error_summary, payload_json,
                          status, created_at, updated_at, resolved_at
                """,
                (clean_id,),
            )
            row = cur.fetchone()
        conn.commit()
    if not row:
        return _safe_response(success=False, status="dead_letter_not_found", dead_letter_id=clean_id, storage_mode="postgres", durable=True)
    return _safe_response(success=True, status="resolved", dead_letter=_row_to_record(row, _dead_letter_columns()), storage_mode="postgres", durable=True)


def create_recovery_action(
    *,
    tenant_id: str,
    project_id: str = "default_project",
    review_id: str = "",
    dead_letter_id: str = "",
    orchestration_id: str = "",
    provider_job_id: str = "",
    queue_job_id: str = "",
    action_type: str,
    status: str = "requested",
    payload: Optional[Dict[str, Any]] = None,
    recovery_action_id: str = "",
) -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness
    action = {
        "recovery_action_id": _coerce_id(recovery_action_id) or f"recovery_{uuid.uuid4().hex[:16]}",
        "tenant_id": _coerce_id(tenant_id) or "unknown",
        "project_id": _coerce_id(project_id) or "default_project",
        "review_id": _coerce_id(review_id),
        "dead_letter_id": _coerce_id(dead_letter_id),
        "orchestration_id": _coerce_id(orchestration_id),
        "provider_job_id": _coerce_id(provider_job_id),
        "queue_job_id": _coerce_id(queue_job_id),
        "action_type": _coerce_id(action_type) or "recovery_action",
        "status": _coerce_id(status) or "requested",
        "payload": _scrub_sensitive(payload or {}),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "completed_at": None,
        "failed_at": None,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_RECOVERY_ACTIONS[action["recovery_action_id"]] = deepcopy(action)
        return _safe_response(success=True, status=action["status"], recovery_action=deepcopy(action), recovery_action_id=action["recovery_action_id"], storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO recovery_actions
                (recovery_action_id, tenant_id, project_id, review_id, dead_letter_id,
                 orchestration_id, provider_job_id, queue_job_id, action_type, status,
                 payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING recovery_action_id, tenant_id, project_id, review_id,
                          dead_letter_id, orchestration_id, provider_job_id,
                          queue_job_id, action_type, status, payload_json, created_at,
                          updated_at, completed_at, failed_at
                """,
                (
                    action["recovery_action_id"],
                    action["tenant_id"],
                    action["project_id"],
                    action["review_id"] or None,
                    action["dead_letter_id"] or None,
                    action["orchestration_id"] or None,
                    action["provider_job_id"] or None,
                    action["queue_job_id"] or None,
                    action["action_type"],
                    action["status"],
                    _json(action["payload"]),
                ),
            )
            row = cur.fetchone()
        conn.commit()
    record = _row_to_record(row, _recovery_action_columns())
    return _safe_response(success=True, status=record["status"], recovery_action=record, recovery_action_id=record["recovery_action_id"], storage_mode="postgres", durable=True)


def list_recovery_actions(*, tenant_id: str = "", review_id: str = "", status: str = "", limit: int = 50) -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        actions = list(_DEV_RECOVERY_ACTIONS.values())
        if tenant_id:
            actions = [action for action in actions if action.get("tenant_id") == tenant_id]
        if review_id:
            actions = [action for action in actions if action.get("review_id") == review_id]
        if status:
            actions = [action for action in actions if action.get("status") == status]
        actions = sorted(actions, key=lambda action: str(action.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", count=len(actions), recovery_actions=deepcopy(actions), storage_mode="dev_memory", dev_only=True)
    clauses: List[str] = []
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if review_id:
        clauses.append("review_id = %s")
        params.append(review_id)
    if status:
        clauses.append("status = %s")
        params.append(status)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT recovery_action_id, tenant_id, project_id, review_id,
                       dead_letter_id, orchestration_id, provider_job_id,
                       queue_job_id, action_type, status, payload_json, created_at,
                       updated_at, completed_at, failed_at
                FROM recovery_actions
                {where}
                ORDER BY created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    actions = [_row_to_record(row, _recovery_action_columns()) for row in rows]
    return _safe_response(success=True, status="listed", count=len(actions), recovery_actions=actions, storage_mode="postgres", durable=True)


def get_review_recovery_summary(tenant_id: str = "") -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    if not readiness.get("success"):
        return readiness
    reviews = list_manual_review_items(tenant_id=tenant_id, limit=500)
    dead_letters = list_dead_letter_records(tenant_id=tenant_id, limit=500)
    recovery_actions = list_recovery_actions(tenant_id=tenant_id, limit=500)
    review_counts: Dict[str, int] = {}
    for item in reviews.get("items", []):
        status = str(item.get("status") or "unknown")
        review_counts[status] = review_counts.get(status, 0) + 1
    dead_letter_counts: Dict[str, int] = {}
    for record in dead_letters.get("dead_letters", []):
        status = str(record.get("status") or "unknown")
        dead_letter_counts[status] = dead_letter_counts.get(status, 0) + 1
    return _safe_response(
        success=True,
        status="ready",
        manual_review_recovery_ready=True,
        storage_mode=readiness.get("storage_mode"),
        durable=readiness.get("durable", False),
        dev_only=readiness.get("dev_only", False),
        not_production_durable=readiness.get("not_production_durable", False),
        review_count=reviews.get("count", 0),
        dead_letter_count=dead_letters.get("count", 0),
        recovery_action_count=recovery_actions.get("count", 0),
        review_status_counts=review_counts,
        dead_letter_status_counts=dead_letter_counts,
        manual_review_items=reviews.get("items", [])[:20],
        dead_letters=dead_letters.get("dead_letters", [])[:20],
        recovery_actions=recovery_actions.get("recovery_actions", [])[:20],
    )


def reset_dev_manual_review_recovery_for_tests() -> Dict[str, Any]:
    _DEV_REVIEW_ITEMS.clear()
    _DEV_DECISIONS.clear()
    _DEV_DEAD_LETTERS.clear()
    _DEV_RECOVERY_ACTIONS.clear()
    return _safe_response(success=True, reset=True, status="dev_manual_review_recovery_reset", storage_mode="dev_memory", dev_only=True, not_production_durable=True)
