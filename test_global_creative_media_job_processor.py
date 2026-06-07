from __future__ import annotations

import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Iterator

from backend.app.api.media_routes import list_assets
from backend.app.runtime import async_media_job_foundation as media_jobs
from backend.app.runtime import delegated_workforce_execution_runtime as delegated
from backend.app.runtime import shared_creative_media_generation_runtime as shared_media
from backend.app.runtime.admin_creative_media_asset_viewer import get_admin_creative_media_assets


TERMINAL_STATUSES = {"completed", "provider_unavailable", "blocked", "failed"}


def _contains_unsafe_payload(value: object) -> bool:
    text = json.dumps(value, sort_keys=True).lower()
    return any(
        marker in text
        for marker in [
            "super_secret_provider_token",
            "raw_provider_payload",
            "internal_prompt",
            "debug_trace",
        ]
    )


@contextmanager
def provider_unavailable_media_generation() -> Iterator[None]:
    original = shared_media.generate_creative_media_pack

    def fake_generate_creative_media_pack(**kwargs: Any) -> Dict[str, Any]:
        return {
            "success": True,
            "media_pack_id": "media_pack_provider_unavailable",
            "agent_id": kwargs.get("agent_id"),
            "tenant_id": kwargs.get("tenant_id"),
            "media_assets": [],
            "real_media_asset_count": 0,
            "persisted_asset_count": 0,
            "playable_asset_count": 0,
            "metadata_only_asset_count": 0,
            "live_provider_execution_attempted_count": 0,
            "provider_execution_results": [
                {
                    "success": True,
                    "status": "prepared_no_live_provider_configured",
                    "execution_status": "prepared_no_live_provider_configured",
                    "live_provider_execution_attempted": False,
                    "raw_provider_payload": "raw_provider_payload",
                    "credential_values_exposed": False,
                    "customer_safe": True,
                }
            ],
            "generation_jobs": [
                {
                    "job_id": "provider_job_not_created",
                    "provider": "runway",
                    "media_type": "video",
                    "status": "prepared_no_live_provider_configured",
                    "live_generation_available": False,
                    "live_provider_execution_attempted": False,
                }
            ],
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    shared_media.generate_creative_media_pack = fake_generate_creative_media_pack
    try:
        yield
    finally:
        shared_media.generate_creative_media_pack = original


@contextmanager
def patched_delegated_persistence() -> Iterator[None]:
    originals = {
        "normalize_implementation_plan": delegated.normalize_implementation_plan,
        "create_orchestration_plan": delegated.create_orchestration_plan,
        "update_orchestration_plan_status": delegated.update_orchestration_plan_status,
        "record_orchestration_event": delegated.record_orchestration_event,
    }

    delegated.normalize_implementation_plan = lambda implementation_plan, fallback_agent="marketing_specialist_agent": implementation_plan
    delegated.create_orchestration_plan = lambda **kwargs: {"success": True}
    delegated.update_orchestration_plan_status = lambda **kwargs: {"success": True}
    delegated.record_orchestration_event = lambda **kwargs: {"success": True}
    try:
        yield
    finally:
        for name, original in originals.items():
            setattr(delegated, name, original)


def _create_queued_job(agent_id: str, tenant_id: str) -> Dict[str, Any]:
    job = media_jobs.enqueue_media_job(
        task=f"Create governed creative media assets for {agent_id}.",
        agent_id=agent_id,
        tenant_id=tenant_id,
        include_image=True,
        include_audio=True,
        include_video=True,
        include_avatar=agent_id != "ugc_creative_agent",
    )
    job["provider_token"] = "super_secret_provider_token"
    job["debug_trace"] = {"raw_provider_payload": "raw_provider_payload"}
    job["internal_prompt"] = "internal_prompt"
    media_jobs._write_job(job)
    return job


def test_delegated_workforce_processes_global_creative_media_jobs() -> None:
    old_store = media_jobs.STORE
    with TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        media_jobs.STORE.mkdir(parents=True, exist_ok=True)
        try:
            jobs = [
                _create_queued_job("ugc_creative_agent", "client_demo_001"),
                _create_queued_job("paid_ads_agent", "client_demo_001"),
            ]

            with provider_unavailable_media_generation(), patched_delegated_persistence():
                delegated_result = delegated.execute_delegated_workforce_plan(
                    implementation_plan={"action_packets": []},
                    owner_approved=True,
                    client_owned_agents=["ugc_creative_agent", "paid_ads_agent"],
                    package_tier="enterprise",
                    connected_integrations=[],
                    tenant_id="client_demo_001",
                    media_job_processing_authorized=True,
                )

            assert delegated_result["success"] is True
            assert delegated_result["media_job_runner_triggered"] is True
            assert delegated_result["media_job_processed_count"] == 2
            assert not _contains_unsafe_payload(delegated_result)

            listed = media_jobs.list_media_jobs(limit=10)
            by_id = {job["job_id"]: job for job in listed["jobs"]}
            for job in jobs:
                processed = by_id[job["job_id"]]
                assert processed["status"] in TERMINAL_STATUSES
                assert processed["status"] != "queued"
                assert processed["status"] == "provider_unavailable"
                assert processed["preview_ready_count"] == 0
                assert processed["download_ready_count"] == 0

            admin_assets = get_admin_creative_media_assets(limit=10)
            assert admin_assets["success"] is True
            admin_by_id = {asset.get("asset_id"): asset for asset in admin_assets["assets"]}
            for job in jobs:
                evidence = admin_by_id[job["job_id"]]
                assert evidence["status"] in TERMINAL_STATUSES
                assert evidence["status"] != "queued"
                assert evidence["status"] == "provider_unavailable"
                assert evidence["preview_ready"] is False
                assert evidence["download_ready"] is False
                assert evidence["credential_values_exposed"] is False
            assert not _contains_unsafe_payload(admin_assets)

            client_assets = list_assets(x_tenant_id="client_demo_001")
            assert client_assets["success"] is True
            client_by_id = {asset.get("asset_id"): asset for asset in client_assets["assets"]}
            for job in jobs:
                evidence = client_by_id[job["job_id"]]
                assert evidence["status"] in TERMINAL_STATUSES
                assert evidence["status"] != "queued"
                assert evidence["customer_safe"] is True
                assert evidence["client_safe"] is True
                assert evidence["final_assets"] == []
                assert evidence["credential_values_exposed"] is False
            assert not _contains_unsafe_payload(client_assets)
        finally:
            media_jobs.STORE = old_store


if __name__ == "__main__":
    test_delegated_workforce_processes_global_creative_media_jobs()
    print("GLOBAL_CREATIVE_MEDIA_JOB_PROCESSOR_PASSED")
    sys.stdout.flush()
    os._exit(0)
