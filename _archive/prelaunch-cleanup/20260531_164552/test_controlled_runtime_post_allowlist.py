from pathlib import Path

def main():
    text = Path("backend/app/main.py").read_text(encoding="utf-8", errors="replace")
    required = [
        "/admin/runtime-execution-dry-run-safe",
        "CONTROLLED_RUNTIME_DRY_RUN_COMPLETE",
        "adapter.enqueue",
        "provider_execution_allowed",
        "spend_allowed",
        "autonomous_execution_allowed",
        "jobs_executed",
        "external_provider_called",
        "spend_performed",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise AssertionError(f"Missing controlled runtime dry-run markers: {missing}")
    print("CONTROLLED_RUNTIME_POST_ALLOWLIST_TEST_PASSED")

if __name__ == "__main__":
    main()
