from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"worker_orchestration_runtime_foundation_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

WORKER_FILE = ROOT / "backend" / "app" / "runtime" / "worker_orchestration_runtime.py"
TEST_FILE = ROOT / "test_worker_orchestration_runtime.py"

WORKER_RUNTIME = r'''"""
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
'''

TEST = r'''from backend.app.runtime.queue_adapter import InMemoryQueueAdapter
from backend.app.runtime.worker_orchestration_runtime import (
    WorkerPlanRequest,
    build_worker_plan,
    export_worker_plan,
    worker_orchestration_executes_jobs,
    worker_orchestration_changes_live_routes,
    worker_orchestration_requires_redis,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    adapter = InMemoryQueueAdapter()

    client_plan = export_worker_plan(
        build_worker_plan(
            WorkerPlanRequest(
                action_type="run_agent",
                tenant_id="tenant_1",
                agent_key="seo_agent",
                actor_role="client",
                client_has_entitlement=True,
                payload={"prompt": "test"},
            ),
            adapter=adapter,
        )
    )

    assert_equal(client_plan["admitted"], True, "client admitted")
    assert_equal(client_plan["queue_target"], "client_agent_execution_queue", "client queue")
    assert_equal(client_plan["planned_only"], True, "planned only")
    assert_equal(client_plan["would_enqueue"], True, "would enqueue")
    assert_equal(client_plan["would_execute_now"], False, "does not execute now")
    assert_equal(client_plan["governance"]["jobs_executed"], False, "jobs not executed")

    blocked_provider = export_worker_plan(
        build_worker_plan(
            WorkerPlanRequest(
                action_type="openai_live_generation",
                tenant_id="tenant_1",
                agent_key="product_image_agent",
                actor_role="client",
                client_has_entitlement=True,
                live_external_requested=True,
                live_external_enabled=False,
                owner_approved=False,
            ),
            adapter=adapter,
        )
    )

    assert_equal(blocked_provider["admitted"], False, "blocked provider")
    if "owner_approval_required" not in blocked_provider["blocked_reasons"]:
        raise AssertionError("Missing owner approval block")
    if "live_external_execution_disabled" not in blocked_provider["blocked_reasons"]:
        raise AssertionError("Missing live external disabled block")

    approved_provider = export_worker_plan(
        build_worker_plan(
            WorkerPlanRequest(
                action_type="openai_live_generation",
                tenant_id="tenant_1",
                agent_key="product_image_agent",
                actor_role="client",
                client_has_entitlement=True,
                live_external_requested=True,
                live_external_enabled=True,
                owner_approved=True,
            ),
            adapter=adapter,
        )
    )

    assert_equal(approved_provider["admitted"], True, "approved provider")
    assert_equal(approved_provider["queue_target"], "provider_generation_queue", "provider queue")
    assert_equal(approved_provider["governance"]["live_external_allowed"], True, "live external allowed after approval")
    assert_equal(approved_provider["would_execute_now"], False, "approved still does not execute now")

    owner_admin_plan = export_worker_plan(
        build_worker_plan(
            WorkerPlanRequest(
                action_type="admin_audit",
                actor_role="owner_admin",
                client_has_entitlement=False,
            ),
            adapter=adapter,
        )
    )

    assert_equal(owner_admin_plan["admitted"], True, "owner admin admitted")
    assert_equal(owner_admin_plan["queue_target"], "admin_internal_queue", "admin queue")
    if "client_entitlement_bypass_allowed_for_owner_admin" not in owner_admin_plan["reasons"]:
        raise AssertionError("Missing owner/admin bypass reason")

    assert_equal(worker_orchestration_executes_jobs(), False, "worker does not execute")
    assert_equal(worker_orchestration_changes_live_routes(), False, "routes unchanged")
    assert_equal(worker_orchestration_requires_redis(), False, "redis not required")

    print("WORKER_ORCHESTRATION_RUNTIME_TEST_PASSED")


if __name__ == "__main__":
    main()
'''

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def write(path: Path, content: str):
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    write(WORKER_FILE, WORKER_RUNTIME)
    write(TEST_FILE, TEST)

    print("WORKER_ORCHESTRATION_RUNTIME_FOUNDATION_INSTALLED")
    print("Backup folder:", BACKUP)
    print("Created/updated:")
    print("-", WORKER_FILE)
    print("-", TEST_FILE)
    print("Safety:")
    print("- Planning/visibility only")
    print("- No jobs executed")
    print("- No Redis required")
    print("- No live route behaviour changed")


if __name__ == "__main__":
    main()