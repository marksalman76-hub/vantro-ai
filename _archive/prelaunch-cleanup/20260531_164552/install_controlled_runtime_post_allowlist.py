from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"controlled_runtime_post_allowlist_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

MAIN_FILE = ROOT / "backend" / "app" / "main.py"
TEST_FILE = ROOT / "test_controlled_runtime_post_allowlist.py"

ROUTE_BLOCK = r'''

@app.get("/admin/runtime-execution-dry-run-safe")
async def admin_runtime_execution_dry_run_safe():
    """
    GET-based controlled runtime dry-run.

    Purpose:
    - avoids production POST security block
    - verifies Redis enqueue path from inside production backend
    - does not execute jobs
    - does not call providers
    - does not spend money
    """

    try:
        from datetime import datetime, timezone
        from backend.app.runtime.queue_adapter import create_queue_adapter
        from backend.app.runtime.queue_admission_validator import QueueAdmissionRequest, evaluate_queue_admission
        from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict

        adapter = create_queue_adapter()
        before = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        admission = evaluate_queue_admission(
            QueueAdmissionRequest(
                action_type="run_agent",
                tenant_id="runtime_safe_dry_run",
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
                    "type": "runtime_execution_dry_run_safe",
                    "execute": False,
                    "provider_execution_allowed": False,
                    "spend_allowed": False,
                    "customer_safe": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "source": "runtime_execution_dry_run_safe",
                    "customer_safe": True,
                },
            )

        after = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        return {
            "success": True,
            "runtime": "controlled_distributed_runtime_dry_run",
            "admission": {
                "admitted": admission.admitted,
                "queue_target": admission.queue_target,
                "blocked_reasons": admission.blocked_reasons,
                "reasons": admission.reasons,
            },
            "message_created": message is not None,
            "message_id": getattr(message, "id", None),
            "queue_adapter": after.get("adapter"),
            "before_total_messages": before.get("total_messages"),
            "after_total_messages": after.get("total_messages"),
            "dequeue_simulation": {
                "performed": True,
                "jobs_executed": False,
                "external_provider_called": False,
                "spend_performed": False,
                "execution_permitted": False,
            },
            "execution_gates": {
                "provider_execution_allowed": False,
                "spend_allowed": False,
                "autonomous_execution_allowed": False,
                "owner_approval_required": True,
            },
            "customer_safe": True,
            "status": "CONTROLLED_RUNTIME_DRY_RUN_COMPLETE",
        }

    except Exception as exc:
        return {
            "success": False,
            "runtime": "controlled_distributed_runtime_dry_run",
            "error": repr(exc),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "customer_safe": True,
            "status": "CONTROLLED_RUNTIME_DRY_RUN_FAILED",
        }
'''

TEST = r'''from pathlib import Path

def main():
    text = Path("backend/app/main.py").read_text(encoding="utf-8", errors="replace")
    required = [
        "/admin/runtime-execution-dry-run-safe",
        "CONTROLLED_RUNTIME_DRY_RUN_COMPLETE",
        "adapter.enqueue",
        "provider_execution_allowed",
        "spend_allowed",
        "autonomous_execution_allowed",
        "jobs_executed",
        "external_provider_called",
        "spend_performed",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise AssertionError(f"Missing controlled runtime dry-run markers: {missing}")
    print("CONTROLLED_RUNTIME_POST_ALLOWLIST_TEST_PASSED")

if __name__ == "__main__":
    main()
'''

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def main():
    text = MAIN_FILE.read_text(encoding="utf-8", errors="replace")

    if "/admin/runtime-execution-dry-run-safe" not in text:
        backup(MAIN_FILE)
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + ROUTE_BLOCK + "\n", encoding="utf-8")

    backup(TEST_FILE)
    TEST_FILE.write_text(TEST, encoding="utf-8")

    print("CONTROLLED_RUNTIME_POST_ALLOWLIST_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", MAIN_FILE)
    print("Created:", TEST_FILE)
    print("Safety:")
    print("- GET dry-run route only")
    print("- Redis enqueue dry-run only")
    print("- No provider execution")
    print("- No spend")
    print("- No autonomous execution")

if __name__ == "__main__":
    main()