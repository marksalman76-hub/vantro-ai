
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
