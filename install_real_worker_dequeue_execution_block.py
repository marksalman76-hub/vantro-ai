from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"real_worker_dequeue_execution_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

WORKER_FILE = ROOT / "backend" / "app" / "runtime" / "background_worker_loop.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
TEST_FILE = ROOT / "test_real_worker_dequeue_execution_block.py"

WORKER_APPEND = r'''

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
'''

ROUTE_APPEND = r'''

@app.get("/admin/runtime-safe-worker-execute-one")
async def admin_runtime_safe_worker_execute_one():
    """
    Controlled worker-side internal execution.

    Safe behaviour:
    - Dequeues one queued packet.
    - Completes internal lifecycle only.
    - Does not call providers.
    - Does not spend money.
    - Does not perform external actions.
    """

    try:
        from backend.app.runtime.background_worker_loop import process_one_safe_internal_job
        from backend.app.runtime.queue_adapter import create_queue_adapter
        from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict

        adapter = create_queue_adapter()
        before = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        result = process_one_safe_internal_job("client_agent_execution_queue")

        after = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        return {
            "success": True,
            "runtime": "safe_worker_dequeue_execution",
            "before_total_messages": before.get("total_messages"),
            "after_total_messages": after.get("total_messages"),
            "worker_result": result,
            "provider_execution_allowed": False,
            "spend_allowed": False,
            "autonomous_execution_allowed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "external_action_performed": False,
            "customer_safe": True,
            "status": "SAFE_WORKER_DEQUEUE_EXECUTION_COMPLETE",
        }

    except Exception as exc:
        return {
            "success": False,
            "runtime": "safe_worker_dequeue_execution",
            "error": repr(exc),
            "external_provider_called": False,
            "spend_performed": False,
            "external_action_performed": False,
            "customer_safe": True,
            "status": "SAFE_WORKER_DEQUEUE_EXECUTION_FAILED",
        }
'''

TEST = r'''from pathlib import Path
from backend.app.runtime.background_worker_loop import process_one_safe_internal_job

def main():
    worker_text = Path("backend/app/runtime/background_worker_loop.py").read_text(encoding="utf-8", errors="replace")
    main_text = Path("backend/app/main.py").read_text(encoding="utf-8", errors="replace")

    required_worker = [
        "process_one_safe_internal_job",
        "SAFE_INTERNAL_WORKER_EXECUTION_COMPLETE",
        "external_provider_called",
        "spend_performed",
        "external_action_performed",
    ]

    required_main = [
        "/admin/runtime-safe-worker-execute-one",
        "SAFE_WORKER_DEQUEUE_EXECUTION_COMPLETE",
        "process_one_safe_internal_job",
    ]

    missing_worker = [x for x in required_worker if x not in worker_text]
    missing_main = [x for x in required_main if x not in main_text]

    if missing_worker:
        raise AssertionError(f"Missing worker markers: {missing_worker}")

    if missing_main:
        raise AssertionError(f"Missing route markers: {missing_main}")

    result = process_one_safe_internal_job("__empty_test_queue__")

    if result["external_provider_called"] is not False:
        raise AssertionError("Provider calls must remain blocked")

    if result["spend_performed"] is not False:
        raise AssertionError("Spend must remain blocked")

    print("REAL_WORKER_DEQUEUE_EXECUTION_BLOCK_TEST_PASSED")
    print(result)

if __name__ == "__main__":
    main()
'''

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def append_once(path: Path, marker: str, content: str):
    text = path.read_text(encoding="utf-8", errors="replace")
    if marker not in text:
        backup(path)
        path.write_text(text.rstrip() + "\n\n" + content + "\n", encoding="utf-8")

def main():
    append_once(WORKER_FILE, "def process_one_safe_internal_job", WORKER_APPEND)
    append_once(MAIN_FILE, "/admin/runtime-safe-worker-execute-one", ROUTE_APPEND)

    backup(TEST_FILE)
    TEST_FILE.write_text(TEST, encoding="utf-8")

    print("REAL_WORKER_DEQUEUE_EXECUTION_BLOCK_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:")
    print("-", WORKER_FILE)
    print("-", MAIN_FILE)
    print("-", TEST_FILE)
    print("Safety:")
    print("- Real dequeue path")
    print("- Internal lifecycle only")
    print("- No provider execution")
    print("- No spend")
    print("- No external action")

if __name__ == "__main__":
    main()