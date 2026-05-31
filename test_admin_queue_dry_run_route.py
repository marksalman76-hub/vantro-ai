from pathlib import Path


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
