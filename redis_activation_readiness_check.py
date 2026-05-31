import json
import os
from pathlib import Path

from backend.app.runtime.queue_adapter import create_queue_adapter, RedisQueueAdapter

def main():
    redis_url = os.getenv("REDIS_URL", "")
    redis_probe = RedisQueueAdapter(redis_url=redis_url or None)
    redis_health = redis_probe.health()

    memory_adapter = create_queue_adapter("memory")
    memory_health = memory_adapter.health()

    report = {
        "check": "redis_activation_readiness",
        "redis_url_configured": bool(redis_url),
        "redis_health": redis_health,
        "memory_fallback_health": memory_health,
        "live_runtime_changed": False,
        "jobs_executed": False,
        "safe_to_activate_redis": bool(redis_health.get("available")),
        "status": "REDIS_READY" if redis_health.get("available") else "REDIS_NOT_CONFIGURED_OR_UNAVAILABLE",
        "next_action": "Set REDIS_URL in Render/backend env before live worker activation" if not redis_health.get("available") else "Proceed to controlled queue adapter Redis verification"
    }

    Path("redis_activation_readiness_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("REDIS_ACTIVATION_READINESS_CHECK_COMPLETE")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()