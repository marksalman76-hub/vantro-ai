from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from backend.app.runtime.durable_execution_history_evidence_runtime import (
    list_execution_events as durable_list_execution_events,
    record_execution_event,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def add_execution_event(
    tenant_id: str,
    project_id: str,
    event_type: str,
    title: str,
    agent_id: str = "",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = dict(payload or {})
    result = record_execution_event(
        tenant_id=tenant_id,
        project_id=project_id or "default_project",
        execution_id=str(payload.get("execution_id") or payload.get("run_id") or ""),
        event_type=event_type,
        source_type="execution_event_runtime",
        source_id=str(payload.get("source_id") or payload.get("history_id") or ""),
        payload={
            **payload,
            "title": title,
            "agent_id": agent_id,
            "compatibility_wrapper": "execution_event_runtime",
        },
    )
    if not result.get("success"):
        return result
    event = result.get("event") or {}
    return {
        "success": True,
        "event_id": event.get("event_id") or result.get("event_id"),
        "created_at": event.get("created_at") or _now(),
        "storage_mode": result.get("storage_mode"),
        "durable": result.get("durable", False),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_execution_events(
    tenant_id: str,
    project_id: str,
    limit: int = 20,
) -> Dict[str, Any]:
    result = durable_list_execution_events(
        tenant_id=tenant_id,
        project_id=project_id or "default_project",
        limit=limit,
    )
    return {
        **result,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "count": result.get("count", 0),
        "events": result.get("events", []),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
