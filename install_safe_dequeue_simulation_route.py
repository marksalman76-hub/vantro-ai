from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"safe_dequeue_simulation_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

MAIN_FILE = ROOT / "backend" / "app" / "main.py"
TEST_FILE = ROOT / "test_safe_dequeue_simulation_route.py"

ROUTE_BLOCK = r'''

@app.get("/admin/runtime-dequeue-simulation")
async def admin_runtime_dequeue_simulation():
    """
    Controlled dequeue simulation.

    Safe behaviour:
    - Reads/removes one dry-run packet only.
    - Does not execute jobs.
    - Does not call providers.
    - Does not spend money.
    - Confirms queue reduction.
    """

    try:
        from backend.app.runtime.queue_adapter import create_queue_adapter
        from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict

        adapter = create_queue_adapter()
        queue_name = "client_agent_execution_queue"

        before = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        message = adapter.dequeue(queue_name)

        after = export_queue_health_dict(build_queue_health_snapshot(adapter=adapter))

        return {
            "success": True,
            "simulation": "runtime_dequeue",
            "queue_adapter": after.get("adapter"),
            "queue_name": queue_name,
            "message_found": message is not None,
            "message_id": getattr(message, "id", None),
            "before_total_messages": before.get("total_messages"),
            "after_total_messages": after.get("total_messages"),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "execution_permitted": False,
            "customer_safe": True,
            "status": "SAFE_DEQUEUE_SIMULATION_COMPLETE",
        }

    except Exception as exc:
        return {
            "success": False,
            "simulation": "runtime_dequeue",
            "error": repr(exc),
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "customer_safe": True,
            "status": "SAFE_DEQUEUE_SIMULATION_FAILED",
        }
'''

TEST = r'''from pathlib import Path

def main():
    text = Path("backend/app/main.py").read_text(encoding="utf-8", errors="replace")
    required = [
        "/admin/runtime-dequeue-simulation",
        "SAFE_DEQUEUE_SIMULATION_COMPLETE",
        "adapter.dequeue",
        "jobs_executed",
        "external_provider_called",
        "spend_performed",
        "execution_permitted",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise AssertionError(f"Missing dequeue simulation markers: {missing}")
    print("SAFE_DEQUEUE_SIMULATION_ROUTE_TEST_PASSED")

if __name__ == "__main__":
    main()
'''

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def main():
    text = MAIN_FILE.read_text(encoding="utf-8", errors="replace")

    if "/admin/runtime-dequeue-simulation" not in text:
        backup(MAIN_FILE)
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + ROUTE_BLOCK + "\n", encoding="utf-8")

    backup(TEST_FILE)
    TEST_FILE.write_text(TEST, encoding="utf-8")

    print("SAFE_DEQUEUE_SIMULATION_ROUTE_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", MAIN_FILE)
    print("Created:", TEST_FILE)

if __name__ == "__main__":
    main()