from pathlib import Path
import shutil

from backend.app.runtime.durable_media_job_store import LocalDurableMediaJobStore
from backend.app.runtime.durable_media_asset_store import LocalDurableMediaAssetStore
from backend.app.runtime.durable_media_queue import LocalDurableMediaQueue
from backend.app.runtime.media_job_acceptance_service import MediaJobAcceptanceService


def make_service(name: str):
    root = Path("runtime_outputs") / name
    if root.exists():
        shutil.rmtree(root)

    job_store = LocalDurableMediaJobStore(root=root / "jobs")
    asset_store = LocalDurableMediaAssetStore(root=root / "assets")
    queue = LocalDurableMediaQueue(root=root / "queue")
    service = MediaJobAcceptanceService(job_store=job_store, asset_store=asset_store, queue=queue)
    return service, job_store, asset_store, queue


def test_admin_acceptance():
    service, job_store, asset_store, queue = make_service("media_job_acceptance_admin")

    result = service.accept_media_job({
        "portal_mode": "admin",
        "role": "owner",
        "actor_id": "owner_test",
        "prompt": "Create a cinematic brand video.",
        "duration_seconds": 60,
        "media_type": "complete_video",
        "selected_agent": "marketing_specialist_agent",
        "human_mode": "No human/avatar",
        "api_key": "should-never-leak",
    })

    assert result["success"] is True
    assert result["accepted"] is True
    assert result["status"] == "queued"
    assert result["portal_mode"] == "admin"
    assert result["decision"]["requires_credit_check"] is False
    assert result["decision"]["requires_package_check"] is False
    assert result["decision"]["requires_owner_approval"] is False
    assert result["credential_values_exposed"] is False

    job = job_store.get_job(result["job_id"])
    assert job["success"] is True
    assert job["status"] == "queued"
    assert job["creative_controls"]["duration_seconds"] == 60

    stats = queue.stats()
    assert stats["ready"] == 1


def test_client_acceptance():
    service, job_store, asset_store, queue = make_service("media_job_acceptance_client")

    result = service.accept_media_job({
        "portal_mode": "client",
        "client_id": "client_test",
        "tenant_id": "client_test",
        "actor_id": "client_test",
        "prompt": "Create a client paid media video.",
        "duration_seconds": 30,
        "media_type": "complete_video",
        "selected_agent": "marketing_specialist_agent",
        "human_mode": "Use client-uploaded face/likeness",
        "uploaded_likeness_asset_id": "asset_face_ref_001",
        "explicit_likeness_consent": True,
        "owner_approval_required": True,
        "provider_diagnostics": {"should": "not leak"},
        "api_key": "should-never-leak",
    })

    assert result["success"] is True
    assert result["accepted"] is True
    assert result["status"] == "queued"
    assert result["portal_mode"] == "client"
    assert result["decision"]["requires_credit_check"] is True
    assert result["decision"]["requires_package_check"] is True
    assert result["decision"]["requires_owner_approval"] is True
    assert result["credential_values_exposed"] is False

    response_text = str(result)
    assert "should-never-leak" not in response_text
    assert "not leak" not in response_text

    job = job_store.get_job(result["job_id"])
    assert job["success"] is True
    assert job["creative_controls"]["human"]["human_mode"] == "Use client-uploaded face/likeness"
    assert job["creative_controls"]["human"]["explicit_likeness_consent"] is True

    client_status = service.get_media_job_status(result["job_id"], {
        "portal_mode": "client",
        "client_id": "client_test",
    })
    assert client_status["credential_values_exposed"] is False
    assert "provider_diagnostics" not in str(client_status)

    stats = queue.stats()
    assert stats["ready"] == 1


def main():
    test_admin_acceptance()
    test_client_acceptance()
    print("MEDIA_JOB_ACCEPTANCE_SERVICE_TEST_PASSED")


if __name__ == "__main__":
    main()
