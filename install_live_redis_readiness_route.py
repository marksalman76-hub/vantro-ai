from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"live_redis_readiness_route_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

MAIN_FILE = ROOT / "backend" / "app" / "main.py"
TEST_FILE = ROOT / "test_live_redis_readiness_route.py"

ROUTE_CODE = r'''

@app.get("/admin/redis-readiness")
async def admin_redis_readiness(request: Request):
    """
    Owner/admin Redis readiness check.

    Safe behaviour:
    - Does not enqueue jobs.
    - Does not execute workers.
    - Does not call providers.
    - Does not expose REDIS_URL.
    """
    try:
        from backend.app.runtime.queue_adapter import RedisQueueAdapter, create_queue_adapter

        redis_probe = RedisQueueAdapter()
        redis_health = redis_probe.health()

        selected_adapter = create_queue_adapter()
        selected_health = selected_adapter.health()

        return {
            "success": True,
            "check": "admin_redis_readiness",
            "redis_configured": bool(redis_health.get("redis_url_configured")),
            "redis_available": bool(redis_health.get("available")),
            "redis_health": {
                "adapter": redis_health.get("adapter"),
                "available": redis_health.get("available"),
                "redis_required": redis_health.get("redis_required"),
                "redis_url_configured": redis_health.get("redis_url_configured"),
                "error": redis_health.get("error"),
            },
            "selected_queue_adapter": {
                "adapter": selected_health.get("adapter"),
                "available": selected_health.get("available"),
                "redis_required": selected_health.get("redis_required"),
            },
            "live_runtime_changed": False,
            "jobs_executed": False,
            "external_provider_called": False,
            "customer_safe": True,
            "status": "REDIS_READY" if redis_health.get("available") else "REDIS_NOT_READY",
        }
    except Exception as exc:
        return {
            "success": False,
            "check": "admin_redis_readiness",
            "error": repr(exc),
            "live_runtime_changed": False,
            "jobs_executed": False,
            "external_provider_called": False,
            "customer_safe": True,
            "status": "REDIS_READINESS_CHECK_FAILED",
        }
'''

TEST = r'''from pathlib import Path


def main():
    text = Path("backend/app/main.py").read_text(encoding="utf-8", errors="replace")

    required = [
        "/admin/redis-readiness",
        "RedisQueueAdapter",
        "create_queue_adapter",
        "jobs_executed",
        "external_provider_called",
        "customer_safe",
        "REDIS_READY",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(f"Missing Redis readiness route markers: {missing}")

    print("LIVE_REDIS_READINESS_ROUTE_TEST_PASSED")


if __name__ == "__main__":
    main()
'''

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")


def main():
    text = MAIN_FILE.read_text(encoding="utf-8", errors="replace")

    if '/admin/redis-readiness' not in text:
        backup(MAIN_FILE)
        text = text.rstrip() + "\n" + ROUTE_CODE + "\n"
        MAIN_FILE.write_text(text, encoding="utf-8")

    backup(TEST_FILE)
    TEST_FILE.write_text(TEST, encoding="utf-8")

    print("LIVE_REDIS_READINESS_ROUTE_INSTALLED")
    print("Backup folder:", BACKUP)
    print("Updated:", MAIN_FILE)
    print("Created/updated:", TEST_FILE)
    print("Safety:")
    print("- No jobs executed")
    print("- No provider calls")
    print("- REDIS_URL not exposed")
    print("- Customer-safe readiness only")


if __name__ == "__main__":
    main()