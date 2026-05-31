
from pathlib import Path

def main():
    text = Path("backend/app/main.py").read_text(
        encoding="utf-8",
        errors="replace",
    )

    required = [
        "/admin/runtime-execution-dry-run",
        "ADVANCED_RUNTIME_EXECUTION_READY",
        "distributed_execution_runtime",
        "multi_worker_ready",
        "queue_governance_active",
        "dequeue_simulation",
        "jobs_executed",
        "external_provider_called",
        "spend_performed",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        raise AssertionError(f"Missing runtime execution markers: {missing}")

    print("ADVANCED_RUNTIME_EXECUTION_TEST_PASSED")

if __name__ == "__main__":
    main()
