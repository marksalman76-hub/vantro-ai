from __future__ import annotations

import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.app.api.media_routes import list_assets
from backend.app.runtime import async_media_job_foundation as media_jobs
from backend.app.runtime import shared_creative_media_generation_runtime as shared_media
from backend.app.runtime.admin_creative_media_asset_viewer import get_admin_creative_media_assets


def _contains_secret(value: object) -> bool:
    return "super_secret_provider_token" in json.dumps(value, sort_keys=True)


@contextmanager
def provider_unavailable_media_generation():
    original = shared_media.generate_creative_media_pack

    def fake_generate_creative_media_pack(**kwargs):
        return {
            "success": True,
            "media_pack_id": "media_pack_provider_unavailable",
            "media_assets": [],
            "real_media_asset_count": 0,
            "persisted_asset_count": 0,
            "credential_values_exposed": False,
        }

    shared_media.generate_creative_media_pack = fake_generate_creative_media_pack
    try:
        yield
    finally:
        shared_media.generate_creative_media_pack = original


def test_queued_creative_media_job_processed_to_safe_visible_evidence() -> None:
    old_store = media_jobs.STORE
    with TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        media_jobs.STORE.mkdir(parents=True, exist_ok=True)
        try:
            job = media_jobs.enqueue_media_job(
                task="Create UGC product launch creative media.",
                agent_id="ugc_creative_agent",
                tenant_id="client_demo_001",
                include_image=True,
                include_audio=True,
                include_video=True,
            )
            job["provider_token"] = "super_secret_provider_token"
            job["debug_payload"] = {"secret": "super_secret_provider_token"}
            media_jobs._write_job(job)

            with provider_unavailable_media_generation():
                processed = media_jobs.run_all_media_jobs(limit=5)

            assert processed["success"] is True
            assert processed["processed_count"] == 1
            processed_job = processed["results"][0]["job"]
            assert processed_job["status"] == "provider_unavailable"
            assert processed_job["status"] != "queued"
            assert processed_job["blocked_reason"]
            assert "super_secret_provider_token" not in processed_job["blocked_reason"]
            assert "provider_token" not in processed_job["blocked_reason"]
            assert not _contains_secret(processed)

            admin_assets = get_admin_creative_media_assets(limit=10)
            assert admin_assets["success"] is True
            assert admin_assets["asset_count"] >= 1
            admin_evidence = [asset for asset in admin_assets["assets"] if asset.get("asset_id") == job["job_id"]]
            assert admin_evidence
            assert admin_evidence[0]["status"] == "provider_unavailable"
            assert admin_evidence[0]["provider_readiness"] == "provider_unavailable"
            assert admin_evidence[0]["blocked_reason"]
            assert admin_evidence[0]["credential_values_exposed"] is False
            assert not _contains_secret(admin_assets)

            client_assets = list_assets(x_tenant_id="client_demo_001")
            assert client_assets["success"] is True
            assert client_assets["asset_count"] >= 1
            client_evidence = [asset for asset in client_assets["assets"] if asset.get("asset_id") == job["job_id"]]
            assert client_evidence
            assert client_evidence[0]["status"] == "provider_unavailable"
            assert client_evidence[0]["customer_safe"] is True
            assert client_evidence[0]["credential_values_exposed"] is False
            assert not _contains_secret(client_assets)
        finally:
            media_jobs.STORE = old_store


def test_delegated_workforce_api_triggers_media_job_runner() -> None:
    route_text = Path("frontend/src/app/api/delegated-workforce-execution/route.ts").read_text(encoding="utf-8")
    assert "/admin/media-jobs/run-all" in route_text
    assert "runBackendMediaJobsForDelegatedWorkforce" in route_text
    assert "media_job_runner_triggered" in route_text
    assert "media_job_processed_count" in route_text


if __name__ == "__main__":
    test_queued_creative_media_job_processed_to_safe_visible_evidence()
    test_delegated_workforce_api_triggers_media_job_runner()
    print("MEDIA_JOB_VISIBLE_ASSET_EVIDENCE_PASSED")
    sys.stdout.flush()
    os._exit(0)
