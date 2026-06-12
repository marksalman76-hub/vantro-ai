from pathlib import Path
import shutil

from backend.app.runtime.durable_media_job_store import LocalDurableMediaJobStore
from backend.app.runtime.durable_media_asset_store import LocalDurableMediaAssetStore
from backend.app.runtime.durable_media_queue import LocalDurableMediaQueue
from backend.app.workers.media_worker import MediaWorker


def make_isolated_worker(name: str):
    root = Path("runtime_outputs") / name
    if root.exists():
        shutil.rmtree(root)

    job_store = LocalDurableMediaJobStore(root=root / "jobs")
    asset_store = LocalDurableMediaAssetStore(root=root / "assets")
    queue = LocalDurableMediaQueue(root=root / "queue")
    worker = MediaWorker(job_store=job_store, asset_store=asset_store, queue=queue)
    return worker, job_store, asset_store, queue


def test_admin_worker_flow():
    worker, job_store, asset_store, queue = make_isolated_worker("media_worker_test_admin")

    job = job_store.create_job({
        "portal_mode": "admin",
        "role": "owner",
        "prompt": "Create a cinematic full-stack media test.",
        "duration_seconds": 30,
        "selected_agent": "marketing_specialist_agent",
        "media_type": "complete_video",
    })

    enqueued = queue.enqueue(
        job_id=job["job_id"],
        payload={
            "portal_mode": "admin",
            "role": "owner",
            "actor_id": "owner_test",
            "media_type": "complete_video",
        },
    )
    assert enqueued["success"] is True

    result = worker.process_next()
    assert result["success"] is True
    assert result["status"] == "worker_foundation_completed"
    assert result["authority"]["portal_mode"] == "admin"
    assert result["authority"]["unrestricted_execution"] is True
    assert result["decision"]["requires_credit_check"] is False
    assert result["decision"]["requires_package_check"] is False
    assert result["decision"]["requires_owner_approval"] is False

    loaded = job_store.get_job(job["job_id"])
    assert loaded["status"] == "worker_foundation_completed"

    stats = queue.stats()
    assert stats["done"] == 1


def test_client_worker_flow():
    worker, job_store, asset_store, queue = make_isolated_worker("media_worker_test_client")

    job = job_store.create_job({
        "portal_mode": "client",
        "client_id": "client_test",
        "tenant_id": "client_test",
        "prompt": "Create a governed client media test.",
        "duration_seconds": 30,
        "selected_agent": "marketing_specialist_agent",
        "media_type": "complete_video",
    })

    enqueued = queue.enqueue(
        job_id=job["job_id"],
        payload={
            "portal_mode": "client",
            "client_id": "client_test",
            "actor_id": "client_test",
            "owner_approval_required": True,
            "media_type": "complete_video",
            "provider_diagnostics": {"should": "not leak to client"},
            "api_key": "secret-test-value",
        },
    )
    assert enqueued["success"] is True

    result = worker.process_next()
    assert result["success"] is True
    assert result["status"] == "worker_foundation_completed"
    assert result["authority"]["portal_mode"] == "client"
    assert result["authority"]["unrestricted_execution"] is False
    assert result["decision"]["requires_credit_check"] is True
    assert result["decision"]["requires_package_check"] is True
    assert result["decision"]["requires_owner_approval"] is True

    assert result["job"]["credential_values_exposed"] is False
    assert result["job"]["internal_config_exposed"] is False

    loaded = job_store.get_job(job["job_id"])
    assert loaded["status"] == "worker_foundation_completed"

    stats = queue.stats()
    assert stats["done"] == 1


def main():
    test_admin_worker_flow()
    test_client_worker_flow()
    print("MEDIA_WORKER_FOUNDATION_TEST_PASSED")


if __name__ == "__main__":
    main()
