"""
Queue telemetry and worker health snapshot.

Safe visibility foundation for future Redis/worker scaling.

This module:
- Does not connect to Redis by default.
- Does not execute jobs.
- Does not alter live routes.
- Produces customer-safe/admin-safe queue health snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.runtime.queue_adapter import BaseQueueAdapter, create_queue_adapter
from backend.app.runtime.queue_isolation_policy import export_queue_isolation_snapshot


@dataclass(frozen=True)
class QueueHealthSnapshot:
    generated_at: str
    adapter: str
    adapter_available: bool
    redis_required: bool
    queue_count: int
    total_messages: int
    queues: Dict[str, Dict[str, Any]]
    worker_health: Dict[str, Any]
    governance: Dict[str, Any]
    customer_safe: bool = True


DEFAULT_QUEUE_NAMES = [
    "client_agent_execution_queue",
    "provider_generation_queue",
    "external_integration_action_queue",
    "reporting_queue",
    "retry_reconciliation_queue",
    "admin_internal_queue",
]


def build_worker_health_snapshot(worker_count: int = 0, active_workers: int = 0) -> Dict[str, Any]:
    status = "not_started"
    if worker_count > 0 and active_workers > 0:
        status = "active"
    elif worker_count > 0 and active_workers == 0:
        status = "configured_but_inactive"

    return {
        "status": status,
        "worker_count_configured": worker_count,
        "active_workers": active_workers,
        "live_execution_changed": False,
        "jobs_executed_by_snapshot": False,
    }


def build_queue_health_snapshot(
    adapter: Optional[BaseQueueAdapter] = None,
    queue_names: Optional[List[str]] = None,
    worker_count: int = 0,
    active_workers: int = 0,
) -> QueueHealthSnapshot:
    queue_adapter = adapter or create_queue_adapter()
    names = queue_names or list(DEFAULT_QUEUE_NAMES)
    adapter_health = queue_adapter.health()

    queue_details: Dict[str, Dict[str, Any]] = {}
    total_messages = 0

    for name in names:
        try:
            size = int(queue_adapter.size(name))
        except Exception:
            size = 0

        total_messages += size
        queue_details[name] = {
            "queue_name": name,
            "size": size,
            "available": bool(adapter_health.get("available", False)),
            "customer_safe": True,
        }

    policy_snapshot = export_queue_isolation_snapshot()

    return QueueHealthSnapshot(
        generated_at=datetime.now(timezone.utc).isoformat(),
        adapter=str(adapter_health.get("adapter", "unknown")),
        adapter_available=bool(adapter_health.get("available", False)),
        redis_required=bool(adapter_health.get("redis_required", False)),
        queue_count=len(queue_details),
        total_messages=total_messages,
        queues=queue_details,
        worker_health=build_worker_health_snapshot(worker_count, active_workers),
        governance={
            "owner_approval_preserved": True,
            "live_external_execution_enabled_by_snapshot": False,
            "customer_safe_snapshot": True,
            "policy_groups": sorted(policy_snapshot.keys()),
        },
        customer_safe=True,
    )


def export_queue_health_dict(snapshot: QueueHealthSnapshot) -> Dict[str, Any]:
    return {
        "generated_at": snapshot.generated_at,
        "adapter": snapshot.adapter,
        "adapter_available": snapshot.adapter_available,
        "redis_required": snapshot.redis_required,
        "queue_count": snapshot.queue_count,
        "total_messages": snapshot.total_messages,
        "queues": snapshot.queues,
        "worker_health": snapshot.worker_health,
        "governance": snapshot.governance,
        "customer_safe": snapshot.customer_safe,
    }


def queue_telemetry_changes_live_execution() -> bool:
    return False


def queue_telemetry_executes_jobs() -> bool:
    return False
