"""
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
