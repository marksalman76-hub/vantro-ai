"""
Queue isolation policy foundation.

This module classifies execution workloads and defines the intended queue/process
target. It is policy-only and does not enqueue, dequeue, call Redis, or execute
external provider actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class QueueIsolationPolicy:
    workload_group: str
    queue_target: str
    requires_owner_approval: bool
    live_external_safe_default: bool
    max_attempts: int
    notes: str


POLICIES: Dict[str, QueueIsolationPolicy] = {
    "client_agent_execution": QueueIsolationPolicy(
        workload_group="client_agent_execution",
        queue_target="client_agent_execution_queue",
        requires_owner_approval=False,
        live_external_safe_default=True,
        max_attempts=3,
        notes="Client-owned agent execution may be queued while preserving entitlement checks.",
    ),
    "provider_generation": QueueIsolationPolicy(
        workload_group="provider_generation",
        queue_target="provider_generation_queue",
        requires_owner_approval=True,
        live_external_safe_default=False,
        max_attempts=2,
        notes="Live provider generation must remain owner-approved and disabled by default.",
    ),
    "external_integration_action": QueueIsolationPolicy(
        workload_group="external_integration_action",
        queue_target="external_integration_action_queue",
        requires_owner_approval=True,
        live_external_safe_default=False,
        max_attempts=2,
        notes="CRM/email/calendar/store actions should be isolated from web requests.",
    ),
    "reporting": QueueIsolationPolicy(
        workload_group="reporting",
        queue_target="reporting_queue",
        requires_owner_approval=False,
        live_external_safe_default=True,
        max_attempts=3,
        notes="Weekly reports and analytics can run in background workers.",
    ),
    "retry_reconciliation": QueueIsolationPolicy(
        workload_group="retry_reconciliation",
        queue_target="retry_reconciliation_queue",
        requires_owner_approval=False,
        live_external_safe_default=True,
        max_attempts=5,
        notes="Retries and reconciliation should be worker-owned and idempotent.",
    ),
    "admin_internal": QueueIsolationPolicy(
        workload_group="admin_internal",
        queue_target="admin_internal_queue",
        requires_owner_approval=False,
        live_external_safe_default=True,
        max_attempts=1,
        notes="Owner/admin diagnostics may bypass client limits but remain audited.",
    ),
}


def classify_workload(action_type: str) -> str:
    value = (action_type or "").lower()

    if any(token in value for token in ["provider", "openai", "image_generation", "video_generation", "live_generation"]):
        return "provider_generation"

    if any(token in value for token in ["crm", "email", "calendar", "store", "integration", "external_action"]):
        return "external_integration_action"

    if any(token in value for token in ["weekly_report", "analytics", "reporting", "summary"]):
        return "reporting"

    if any(token in value for token in ["retry", "reconcile", "dead_letter", "dlq"]):
        return "retry_reconciliation"

    if any(token in value for token in ["admin", "owner", "diagnostic", "audit"]):
        return "admin_internal"

    return "client_agent_execution"


def get_queue_policy(action_type: str) -> QueueIsolationPolicy:
    return POLICIES[classify_workload(action_type)]


def export_queue_isolation_snapshot() -> dict:
    return {
        key: {
            "workload_group": policy.workload_group,
            "queue_target": policy.queue_target,
            "requires_owner_approval": policy.requires_owner_approval,
            "live_external_safe_default": policy.live_external_safe_default,
            "max_attempts": policy.max_attempts,
            "notes": policy.notes,
        }
        for key, policy in POLICIES.items()
    }


def redis_activation_required() -> bool:
    return True


def live_external_execution_enabled_by_default() -> bool:
    return False
