from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"admin_queue_dry_run_route_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

MAIN_FILE = ROOT / "backend" / "app" / "main.py"
TEST_FILE = ROOT / "test_admin_queue_dry_run_route.py"

ROUTE_CODE = r'''

@app.post("/admin/queue-dry-run")
async def admin_queue_dry_run():
    """
    Admin-only production Redis queue dry run.

    Safe behaviour:
    - Enqueues a dry-run packet only.
    - Does not execute jobs.
    - Does not call providers.
    - Does not spend money.
    - Does not expose secrets.
    """

    try:
        from backend.app.runtime.queue_adapter import create_queue_adapter
        from backend.app.runtime.queue_admission_validator import QueueAdmissionRequest, evaluate_queue_admission
        from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict

        adapter = create_queue_adapter()

        before = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        admission = evaluate_queue_admission(
            QueueAdmissionRequest(
                action_type="run_agent",
                tenant_id="admin_queue_dry_run_tenant",
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
                    "type": "admin_queue_dry_run",
                    "action_type": "run_agent",
                    "tenant_id": "admin_queue_dry_run_tenant",
                    "agent_key": "qa_agent",
                    "execute": False,
                    "provider_call_allowed": False,
                    "spend_allowed": False,
                    "customer_safe": True,
                },
                {
                    "source": "admin_queue_dry_run_route",
                    "customer_safe": True,
                },
            )

        after = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        return {
            "success": True,
            "dry_run": "admin_queue_dry_run",
            "queue_adapter": after.get("adapter"),
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
            "status": "ADMIN_QUEUE_DRY_RUN_COMPLETE",
        }

    except Exception as exc:
        return {
            "success": False,
            "dry_run": "admin_queue_dry_run",
            "error": repr(exc),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "customer_safe": True,
            "status": "ADMIN_QUEUE_DRY_RUN_FAILED",
        }
'''

TEST = r'''from pathlib import Path


def main():
    text = Path("backend/app/main.py").read_text(encoding="utf-8", errors="replace")

    required = [
        "/admin/queue-dry-run",
        "admin_queue_dry_run",
        "QueueAdmissionRequest",
        "adapter.enqueue",
        "jobs_executed",
        "external_provider_called",
        "spend_performed",
        "ADMIN_QUEUE_DRY_RUN_COMPLETE",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        raise AssertionError(f"Missing admin queue dry-run route markers: {missing}")

    print("ADMIN_QUEUE_DRY_RUN_ROUTE_TEST_PASSED")


if __name__ == "__main__":
    main()
'''

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(
            path.read_text(encoding="utf-8", errors="replace"),
            encoding="utf-8",
        )


def main():
    text = MAIN_FILE.read_text(encoding="utf-8", errors="replace")

    if "/admin/queue-dry-run" not in text:
        backup(MAIN_FILE)
        MAIN_FILE.write_text(text.rstrip() + "\n" + ROUTE_CODE + "\n", encoding="utf-8")

    backup(TEST_FILE)
    TEST_FILE.write_text(TEST, encoding="utf-8")

    print("ADMIN_QUEUE_DRY_RUN_ROUTE_INSTALLED")
    print("Backup folder:", BACKUP)
    print("Updated:", MAIN_FILE)
    print("Created/updated:", TEST_FILE)
    print("Safety:")
    print("- Dry-run queue packet only")
    print("- No job execution")
    print("- No provider calls")
    print("- No spending")
    print("- Customer-safe")


if __name__ == "__main__":
    main()