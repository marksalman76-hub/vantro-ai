from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"background_worker_loop_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

WORKER_FILE = ROOT / "backend" / "app" / "runtime" / "background_worker_loop.py"
TEST_FILE = ROOT / "test_background_worker_loop.py"

WORKER = r'''"""
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
'''

TEST = r'''from backend.app.runtime.background_worker_loop import (
    run_once,
    worker_live_execution_enabled,
)


def main():
    status = run_once()

    if status["worker"] != "background_worker_loop":
        raise AssertionError("Wrong worker name")

    if status["status"] != "running":
        raise AssertionError("Worker status not running")

    if status["jobs_executed"] is not False:
        raise AssertionError("Worker should not execute jobs in foundation mode")

    if status["external_provider_called"] is not False:
        raise AssertionError("Worker should not call providers in foundation mode")

    if worker_live_execution_enabled() is not False:
        raise AssertionError("Worker live execution should be false by default")

    print("BACKGROUND_WORKER_LOOP_TEST_PASSED")
    print(status)


if __name__ == "__main__":
    main()
'''

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def write(path: Path, content: str):
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    write(WORKER_FILE, WORKER)
    write(TEST_FILE, TEST)

    print("BACKGROUND_WORKER_LOOP_INSTALLED")
    print("Backup folder:", BACKUP)
    print("Created/updated:")
    print("-", WORKER_FILE)
    print("-", TEST_FILE)
    print("Safety:")
    print("- Worker entrypoint exists")
    print("- Redis adapter can be checked")
    print("- No jobs executed by default")
    print("- No provider calls by default")


if __name__ == "__main__":
    main()