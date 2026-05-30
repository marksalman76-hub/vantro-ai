from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"queue_isolation_foundation_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

QUEUE_FILE = ROOT / "backend" / "app" / "runtime" / "queue_isolation_policy.py"
TEST_FILE = ROOT / "test_queue_isolation_policy.py"
DOC_FILE = ROOT / "docs" / "queue-isolation-redis-migration-plan.md"

QUEUE_POLICY = r'''"""
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
'''

TEST_POLICY = r'''from backend.app.runtime.queue_isolation_policy import (
    classify_workload,
    get_queue_policy,
    export_queue_isolation_snapshot,
    redis_activation_required,
    live_external_execution_enabled_by_default,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    cases = {
        "run_agent": "client_agent_execution",
        "openai_live_generation": "provider_generation",
        "crm_task_created": "external_integration_action",
        "email_draft_created": "external_integration_action",
        "calendar_event_created": "external_integration_action",
        "weekly_report": "reporting",
        "dead_letter_retry": "retry_reconciliation",
        "admin_audit": "admin_internal",
    }

    for action, expected in cases.items():
        assert_equal(classify_workload(action), expected, action)

    provider = get_queue_policy("openai_live_generation")
    assert_equal(provider.requires_owner_approval, True, "provider owner approval")
    assert_equal(provider.live_external_safe_default, False, "provider live default disabled")

    integration = get_queue_policy("crm_task_created")
    assert_equal(integration.requires_owner_approval, True, "integration owner approval")
    assert_equal(integration.live_external_safe_default, False, "integration live default disabled")

    client = get_queue_policy("run_agent")
    assert_equal(client.requires_owner_approval, False, "client normal execution approval")
    assert_equal(client.live_external_safe_default, True, "client normal execution safe")

    assert_equal(redis_activation_required(), True, "redis activation required")
    assert_equal(live_external_execution_enabled_by_default(), False, "live external default")

    snapshot = export_queue_isolation_snapshot()
    required = [
        "client_agent_execution",
        "provider_generation",
        "external_integration_action",
        "reporting",
        "retry_reconciliation",
        "admin_internal",
    ]
    missing = [key for key in required if key not in snapshot]
    if missing:
        raise AssertionError(f"Missing queue policies: {missing}")

    print("QUEUE_ISOLATION_POLICY_TEST_PASSED")
    print("Queue groups:", ", ".join(sorted(snapshot.keys())))


if __name__ == "__main__":
    main()
'''

DOC = """# Queue Isolation + Redis Migration Plan

## Purpose

Separate fast web/API requests from long-running provider, integration, retry, reporting, and reconciliation workloads.

## Current foundation

This foundation is policy-only. It does not connect to Redis and does not change live runtime behaviour.

## Target queues

- client_agent_execution_queue
- provider_generation_queue
- external_integration_action_queue
- reporting_queue
- retry_reconciliation_queue
- admin_internal_queue

## Safety rules

- Provider generation remains owner-approved.
- Live external calls remain disabled by default.
- CRM/email/calendar/store actions require governance before live execution.
- Client entitlement checks must remain before queue admission.
- Owner/admin bypass applies only to client/package limits, not audit or high-risk governance.

## Redis migration stages

1. Add managed Redis connection settings.
2. Add queue adapter abstraction.
3. Keep in-memory/local queue as fallback for development.
4. Add Redis-backed enqueue/dequeue implementation.
5. Add dedicated worker process.
6. Add retry and dead-letter handling.
7. Add queue depth and worker health telemetry.
8. Add admin visibility before scaling live workload volume.

## Do not activate automatically

Do not enable live external provider calls, budgeted actions, autonomous scaling, or spending based only on queue installation.
"""

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def write(path: Path, content: str):
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    write(QUEUE_FILE, QUEUE_POLICY)
    write(TEST_FILE, TEST_POLICY)
    write(DOC_FILE, DOC)

    print("QUEUE_ISOLATION_FOUNDATION_INSTALLED")
    print("Backup folder:", BACKUP)
    print("Created/updated:")
    print("-", QUEUE_FILE)
    print("-", TEST_FILE)
    print("-", DOC_FILE)
    print("Safety:")
    print("- Policy-only foundation")
    print("- No Redis connection made")
    print("- No live queue execution changed")
    print("- Live external execution remains disabled by default")


if __name__ == "__main__":
    main()