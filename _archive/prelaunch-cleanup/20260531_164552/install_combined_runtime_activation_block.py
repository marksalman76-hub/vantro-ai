from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

BACKUP = ROOT / "backups" / f"combined_runtime_activation_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

WORKER_FILE = ROOT / "backend" / "app" / "runtime" / "background_worker_loop.py"

TEST_FILE = ROOT / "test_combined_runtime_activation.py"

ROUTE_FILE = ROOT / "backend" / "app" / "main.py"


WORKER_APPEND = r'''

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
'''

ROUTE_APPEND = r'''

@app.get("/admin/runtime-worker-health")
async def admin_runtime_worker_health():
    """
    Distributed worker/runtime health visibility.
    Safe visibility only.
    """

    try:
        from backend.app.runtime.background_worker_loop import (
            build_worker_status,
            build_execution_gate_status,
        )

        worker = build_worker_status()
        gates = build_execution_gate_status()

        return {
            "success": True,
            "runtime": "distributed_worker_runtime",
            "worker": worker,
            "execution_gates": gates,
            "queue_backend": worker.get("queue_adapter", {}),
            "jobs_executed": False,
            "external_provider_called": False,
            "customer_safe": True,
            "status": "WORKER_RUNTIME_READY",
        }

    except Exception as exc:
        return {
            "success": False,
            "error": repr(exc),
            "status": "WORKER_RUNTIME_CHECK_FAILED",
        }
'''

TEST = r'''
from backend.app.runtime.background_worker_loop import (
    build_worker_status,
    build_execution_gate_status,
)

def main():
    worker = build_worker_status()
    gates = build_execution_gate_status()

    assert worker["worker"] == "background_worker_loop"
    assert worker["jobs_executed"] is False
    assert worker["external_provider_called"] is False

    assert "execution_permitted" in gates
    assert gates["execution_permitted"] is False

    print("COMBINED_RUNTIME_ACTIVATION_TEST_PASSED")
    print(worker)
    print(gates)

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

def append_once(path: Path, marker: str, content: str):
    text = path.read_text(encoding="utf-8", errors="replace")

    if marker not in text:
        backup(path)
        text += "\n\n" + content + "\n"
        path.write_text(text, encoding="utf-8")

def main():
    append_once(
        WORKER_FILE,
        "def worker_execution_permitted()",
        WORKER_APPEND,
    )

    append_once(
        ROUTE_FILE,
        "/admin/runtime-worker-health",
        ROUTE_APPEND,
    )

    backup(TEST_FILE)
    TEST_FILE.write_text(TEST, encoding="utf-8")

    print("COMBINED_RUNTIME_ACTIVATION_BLOCK_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:")
    print("-", WORKER_FILE)
    print("-", ROUTE_FILE)
    print("-", TEST_FILE)

if __name__ == "__main__":
    main()