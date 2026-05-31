from pathlib import Path
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
