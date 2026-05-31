from pathlib import Path

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
