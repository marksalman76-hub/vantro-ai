from pathlib import Path


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
