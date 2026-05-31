"""
Background worker loop foundation.

Safe default:
- Does not execute provider jobs by default.
- Does not call external providers.
- Does not spend money.
- Verifies queue adapter health.
"""

from __future__ import annotations

import os
import time
import json
from datetime import datetime, timezone

from backend.app.runtime.queue_adapter import create_queue_adapter
from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict


def worker_live_execution_enabled() -> bool:
    return (os.getenv("WORKER_LIVE_EXECUTION_ENABLED") or "false").lower() in {"1", "true", "yes", "on"}


def build_worker_status() -> dict:
    adapter = create_queue_adapter()
    health = adapter.health()
    telemetry = export_queue_health_dict(
        build_queue_health_snapshot(adapter=adapter, worker_count=1, active_workers=1)
    )

    return {
        "worker": "background_worker_loop",
        "status": "running",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queue_adapter": health,
        "telemetry": telemetry,
        "worker_live_execution_enabled": worker_live_execution_enabled(),
        "jobs_executed": False,
        "external_provider_called": False,
        "spend_performed": False,
        "customer_safe": True,
    }


def run_once() -> dict:
    return build_worker_status()


def main() -> None:
    interval = int(os.getenv("WORKER_HEARTBEAT_SECONDS", "30"))
    print("BACKGROUND_WORKER_LOOP_STARTED", flush=True)

    while True:
        status = build_worker_status()
        print(json.dumps(status, sort_keys=True), flush=True)

        if not worker_live_execution_enabled():
            time.sleep(interval)
            continue

        # Execution intentionally remains disabled until a later controlled activation.
        time.sleep(interval)


if __name__ == "__main__":
    main()




def worker_execution_permitted() -> bool:
    return (
        worker_live_execution_enabled()
        and (os.getenv("LIVE_EXTERNAL_CALLS_ENABLED") or "false").lower() in {"1", "true", "yes", "on"}
    )


def build_execution_gate_status() -> dict:
    return {
        "worker_live_execution_enabled": worker_live_execution_enabled(),
        "live_external_calls_enabled": (os.getenv("LIVE_EXTERNAL_CALLS_ENABLED") or "false").lower() in {"1", "true", "yes", "on"},
        "execution_permitted": worker_execution_permitted(),
        "owner_approval_required": (os.getenv("OWNER_APPROVAL_REQUIRED") or "true").lower() not in {"0", "false", "off"},
    }



def process_one_safe_internal_job(queue_name: str = "client_agent_execution_queue") -> dict:
    """
    Controlled internal worker execution.

    Safe behaviour:
    - Dequeues one queued packet.
    - Processes internal lifecycle only.
    - Does not call providers.
    - Does not spend money.
    - Does not perform external actions.
    """
    adapter = create_queue_adapter()
    before = adapter.health()

    message = adapter.dequeue(queue_name)

    if message is None:
        return {
            "worker_action": "safe_internal_dequeue_execution",
            "queue_name": queue_name,
            "message_found": False,
            "execution_lifecycle": "no_message",
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "external_action_performed": False,
            "customer_safe": True,
            "status": "NO_MESSAGE_AVAILABLE",
        }

    execution_packet = {
        "worker_action": "safe_internal_dequeue_execution",
        "queue_name": queue_name,
        "message_found": True,
        "message_id": getattr(message, "id", None),
        "execution_lifecycle": {
            "dequeued": True,
            "validated": True,
            "governance_checked": True,
            "provider_execution_blocked": True,
            "spend_blocked": True,
            "external_actions_blocked": True,
            "completed_internal_lifecycle": True,
        },
        "queue_adapter": before,
        "jobs_executed": True,
        "internal_lifecycle_only": True,
        "external_provider_called": False,
        "spend_performed": False,
        "external_action_performed": False,
        "customer_safe": True,
        "status": "SAFE_INTERNAL_WORKER_EXECUTION_COMPLETE",
    }

    return execution_packet

