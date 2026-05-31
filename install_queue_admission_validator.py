from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"queue_admission_validator_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

VALIDATOR_FILE = ROOT / "backend" / "app" / "runtime" / "queue_admission_validator.py"
TEST_FILE = ROOT / "test_queue_admission_validator.py"

VALIDATOR = r'''"""
Queue admission validator.

Policy-only admission gate for future queue insertion.

This module does not enqueue jobs, connect to Redis, call providers, perform
external actions, or change live route behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from backend.app.runtime.queue_isolation_policy import get_queue_policy


@dataclass(frozen=True)
class QueueAdmissionRequest:
    action_type: str
    tenant_id: str = ""
    agent_key: str = ""
    actor_role: str = "client"
    client_has_entitlement: bool = False
    owner_approved: bool = False
    live_external_requested: bool = False
    live_external_enabled: bool = False
    customer_safe: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QueueAdmissionDecision:
    admitted: bool
    queue_target: str
    workload_group: str
    reasons: List[str]
    blocked_reasons: List[str]
    requires_owner_approval: bool
    live_external_allowed: bool
    customer_safe: bool


OWNER_ADMIN_ROLES = {"owner", "admin", "owner_admin", "super_admin"}


def is_owner_admin(actor_role: str) -> bool:
    return (actor_role or "").lower() in OWNER_ADMIN_ROLES


def evaluate_queue_admission(request: QueueAdmissionRequest) -> QueueAdmissionDecision:
    policy = get_queue_policy(request.action_type)

    reasons: List[str] = []
    blocked: List[str] = []

    actor_is_owner_admin = is_owner_admin(request.actor_role)

    if actor_is_owner_admin:
        reasons.append("owner_admin_actor_detected")

    if not request.customer_safe:
        blocked.append("customer_safe_false")

    if policy.requires_owner_approval and not request.owner_approved:
        blocked.append("owner_approval_required")

    if request.live_external_requested:
        if not request.live_external_enabled:
            blocked.append("live_external_execution_disabled")
        if not request.owner_approved:
            blocked.append("live_external_owner_approval_missing")
        if policy.live_external_safe_default is False:
            reasons.append("live_external_safe_default_false")

    if not actor_is_owner_admin:
        if not request.client_has_entitlement:
            blocked.append("client_entitlement_missing")
    else:
        reasons.append("client_entitlement_bypass_allowed_for_owner_admin")

    if not request.tenant_id and not actor_is_owner_admin:
        blocked.append("tenant_id_missing")

    if request.agent_key:
        reasons.append("agent_key_present")
    else:
        reasons.append("agent_key_missing")

    admitted = len(blocked) == 0

    if admitted:
        reasons.append("queue_admission_allowed")
    else:
        reasons.append("queue_admission_blocked")

    return QueueAdmissionDecision(
        admitted=admitted,
        queue_target=policy.queue_target,
        workload_group=policy.workload_group,
        reasons=reasons,
        blocked_reasons=blocked,
        requires_owner_approval=policy.requires_owner_approval,
        live_external_allowed=bool(
            request.live_external_requested
            and request.live_external_enabled
            and request.owner_approved
            and len(blocked) == 0
        ),
        customer_safe=request.customer_safe,
    )


def queue_admission_changes_live_runtime() -> bool:
    return False


def queue_admission_enqueues_jobs() -> bool:
    return False
'''

TEST = r'''from backend.app.runtime.queue_admission_validator import (
    QueueAdmissionRequest,
    evaluate_queue_admission,
    queue_admission_changes_live_runtime,
    queue_admission_enqueues_jobs,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    client_ok = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="run_agent",
            tenant_id="tenant_1",
            agent_key="seo_agent",
            actor_role="client",
            client_has_entitlement=True,
            customer_safe=True,
        )
    )
    assert_equal(client_ok.admitted, True, "entitled client admitted")
    assert_equal(client_ok.queue_target, "client_agent_execution_queue", "client queue target")

    client_no_entitlement = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="run_agent",
            tenant_id="tenant_1",
            agent_key="seo_agent",
            actor_role="client",
            client_has_entitlement=False,
        )
    )
    assert_equal(client_no_entitlement.admitted, False, "client no entitlement blocked")
    if "client_entitlement_missing" not in client_no_entitlement.blocked_reasons:
        raise AssertionError("Missing entitlement block reason")

    provider_no_approval = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="openai_live_generation",
            tenant_id="tenant_1",
            agent_key="product_image_agent",
            actor_role="client",
            client_has_entitlement=True,
            live_external_requested=True,
            live_external_enabled=True,
            owner_approved=False,
        )
    )
    assert_equal(provider_no_approval.admitted, False, "provider no approval blocked")
    if "owner_approval_required" not in provider_no_approval.blocked_reasons:
        raise AssertionError("Missing owner approval block")

    provider_approved = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="openai_live_generation",
            tenant_id="tenant_1",
            agent_key="product_image_agent",
            actor_role="client",
            client_has_entitlement=True,
            live_external_requested=True,
            live_external_enabled=True,
            owner_approved=True,
        )
    )
    assert_equal(provider_approved.admitted, True, "approved provider admitted")
    assert_equal(provider_approved.live_external_allowed, True, "approved live external allowed")
    assert_equal(provider_approved.queue_target, "provider_generation_queue", "provider queue target")

    owner_admin = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="admin_audit",
            actor_role="owner_admin",
            client_has_entitlement=False,
            customer_safe=True,
        )
    )
    assert_equal(owner_admin.admitted, True, "owner admin bypasses client entitlement")
    if "client_entitlement_bypass_allowed_for_owner_admin" not in owner_admin.reasons:
        raise AssertionError("Owner/admin bypass reason missing")

    unsafe = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="run_agent",
            tenant_id="tenant_1",
            actor_role="client",
            client_has_entitlement=True,
            customer_safe=False,
        )
    )
    assert_equal(unsafe.admitted, False, "customer unsafe blocked")
    if "customer_safe_false" not in unsafe.blocked_reasons:
        raise AssertionError("Missing customer safety block")

    assert_equal(queue_admission_changes_live_runtime(), False, "live runtime unchanged")
    assert_equal(queue_admission_enqueues_jobs(), False, "does not enqueue jobs")

    print("QUEUE_ADMISSION_VALIDATOR_TEST_PASSED")


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
    write(VALIDATOR_FILE, VALIDATOR)
    write(TEST_FILE, TEST)

    print("QUEUE_ADMISSION_VALIDATOR_INSTALLED")
    print("Backup folder:", BACKUP)
    print("Created/updated:")
    print("-", VALIDATOR_FILE)
    print("-", TEST_FILE)
    print("Safety:")
    print("- Policy/admission only")
    print("- No Redis connection")
    print("- No enqueue/dequeue")
    print("- No live route behaviour changed")
    print("- Owner/admin entitlement bypass preserved without bypassing governance")


if __name__ == "__main__":
    main()