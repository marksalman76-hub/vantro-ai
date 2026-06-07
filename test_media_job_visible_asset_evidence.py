from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.app.api.media_routes import list_assets
from backend.app.runtime import async_media_job_foundation as media_jobs
from backend.app.runtime.admin_creative_media_asset_viewer import get_admin_creative_media_assets


def _contains_secret(value: object) -> bool:
    return "super_secret_provider_token" in json.dumps(value, sort_keys=True)


def test_queued_creative_media_job_visible_as_admin_and_client_evidence() -> None:
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

            evidence = media_jobs.media_job_to_visible_asset_evidence(job, audience="admin")
            assert evidence["asset_id"] == job["job_id"]
            assert evidence["asset_type"] == "creative_media_job_evidence"
            assert evidence["agent_label"] == "Ugc Creative Agent"
            assert evidence["credential_values_exposed"] is False
            assert not _contains_secret(evidence)

            admin_assets = get_admin_creative_media_assets(limit=10)
            assert admin_assets["success"] is True
            assert admin_assets["asset_count"] >= 1
            admin_evidence = [asset for asset in admin_assets["assets"] if asset.get("asset_id") == job["job_id"]]
            assert admin_evidence
            assert admin_evidence[0]["provider_readiness"] == "queued"
            assert admin_evidence[0]["credential_values_exposed"] is False
            assert not _contains_secret(admin_assets)

            client_assets = list_assets(x_tenant_id="client_demo_001")
            assert client_assets["success"] is True
            assert client_assets["asset_count"] >= 1
            client_evidence = [asset for asset in client_assets["assets"] if asset.get("asset_id") == job["job_id"]]
            assert client_evidence
            assert client_evidence[0]["customer_safe"] is True
            assert client_evidence[0]["credential_values_exposed"] is False
            assert not _contains_secret(client_assets)
        finally:
            media_jobs.STORE = old_store


if __name__ == "__main__":
    test_queued_creative_media_job_visible_as_admin_and_client_evidence()
    print("MEDIA_JOB_VISIBLE_ASSET_EVIDENCE_PASSED")
