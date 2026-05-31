from backend.app.runtime.queue_adapter import InMemoryQueueAdapter
from backend.app.runtime.queue_telemetry import (
    DEFAULT_QUEUE_NAMES,
    build_queue_health_snapshot,
    export_queue_health_dict,
    queue_telemetry_changes_live_execution,
    queue_telemetry_executes_jobs,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    adapter = InMemoryQueueAdapter()
    adapter.enqueue("client_agent_execution_queue", {"action": "run_agent"})
    adapter.enqueue("provider_generation_queue", {"action": "openai_live_generation"})

    snapshot = build_queue_health_snapshot(adapter=adapter, worker_count=2, active_workers=0)
    data = export_queue_health_dict(snapshot)

    assert_equal(data["adapter"], "in_memory", "adapter")
    assert_equal(data["adapter_available"], True, "adapter available")
    assert_equal(data["redis_required"], False, "redis required")
    assert_equal(data["queue_count"], len(DEFAULT_QUEUE_NAMES), "queue count")
    assert_equal(data["total_messages"], 2, "total messages")
    assert_equal(data["queues"]["client_agent_execution_queue"]["size"], 1, "client queue size")
    assert_equal(data["queues"]["provider_generation_queue"]["size"], 1, "provider queue size")
    assert_equal(data["worker_health"]["status"], "configured_but_inactive", "worker status")
    assert_equal(data["governance"]["owner_approval_preserved"], True, "owner approval preserved")
    assert_equal(data["governance"]["live_external_execution_enabled_by_snapshot"], False, "live external not enabled")
    assert_equal(data["customer_safe"], True, "customer safe")

    assert_equal(queue_telemetry_changes_live_execution(), False, "live execution unchanged")
    assert_equal(queue_telemetry_executes_jobs(), False, "jobs not executed")

    print("QUEUE_TELEMETRY_WORKER_HEALTH_TEST_PASSED")
    print(data)


if __name__ == "__main__":
    main()
