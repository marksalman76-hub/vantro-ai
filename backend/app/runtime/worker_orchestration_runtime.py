"""
Worker orchestration runtime foundation.

Safe planning/visibility layer for future queue-backed worker execution.

This module:
- Does not execute queued jobs.
- Does not connect to Redis by default.
- Does not call providers or external integrations.
- Does not change live route behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.runtime.queue_adapter import BaseQueueAdapter, create_queue_adapter
from backend.app.runtime.queue_admission_validator import QueueAdmissionRequest, evaluate_queue_admission
from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict


@dataclass(frozen=True)
class WorkerPlanRequest:
    action_type: str
    tenant_id: str = ""
    agent_key: str = ""
    actor_role: str = "client"
    client_has_entitlement: bool = False
    owner_approved: bool = False
    live_external_requested: bool = False
    live_external_enabled: bool = False
    customer_safe: bool = True
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkerPlan:
    created_at: str
    admitted: bool
    queue_target: str
    workload_group: str
    planned_only: bool
    would_enqueue: bool
    would_execute_now: bool
    blocked_reasons: List[str]
    reasons: List[str]
    telemetry: Dict[str, Any]
    governance: Dict[str, Any]


def build_worker_plan(
    request: WorkerPlanRequest,
    adapter: Optional[BaseQueueAdapter] = None,
) -> WorkerPlan:
    admission = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type=request.action_type,
            tenant_id=request.tenant_id,
            agent_key=request.agent_key,
            actor_role=request.actor_role,
            client_has_entitlement=request.client_has_entitlement,
            owner_approved=request.owner_approved,
            live_external_requested=request.live_external_requested,
            live_external_enabled=request.live_external_enabled,
            customer_safe=request.customer_safe,
            metadata=request.metadata,
        )
    )

    queue_adapter = adapter or create_queue_adapter()
    telemetry = export_queue_health_dict(
        build_queue_health_snapshot(
            adapter=queue_adapter,
            worker_count=0,
            active_workers=0,
        )
    )

    return WorkerPlan(
        created_at=datetime.now(timezone.utc).isoformat(),
        admitted=admission.admitted,
        queue_target=admission.queue_target,
        workload_group=admission.workload_group,
        planned_only=True,
        would_enqueue=admission.admitted,
        would_execute_now=False,
        blocked_reasons=list(admission.blocked_reasons),
        reasons=list(admission.reasons),
        telemetry=telemetry,
        governance={
            "owner_approval_required": admission.requires_owner_approval,
            "live_external_allowed": admission.live_external_allowed,
            "customer_safe": admission.customer_safe,
            "live_runtime_changed": False,
            "jobs_executed": False,
            "redis_connection_required": False,
        },
    )


def export_worker_plan(plan: WorkerPlan) -> Dict[str, Any]:
    return {
        "created_at": plan.created_at,
        "admitted": plan.admitted,
        "queue_target": plan.queue_target,
        "workload_group": plan.workload_group,
        "planned_only": plan.planned_only,
        "would_enqueue": plan.would_enqueue,
        "would_execute_now": plan.would_execute_now,
        "blocked_reasons": plan.blocked_reasons,
        "reasons": plan.reasons,
        "telemetry": plan.telemetry,
        "governance": plan.governance,
    }


def worker_orchestration_executes_jobs() -> bool:
    return False


def worker_orchestration_changes_live_routes() -> bool:
    return False


def worker_orchestration_requires_redis() -> bool:
    return False
