from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


DURABLE_ORCHESTRATION_PROFILE = "durable_orchestration_state_runtime_v1"

_DEV_PLANS: Dict[str, Dict[str, Any]] = {}
_DEV_STEPS: Dict[str, Dict[str, Any]] = {}
_DEV_EVENTS: List[Dict[str, Any]] = []
_DEV_RESULT_MEMORY: List[Dict[str, Any]] = []
_DEV_RECOVERY_CHECKPOINTS: List[Dict[str, Any]] = []


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
    timeout = max(1, min(int(os.getenv("ORCHESTRATION_CONNECT_TIMEOUT_SECONDS") or 2), 10))
    return psycopg.connect(_database_url(), connect_timeout=timeout)


def _safe_response(**payload: Any) -> Dict[str, Any]:
    result = dict(payload)
    result.setdefault("orchestration_profile", DURABLE_ORCHESTRATION_PROFILE)
    result.setdefault("credential_values_exposed", False)
    result.setdefault("customer_safe", True)
    return result


def _unavailable(reason: str) -> Dict[str, Any]:
    return _safe_response(
        success=False,
        status="orchestration_store_unavailable",
        orchestration_store_ready=False,
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
    return json.dumps(deepcopy(data or {}), ensure_ascii=False, sort_keys=True)


def _json_list(data: Optional[List[str]]) -> str:
    return json.dumps(list(data or []), ensure_ascii=False, sort_keys=True)


def _parse_json(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _parse_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return [str(item) for item in parsed] if isinstance(parsed, list) else []
        except Exception:
            return []
    return []


def _dt(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


def _limit(value: int, default: int = 100, maximum: int = 500) -> int:
    try:
        parsed = int(value or default)
    except Exception:
        parsed = default
    return max(1, min(parsed, maximum))


def _plan_columns() -> List[str]:
    return [
        "orchestration_id",
        "tenant_id",
        "project_id",
        "root_agent_id",
        "status",
        "plan_type",
        "payload_json",
        "created_at",
        "updated_at",
        "completed_at",
        "failed_at",
        "credential_values_exposed",
    ]


def _step_columns() -> List[str]:
    return [
        "step_id",
        "orchestration_id",
        "tenant_id",
        "agent_id",
        "action_type",
        "status",
        "dependency_step_ids",
        "execution_job_id",
        "provider_execution_id",
        "attempt_count",
        "created_at",
        "updated_at",
        "started_at",
        "completed_at",
        "failed_at",
        "last_error",
    ]


def _event_columns() -> List[str]:
    return ["event_id", "orchestration_id", "step_id", "tenant_id", "event_type", "payload_json", "created_at"]


def _memory_columns() -> List[str]:
    return [
        "memory_id",
        "orchestration_id",
        "step_id",
        "tenant_id",
        "agent_id",
        "result_type",
        "result_summary",
        "payload_json",
        "created_at",
    ]


def _checkpoint_columns() -> List[str]:
    return ["checkpoint_id", "orchestration_id", "tenant_id", "checkpoint_type", "recoverable_status", "payload_json", "created_at"]


def _row_to_plan(row: Any) -> Dict[str, Any]:
    data = dict(zip(_plan_columns(), row))
    data["payload"] = _parse_json(data.pop("payload_json", None))
    for key, value in list(data.items()):
        data[key] = _dt(value)
    data["credential_values_exposed"] = False
    data["customer_safe"] = True
    return data


def _row_to_step(row: Any) -> Dict[str, Any]:
    data = dict(zip(_step_columns(), row))
    data["dependency_step_ids"] = _parse_list(data.get("dependency_step_ids"))
    data["attempt_count"] = int(data.get("attempt_count") or 0)
    for key, value in list(data.items()):
        data[key] = _dt(value)
    data["credential_values_exposed"] = False
    data["customer_safe"] = True
    return data


def _row_to_event(row: Any) -> Dict[str, Any]:
    data = dict(zip(_event_columns(), row))
    data["payload"] = _parse_json(data.pop("payload_json", None))
    for key, value in list(data.items()):
        data[key] = _dt(value)
    data["credential_values_exposed"] = False
    return data


def _row_to_memory(row: Any) -> Dict[str, Any]:
    data = dict(zip(_memory_columns(), row))
    data["payload"] = _parse_json(data.pop("payload_json", None))
    for key, value in list(data.items()):
        data[key] = _dt(value)
    data["credential_values_exposed"] = False
    return data


def _row_to_checkpoint(row: Any) -> Dict[str, Any]:
    data = dict(zip(_checkpoint_columns(), row))
    data["payload"] = _parse_json(data.pop("payload_json", None))
    for key, value in list(data.items()):
        data[key] = _dt(value)
    data["credential_values_exposed"] = False
    return data


def ensure_orchestration_tables() -> Dict[str, Any]:
    if not _database_url():
        if _is_production():
            return _unavailable("DATABASE_URL_missing")
        return _safe_response(
            success=True,
            status="dev_only_orchestration_store_ready",
            orchestration_store_ready=True,
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
            status="dev_only_orchestration_store_ready",
            orchestration_store_ready=True,
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
                    CREATE TABLE IF NOT EXISTS orchestration_plans (
                        orchestration_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        root_agent_id TEXT,
                        status TEXT NOT NULL,
                        plan_type TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        completed_at TIMESTAMPTZ,
                        failed_at TIMESTAMPTZ,
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_orchestration_plans_tenant_status ON orchestration_plans (tenant_id, status, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_orchestration_plans_project ON orchestration_plans (tenant_id, project_id)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orchestration_steps (
                        step_id TEXT PRIMARY KEY,
                        orchestration_id TEXT NOT NULL,
                        tenant_id TEXT NOT NULL,
                        agent_id TEXT,
                        action_type TEXT,
                        status TEXT NOT NULL,
                        dependency_step_ids JSONB DEFAULT '[]'::jsonb,
                        execution_job_id TEXT,
                        provider_execution_id TEXT,
                        attempt_count INTEGER NOT NULL DEFAULT 0,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        started_at TIMESTAMPTZ,
                        completed_at TIMESTAMPTZ,
                        failed_at TIMESTAMPTZ,
                        last_error TEXT
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_orchestration_steps_orchestration ON orchestration_steps (orchestration_id, created_at)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_orchestration_steps_tenant_status ON orchestration_steps (tenant_id, status, created_at DESC)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orchestration_events (
                        event_id TEXT PRIMARY KEY,
                        orchestration_id TEXT NOT NULL,
                        step_id TEXT,
                        tenant_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_orchestration_events_orchestration ON orchestration_events (orchestration_id, created_at)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orchestration_result_memory (
                        memory_id TEXT PRIMARY KEY,
                        orchestration_id TEXT NOT NULL,
                        step_id TEXT,
                        tenant_id TEXT NOT NULL,
                        agent_id TEXT,
                        result_type TEXT,
                        result_summary TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_orchestration_result_memory_orchestration ON orchestration_result_memory (orchestration_id, created_at)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orchestration_recovery_checkpoints (
                        checkpoint_id TEXT PRIMARY KEY,
                        orchestration_id TEXT NOT NULL,
                        tenant_id TEXT NOT NULL,
                        checkpoint_type TEXT NOT NULL,
                        recoverable_status TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_orchestration_recovery_orchestration ON orchestration_recovery_checkpoints (orchestration_id, created_at)")
            conn.commit()
        return _safe_response(
            success=True,
            status="orchestration_store_ready",
            orchestration_store_ready=True,
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
            status="dev_only_orchestration_store_ready",
            orchestration_store_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
            postgres_error=str(exc),
        )


def create_orchestration_plan(
    *,
    orchestration_id: str = "",
    tenant_id: str,
    project_id: str = "default_project",
    root_agent_id: str = "orchestration_agent",
    status: str = "pending",
    plan_type: str = "orchestration",
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness

    plan_id = str(orchestration_id or f"orch_{uuid.uuid4().hex[:16]}")
    now = _now_iso()
    plan = {
        "orchestration_id": plan_id,
        "tenant_id": str(tenant_id or "unknown"),
        "project_id": str(project_id or "default_project"),
        "root_agent_id": str(root_agent_id or "orchestration_agent"),
        "status": str(status or "pending"),
        "plan_type": str(plan_type or "orchestration"),
        "payload": deepcopy(payload or {}),
        "created_at": now,
        "updated_at": now,
        "completed_at": None,
        "failed_at": None,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    if _using_dev(readiness):
        existing_created_at = _DEV_PLANS.get(plan_id, {}).get("created_at")
        if existing_created_at:
            plan["created_at"] = existing_created_at
        _DEV_PLANS[plan_id] = deepcopy(plan)
        record_orchestration_event(
            orchestration_id=plan_id,
            tenant_id=plan["tenant_id"],
            event_type="orchestration_plan_created",
            payload={"status": plan["status"], "plan_type": plan["plan_type"]},
        )
        return _safe_response(success=True, status="created", plan=deepcopy(plan), orchestration_id=plan_id, storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orchestration_plans
                (orchestration_id, tenant_id, project_id, root_agent_id, status, plan_type, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (orchestration_id) DO UPDATE SET
                    tenant_id = EXCLUDED.tenant_id,
                    project_id = EXCLUDED.project_id,
                    root_agent_id = EXCLUDED.root_agent_id,
                    status = EXCLUDED.status,
                    plan_type = EXCLUDED.plan_type,
                    payload_json = EXCLUDED.payload_json,
                    updated_at = NOW()
                RETURNING orchestration_id, tenant_id, project_id, root_agent_id, status,
                          plan_type, payload_json, created_at, updated_at, completed_at,
                          failed_at, credential_values_exposed
                """,
                (plan_id, plan["tenant_id"], plan["project_id"], plan["root_agent_id"], plan["status"], plan["plan_type"], _json(plan["payload"])),
            )
            row = cur.fetchone()
        conn.commit()

    record_orchestration_event(
        orchestration_id=plan_id,
        tenant_id=plan["tenant_id"],
        event_type="orchestration_plan_created",
        payload={"status": plan["status"], "plan_type": plan["plan_type"]},
    )
    return _safe_response(success=True, status="created", plan=_row_to_plan(row), orchestration_id=plan_id, storage_mode="postgres", durable=True)


def update_orchestration_plan_status(
    *,
    orchestration_id: str,
    status: str,
    payload: Optional[Dict[str, Any]] = None,
    completed: bool = False,
    failed: bool = False,
) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness

    plan_id = str(orchestration_id or "")
    if _using_dev(readiness):
        plan = _DEV_PLANS.get(plan_id)
        if not plan:
            return _safe_response(success=False, status="orchestration_not_found", orchestration_id=plan_id, storage_mode="dev_memory", dev_only=True)
        plan["status"] = str(status or plan.get("status") or "pending")
        if payload is not None:
            plan["payload"] = deepcopy(payload)
        plan["updated_at"] = _now_iso()
        if completed:
            plan["completed_at"] = plan["updated_at"]
        if failed:
            plan["failed_at"] = plan["updated_at"]
        _DEV_PLANS[plan_id] = deepcopy(plan)
        return _safe_response(success=True, status="updated", plan=deepcopy(plan), storage_mode="dev_memory", dev_only=True)

    completed_sql = "completed_at = NOW()," if completed else ""
    failed_sql = "failed_at = NOW()," if failed else ""
    with _connect() as conn:
        with conn.cursor() as cur:
            if payload is None:
                cur.execute(
                    f"""
                    UPDATE orchestration_plans
                    SET status = %s, {completed_sql} {failed_sql} updated_at = NOW()
                    WHERE orchestration_id = %s
                    RETURNING orchestration_id, tenant_id, project_id, root_agent_id, status,
                              plan_type, payload_json, created_at, updated_at, completed_at,
                              failed_at, credential_values_exposed
                    """,
                    (status, plan_id),
                )
            else:
                cur.execute(
                    f"""
                    UPDATE orchestration_plans
                    SET status = %s, payload_json = %s::jsonb, {completed_sql} {failed_sql} updated_at = NOW()
                    WHERE orchestration_id = %s
                    RETURNING orchestration_id, tenant_id, project_id, root_agent_id, status,
                              plan_type, payload_json, created_at, updated_at, completed_at,
                              failed_at, credential_values_exposed
                    """,
                    (status, _json(payload), plan_id),
                )
            row = cur.fetchone()
        conn.commit()
    if not row:
        return _safe_response(success=False, status="orchestration_not_found", orchestration_id=plan_id, storage_mode="postgres", durable=True)
    return _safe_response(success=True, status="updated", plan=_row_to_plan(row), storage_mode="postgres", durable=True)


def get_orchestration_plan(orchestration_id: str) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness

    plan_id = str(orchestration_id or "")
    if _using_dev(readiness):
        plan = deepcopy(_DEV_PLANS.get(plan_id))
        if not plan:
            return _safe_response(success=False, status="orchestration_not_found", orchestration_id=plan_id, storage_mode="dev_memory", dev_only=True)
        steps = [deepcopy(step) for step in _DEV_STEPS.values() if step.get("orchestration_id") == plan_id]
        steps.sort(key=lambda item: str(item.get("created_at") or ""))
        return _safe_response(success=True, status=plan.get("status"), plan=plan, steps=steps, orchestration_id=plan_id, storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT orchestration_id, tenant_id, project_id, root_agent_id, status,
                       plan_type, payload_json, created_at, updated_at, completed_at,
                       failed_at, credential_values_exposed
                FROM orchestration_plans
                WHERE orchestration_id = %s
                """,
                (plan_id,),
            )
            row = cur.fetchone()
            if not row:
                return _safe_response(success=False, status="orchestration_not_found", orchestration_id=plan_id, storage_mode="postgres", durable=True)
            cur.execute(
                """
                SELECT step_id, orchestration_id, tenant_id, agent_id, action_type, status,
                       dependency_step_ids, execution_job_id, provider_execution_id, attempt_count,
                       created_at, updated_at, started_at, completed_at, failed_at, last_error
                FROM orchestration_steps
                WHERE orchestration_id = %s
                ORDER BY created_at ASC
                """,
                (plan_id,),
            )
            step_rows = cur.fetchall()
    plan = _row_to_plan(row)
    return _safe_response(success=True, status=plan.get("status"), plan=plan, steps=[_row_to_step(step) for step in step_rows], orchestration_id=plan_id, storage_mode="postgres", durable=True)


def list_orchestration_plans(tenant_id: str = "", status: str = "", limit: int = 100) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)

    if _using_dev(readiness):
        plans = list(_DEV_PLANS.values())
        if tenant_id:
            plans = [plan for plan in plans if plan.get("tenant_id") == tenant_id]
        if status:
            plans = [plan for plan in plans if plan.get("status") == status]
        plans = sorted(plans, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", plans=deepcopy(plans), count=len(plans), storage_mode="dev_memory", dev_only=True)

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
                SELECT orchestration_id, tenant_id, project_id, root_agent_id, status,
                       plan_type, payload_json, created_at, updated_at, completed_at,
                       failed_at, credential_values_exposed
                FROM orchestration_plans
                {where}
                ORDER BY created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    plans = [_row_to_plan(row) for row in rows]
    return _safe_response(success=True, status="listed", plans=plans, count=len(plans), storage_mode="postgres", durable=True)


def create_orchestration_step(
    *,
    step_id: str = "",
    orchestration_id: str,
    tenant_id: str,
    agent_id: str,
    action_type: str,
    status: str = "pending",
    dependency_step_ids: Optional[List[str]] = None,
    execution_job_id: str = "",
    provider_execution_id: str = "",
    attempt_count: int = 0,
) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness

    clean_step_id = str(step_id or f"step_{uuid.uuid4().hex[:16]}")
    now = _now_iso()
    step = {
        "step_id": clean_step_id,
        "orchestration_id": str(orchestration_id or ""),
        "tenant_id": str(tenant_id or "unknown"),
        "agent_id": str(agent_id or ""),
        "action_type": str(action_type or "orchestrated_step"),
        "status": str(status or "pending"),
        "dependency_step_ids": list(dependency_step_ids or []),
        "execution_job_id": execution_job_id or None,
        "provider_execution_id": provider_execution_id or None,
        "attempt_count": int(attempt_count or 0),
        "created_at": now,
        "updated_at": now,
        "started_at": None,
        "completed_at": None,
        "failed_at": None,
        "last_error": None,
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    if _using_dev(readiness):
        existing_created_at = _DEV_STEPS.get(clean_step_id, {}).get("created_at")
        if existing_created_at:
            step["created_at"] = existing_created_at
        _DEV_STEPS[clean_step_id] = deepcopy(step)
        record_orchestration_event(
            orchestration_id=step["orchestration_id"],
            step_id=clean_step_id,
            tenant_id=step["tenant_id"],
            event_type="orchestration_step_created",
            payload={"agent_id": step["agent_id"], "action_type": step["action_type"], "status": step["status"]},
        )
        return _safe_response(success=True, status="created", step=deepcopy(step), step_id=clean_step_id, storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orchestration_steps
                (step_id, orchestration_id, tenant_id, agent_id, action_type, status,
                 dependency_step_ids, execution_job_id, provider_execution_id, attempt_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s)
                ON CONFLICT (step_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    dependency_step_ids = EXCLUDED.dependency_step_ids,
                    execution_job_id = EXCLUDED.execution_job_id,
                    provider_execution_id = EXCLUDED.provider_execution_id,
                    attempt_count = EXCLUDED.attempt_count,
                    updated_at = NOW()
                RETURNING step_id, orchestration_id, tenant_id, agent_id, action_type, status,
                          dependency_step_ids, execution_job_id, provider_execution_id, attempt_count,
                          created_at, updated_at, started_at, completed_at, failed_at, last_error
                """,
                (
                    clean_step_id,
                    step["orchestration_id"],
                    step["tenant_id"],
                    step["agent_id"],
                    step["action_type"],
                    step["status"],
                    _json_list(step["dependency_step_ids"]),
                    step["execution_job_id"],
                    step["provider_execution_id"],
                    step["attempt_count"],
                ),
            )
            row = cur.fetchone()
        conn.commit()

    record_orchestration_event(
        orchestration_id=step["orchestration_id"],
        step_id=clean_step_id,
        tenant_id=step["tenant_id"],
        event_type="orchestration_step_created",
        payload={"agent_id": step["agent_id"], "action_type": step["action_type"], "status": step["status"]},
    )
    return _safe_response(success=True, status="created", step=_row_to_step(row), step_id=clean_step_id, storage_mode="postgres", durable=True)


def update_orchestration_step_status(
    *,
    step_id: str,
    status: str,
    orchestration_id: str = "",
    tenant_id: str = "",
    execution_job_id: str = "",
    provider_execution_id: str = "",
    last_error: str = "",
    increment_attempt: bool = False,
) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness

    clean_step_id = str(step_id or "")
    clean_status = str(status or "pending")
    started_at = _now_iso() if clean_status in {"running", "in_progress", "leased"} else None
    completed_at = _now_iso() if clean_status in {"completed", "succeeded"} else None
    failed_at = _now_iso() if clean_status in {"failed", "dead_letter", "failed_manual_review_required"} else None

    if _using_dev(readiness):
        step = _DEV_STEPS.get(clean_step_id)
        if not step:
            return _safe_response(success=False, status="step_not_found", step_id=clean_step_id, storage_mode="dev_memory", dev_only=True)
        step["status"] = clean_status
        step["updated_at"] = _now_iso()
        if execution_job_id:
            step["execution_job_id"] = execution_job_id
        if provider_execution_id:
            step["provider_execution_id"] = provider_execution_id
        if last_error:
            step["last_error"] = last_error
        if increment_attempt:
            step["attempt_count"] = int(step.get("attempt_count") or 0) + 1
        if started_at:
            step["started_at"] = started_at
        if completed_at:
            step["completed_at"] = completed_at
        if failed_at:
            step["failed_at"] = failed_at
        _DEV_STEPS[clean_step_id] = deepcopy(step)
        record_orchestration_event(
            orchestration_id=str(orchestration_id or step.get("orchestration_id") or ""),
            step_id=clean_step_id,
            tenant_id=str(tenant_id or step.get("tenant_id") or "unknown"),
            event_type="orchestration_step_status_updated",
            payload={"status": clean_status, "last_error": last_error},
        )
        return _safe_response(success=True, status="updated", step=deepcopy(step), storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE orchestration_steps
                SET status = %s,
                    execution_job_id = COALESCE(NULLIF(%s, ''), execution_job_id),
                    provider_execution_id = COALESCE(NULLIF(%s, ''), provider_execution_id),
                    last_error = COALESCE(NULLIF(%s, ''), last_error),
                    attempt_count = attempt_count + %s,
                    started_at = COALESCE(started_at, %s),
                    completed_at = COALESCE(completed_at, %s),
                    failed_at = COALESCE(failed_at, %s),
                    updated_at = NOW()
                WHERE step_id = %s
                RETURNING step_id, orchestration_id, tenant_id, agent_id, action_type, status,
                          dependency_step_ids, execution_job_id, provider_execution_id, attempt_count,
                          created_at, updated_at, started_at, completed_at, failed_at, last_error
                """,
                (
                    clean_status,
                    execution_job_id,
                    provider_execution_id,
                    last_error,
                    1 if increment_attempt else 0,
                    started_at,
                    completed_at,
                    failed_at,
                    clean_step_id,
                ),
            )
            row = cur.fetchone()
        conn.commit()
    if not row:
        return _safe_response(success=False, status="step_not_found", step_id=clean_step_id, storage_mode="postgres", durable=True)
    step = _row_to_step(row)
    record_orchestration_event(
        orchestration_id=str(orchestration_id or step.get("orchestration_id") or ""),
        step_id=clean_step_id,
        tenant_id=str(tenant_id or step.get("tenant_id") or "unknown"),
        event_type="orchestration_step_status_updated",
        payload={"status": clean_status, "last_error": last_error},
    )
    return _safe_response(success=True, status="updated", step=step, storage_mode="postgres", durable=True)


def record_orchestration_event(
    *,
    orchestration_id: str,
    tenant_id: str,
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    step_id: str | None = None,
) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness

    event = {
        "event_id": f"orch_event_{uuid.uuid4().hex[:16]}",
        "orchestration_id": str(orchestration_id or ""),
        "step_id": step_id or None,
        "tenant_id": str(tenant_id or "unknown"),
        "event_type": str(event_type or "orchestration_event"),
        "payload": deepcopy(payload or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
    }

    if _using_dev(readiness):
        _DEV_EVENTS.append(deepcopy(event))
        return _safe_response(success=True, status="recorded", event=deepcopy(event), event_id=event["event_id"], storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orchestration_events
                (event_id, orchestration_id, step_id, tenant_id, event_type, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                RETURNING event_id, orchestration_id, step_id, tenant_id, event_type, payload_json, created_at
                """,
                (event["event_id"], event["orchestration_id"], event["step_id"], event["tenant_id"], event["event_type"], _json(event["payload"])),
            )
            row = cur.fetchone()
        conn.commit()
    return _safe_response(success=True, status="recorded", event=_row_to_event(row), event_id=event["event_id"], storage_mode="postgres", durable=True)


def list_orchestration_events(orchestration_id: str = "", tenant_id: str = "", limit: int = 100) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)

    if _using_dev(readiness):
        events = list(_DEV_EVENTS)
        if orchestration_id:
            events = [event for event in events if event.get("orchestration_id") == orchestration_id]
        if tenant_id:
            events = [event for event in events if event.get("tenant_id") == tenant_id]
        events = sorted(events, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", events=deepcopy(events), count=len(events), storage_mode="dev_memory", dev_only=True)

    clauses: List[str] = []
    params: List[Any] = []
    if orchestration_id:
        clauses.append("orchestration_id = %s")
        params.append(orchestration_id)
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT event_id, orchestration_id, step_id, tenant_id, event_type, payload_json, created_at
                FROM orchestration_events
                {where}
                ORDER BY created_at DESC
                LIMIT %s
                """,
                params,
            )
            rows = cur.fetchall()
    events = [_row_to_event(row) for row in rows]
    return _safe_response(success=True, status="listed", events=events, count=len(events), storage_mode="postgres", durable=True)


def record_orchestration_result_memory(
    *,
    orchestration_id: str,
    tenant_id: str,
    agent_id: str = "",
    result_type: str = "agent_output",
    result_summary: str = "",
    payload: Optional[Dict[str, Any]] = None,
    step_id: str | None = None,
) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness

    memory = {
        "memory_id": f"orch_memory_{uuid.uuid4().hex[:16]}",
        "orchestration_id": str(orchestration_id or ""),
        "step_id": step_id or None,
        "tenant_id": str(tenant_id or "unknown"),
        "agent_id": str(agent_id or ""),
        "result_type": str(result_type or "agent_output"),
        "result_summary": str(result_summary or "")[:2000],
        "payload": deepcopy(payload or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
    }

    if _using_dev(readiness):
        _DEV_RESULT_MEMORY.append(deepcopy(memory))
        return _safe_response(success=True, status="recorded", memory=deepcopy(memory), memory_id=memory["memory_id"], storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orchestration_result_memory
                (memory_id, orchestration_id, step_id, tenant_id, agent_id,
                 result_type, result_summary, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING memory_id, orchestration_id, step_id, tenant_id, agent_id,
                          result_type, result_summary, payload_json, created_at
                """,
                (
                    memory["memory_id"],
                    memory["orchestration_id"],
                    memory["step_id"],
                    memory["tenant_id"],
                    memory["agent_id"],
                    memory["result_type"],
                    memory["result_summary"],
                    _json(memory["payload"]),
                ),
            )
            row = cur.fetchone()
        conn.commit()
    return _safe_response(success=True, status="recorded", memory=_row_to_memory(row), memory_id=memory["memory_id"], storage_mode="postgres", durable=True)


def create_recovery_checkpoint(
    *,
    orchestration_id: str,
    tenant_id: str,
    checkpoint_type: str = "state_checkpoint",
    recoverable_status: str = "recoverable",
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness

    checkpoint = {
        "checkpoint_id": f"orch_checkpoint_{uuid.uuid4().hex[:16]}",
        "orchestration_id": str(orchestration_id or ""),
        "tenant_id": str(tenant_id or "unknown"),
        "checkpoint_type": str(checkpoint_type or "state_checkpoint"),
        "recoverable_status": str(recoverable_status or "recoverable"),
        "payload": deepcopy(payload or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
    }

    if _using_dev(readiness):
        _DEV_RECOVERY_CHECKPOINTS.append(deepcopy(checkpoint))
        return _safe_response(success=True, status="recorded", checkpoint=deepcopy(checkpoint), checkpoint_id=checkpoint["checkpoint_id"], storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orchestration_recovery_checkpoints
                (checkpoint_id, orchestration_id, tenant_id, checkpoint_type, recoverable_status, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                RETURNING checkpoint_id, orchestration_id, tenant_id, checkpoint_type, recoverable_status, payload_json, created_at
                """,
                (
                    checkpoint["checkpoint_id"],
                    checkpoint["orchestration_id"],
                    checkpoint["tenant_id"],
                    checkpoint["checkpoint_type"],
                    checkpoint["recoverable_status"],
                    _json(checkpoint["payload"]),
                ),
            )
            row = cur.fetchone()
        conn.commit()
    return _safe_response(success=True, status="recorded", checkpoint=_row_to_checkpoint(row), checkpoint_id=checkpoint["checkpoint_id"], storage_mode="postgres", durable=True)


def get_orchestration_context(orchestration_id: str, limit: int = 100) -> Dict[str, Any]:
    plan_result = get_orchestration_plan(orchestration_id)
    if not plan_result.get("success"):
        return plan_result

    safe_limit = _limit(limit)
    events_result = list_orchestration_events(orchestration_id=orchestration_id, limit=safe_limit)
    readiness = ensure_orchestration_tables()
    if not readiness.get("success"):
        return readiness

    if _using_dev(readiness):
        memory = [deepcopy(item) for item in _DEV_RESULT_MEMORY if item.get("orchestration_id") == orchestration_id]
        checkpoints = [deepcopy(item) for item in _DEV_RECOVERY_CHECKPOINTS if item.get("orchestration_id") == orchestration_id]
        memory = sorted(memory, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        checkpoints = sorted(checkpoints, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(
            success=True,
            status="context_loaded",
            orchestration_id=orchestration_id,
            plan=plan_result.get("plan"),
            steps=plan_result.get("steps", []),
            events=list(reversed(events_result.get("events", []))),
            state_events=list(reversed(events_result.get("events", []))),
            result_memory=list(reversed(memory)),
            recovery_checkpoints=list(reversed(checkpoints)),
            state_event_count=events_result.get("count", 0),
            result_memory_count=len(memory),
            recovery_checkpoint_count=len(checkpoints),
            cross_agent_context_available=bool(memory),
            recovery_context_available=bool(events_result.get("events") or checkpoints),
            storage_mode="dev_memory",
            dev_only=True,
        )

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT memory_id, orchestration_id, step_id, tenant_id, agent_id,
                       result_type, result_summary, payload_json, created_at
                FROM orchestration_result_memory
                WHERE orchestration_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (orchestration_id, safe_limit),
            )
            memory_rows = cur.fetchall()
            cur.execute(
                """
                SELECT checkpoint_id, orchestration_id, tenant_id, checkpoint_type,
                       recoverable_status, payload_json, created_at
                FROM orchestration_recovery_checkpoints
                WHERE orchestration_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (orchestration_id, safe_limit),
            )
            checkpoint_rows = cur.fetchall()
    memory = [_row_to_memory(row) for row in memory_rows]
    checkpoints = [_row_to_checkpoint(row) for row in checkpoint_rows]
    events = list(reversed(events_result.get("events", [])))
    return _safe_response(
        success=True,
        status="context_loaded",
        orchestration_id=orchestration_id,
        plan=plan_result.get("plan"),
        steps=plan_result.get("steps", []),
        events=events,
        state_events=events,
        result_memory=list(reversed(memory)),
        recovery_checkpoints=list(reversed(checkpoints)),
        state_event_count=events_result.get("count", 0),
        result_memory_count=len(memory),
        recovery_checkpoint_count=len(checkpoints),
        cross_agent_context_available=bool(memory),
        recovery_context_available=bool(events or checkpoints),
        storage_mode="postgres",
        durable=True,
    )


def get_orchestration_recovery_packet(orchestration_id: str) -> Dict[str, Any]:
    context = get_orchestration_context(orchestration_id, limit=200)
    if not context.get("success"):
        return context

    steps = context.get("steps", [])
    events = context.get("events", [])
    checkpoints = context.get("recovery_checkpoints", [])
    completed_steps = [step.get("step_id") for step in steps if step.get("status") in {"completed", "succeeded"}]
    failed_steps = [step for step in steps if step.get("status") in {"failed", "dead_letter", "failed_manual_review_required"}]
    last_event = events[-1] if events else None
    last_checkpoint = checkpoints[-1] if checkpoints else None

    return _safe_response(
        success=True,
        status="recovery_packet_ready",
        orchestration_id=orchestration_id,
        recovery_ready=True,
        plan=context.get("plan"),
        last_event=last_event,
        last_checkpoint=last_checkpoint,
        completed_steps=completed_steps,
        failed_steps=failed_steps,
        result_memory_count=context.get("result_memory_count", 0),
        next_step_selection_ready=True,
        parallel_safe_resume_ready=True,
        storage_mode=context.get("storage_mode"),
        durable=context.get("durable", False),
        dev_only=context.get("dev_only", False),
        not_production_durable=context.get("not_production_durable", False),
    )


def get_orchestration_status(orchestration_id: str) -> Dict[str, Any]:
    context = get_orchestration_context(orchestration_id, limit=100)
    if not context.get("success"):
        return context
    steps = context.get("steps", [])
    counts: Dict[str, int] = {}
    for step in steps:
        status = str(step.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return _safe_response(
        success=True,
        status=context.get("plan", {}).get("status") or "unknown",
        orchestration_id=orchestration_id,
        plan=context.get("plan"),
        step_count=len(steps),
        step_status_counts=counts,
        event_count=context.get("state_event_count", 0),
        result_memory_count=context.get("result_memory_count", 0),
        recovery_checkpoint_count=context.get("recovery_checkpoint_count", 0),
        storage_mode=context.get("storage_mode"),
        durable=context.get("durable", False),
        dev_only=context.get("dev_only", False),
    )


def reset_dev_orchestration_state_for_tests() -> Dict[str, Any]:
    _DEV_PLANS.clear()
    _DEV_STEPS.clear()
    _DEV_EVENTS.clear()
    _DEV_RESULT_MEMORY.clear()
    _DEV_RECOVERY_CHECKPOINTS.clear()
    return _safe_response(success=True, reset=True, status="dev_orchestration_state_reset", storage_mode="dev_memory", dev_only=True, not_production_durable=True)
