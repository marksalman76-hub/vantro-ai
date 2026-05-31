from backend.app.runtime.queue_adapter import (
    InMemoryQueueAdapter,
    RedisQueueAdapter,
    create_queue_adapter,
    queue_adapter_live_redis_required,
    queue_adapter_changes_live_execution,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    adapter = InMemoryQueueAdapter()
    health = adapter.health()

    assert_equal(health["adapter"], "in_memory", "memory adapter name")
    assert_equal(health["available"], True, "memory available")
    assert_equal(health["redis_required"], False, "memory redis required")

    msg = adapter.enqueue("client_agent_execution_queue", {"action": "run_agent"}, {"tenant_id": "test"})
    assert msg.id
    assert_equal(msg.status, "queued", "queued status")
    assert_equal(adapter.size("client_agent_execution_queue"), 1, "queue size after enqueue")

    out = adapter.dequeue("client_agent_execution_queue")
    if out is None:
        raise AssertionError("Expected dequeued message")
    assert_equal(out.status, "dequeued", "dequeued status")
    assert_equal(out.attempts, 1, "attempt increment")
    assert_equal(adapter.size("client_agent_execution_queue"), 0, "queue size after dequeue")

    fallback = create_queue_adapter("redis")
    fallback_health = fallback.health()
    if fallback_health["adapter"] not in {"in_memory", "redis"}:
        raise AssertionError(f"Unexpected adapter: {fallback_health}")

    redis_probe = RedisQueueAdapter(redis_url=None)
    redis_health = redis_probe.health()
    assert_equal(redis_health["adapter"], "redis", "redis adapter name")
    assert_equal(redis_health["available"], False, "redis unavailable without url")

    assert_equal(queue_adapter_live_redis_required(), False, "live redis required")
    assert_equal(queue_adapter_changes_live_execution(), False, "live execution changed")

    print("QUEUE_ADAPTER_TEST_PASSED")
    print("Default adapter:", create_queue_adapter().health())


if __name__ == "__main__":
    main()
