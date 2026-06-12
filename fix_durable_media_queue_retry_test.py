from pathlib import Path

ROOT = Path.cwd()
QUEUE = ROOT / "backend" / "app" / "runtime" / "durable_media_queue.py"
TEST = ROOT / "test_durable_media_queue.py"

queue_text = QUEUE.read_text(encoding="utf-8")

old = 'message["visible_after"] = time.time() + min(300, 15 * attempts)'
new = 'message["visible_after"] = 0.0  # local deterministic retry; AWS SQS delay is handled by production adapter'

if old not in queue_text:
    raise SystemExit("Expected retry visibility line not found")

queue_text = queue_text.replace(old, new)
QUEUE.write_text(queue_text, encoding="utf-8")

TEST.write_text(r'''from pathlib import Path
import shutil

from backend.app.runtime.durable_media_queue import LocalDurableMediaQueue


def main():
    test_root = Path("runtime_outputs") / "durable_media_queue_test_isolated"
    if test_root.exists():
        shutil.rmtree(test_root)

    queue = LocalDurableMediaQueue(root=test_root)

    enqueued = queue.enqueue(
        job_id="durable_media_job_queue_test_001",
        payload={
            "media_type": "complete_video",
            "duration_seconds": 30,
            "human_mode": "Generate new avatar/person",
            "provider_plan": {
                "video": "runway",
                "audio": "elevenlabs",
                "composition": "ffmpeg",
            },
        },
        priority=10,
        max_attempts=2,
    )
    assert enqueued["success"] is True
    assert enqueued["accepted"] is True
    assert enqueued["status"] == "ready"

    claimed = queue.claim_next(visibility_timeout_seconds=60)
    assert claimed["success"] is True
    assert claimed["status"] == "in_flight"
    assert claimed["job_id"] == "durable_media_job_queue_test_001"
    assert claimed["message"]["attempt_count"] == 1

    failed = queue.fail(
        claimed["message_id"],
        error="temporary provider delay",
        receipt_handle=claimed["receipt_handle"],
        retry=True,
    )
    assert failed["success"] is True
    assert failed["status"] == "requeued"

    claimed_again = queue.claim_next(visibility_timeout_seconds=60)
    assert claimed_again["success"] is True
    assert claimed_again["message"]["attempt_count"] == 2

    dead = queue.fail(
        claimed_again["message_id"],
        error="provider failed after retry",
        receipt_handle=claimed_again["receipt_handle"],
        retry=True,
    )
    assert dead["success"] is True
    assert dead["status"] == "dead_letter"

    enqueued_2 = queue.enqueue(
        job_id="durable_media_job_queue_test_002",
        payload={"media_type": "complete_video"},
        priority=20,
    )
    assert enqueued_2["success"] is True

    claimed_2 = queue.claim_next(visibility_timeout_seconds=60)
    assert claimed_2["success"] is True

    completed = queue.complete(
        claimed_2["message_id"],
        receipt_handle=claimed_2["receipt_handle"],
    )
    assert completed["success"] is True
    assert completed["status"] == "done"

    stats = queue.stats()
    assert stats["success"] is True
    assert stats["queue_backend"] == "local_dev"
    assert stats["aws_target"] == "sqs_with_dead_letter_queue"
    assert stats["dead_letter"] == 1
    assert stats["done"] == 1

    print("DURABLE_MEDIA_QUEUE_TEST_PASSED")
    print("dead_letter:", stats["dead_letter"])
    print("done:", stats["done"])


if __name__ == "__main__":
    main()
''', encoding="utf-8")

print("DURABLE_MEDIA_QUEUE_RETRY_TEST_FIXED")
print(f"Updated: {QUEUE}")
print(f"Updated: {TEST}")