import json
from pathlib import Path
from backend.app.runtime.queue_adapter import create_queue_adapter
from backend.app.runtime.queue_admission_validator import QueueAdmissionRequest, evaluate_queue_admission
from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict

def main():
    adapter = create_queue_adapter()
    before = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

    admission = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="run_agent",
            tenant_id="dry_run_tenant",
            agent_key="qa_agent",
            actor_role="owner_admin",
            client_has_entitlement=False,
            customer_safe=True,
        )
    )

    message = None
    if admission.admitted:
        message = adapter.enqueue(
            admission.queue_target,
            {
                "type": "dry_run",
                "action_type": "run_agent",
                "tenant_id": "dry_run_tenant",
                "agent_key": "qa_agent",
                "execute": False,
                "provider_call_allowed": False,
            },
            {
                "source": "queue_execution_dry_run",
                "customer_safe": True,
            },
        )

    after = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

    report = {
        "dry_run": "queue_execution",
        "adapter": after.get("adapter"),
        "admission": {
            "admitted": admission.admitted,
            "queue_target": admission.queue_target,
            "blocked_reasons": admission.blocked_reasons,
            "reasons": admission.reasons,
        },
        "message_created": message is not None,
        "message_id": getattr(message, "id", None),
        "before_total_messages": before.get("total_messages"),
        "after_total_messages": after.get("total_messages"),
        "jobs_executed": False,
        "external_provider_called": False,
        "spend_performed": False,
        "customer_safe": True,
        "status": "QUEUE_EXECUTION_DRY_RUN_COMPLETE",
    }

    Path("queue_execution_dry_run_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("QUEUE_EXECUTION_DRY_RUN_COMPLETE")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
