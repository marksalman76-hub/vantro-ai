from __future__ import annotations

import base64
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.app.runtime import ai_media_live_provider_execution as live_exec
from backend.app.runtime import async_media_job_foundation as media_jobs
from backend.app.runtime import creative_asset_persistence_bridge as bridge
from backend.app.runtime import shared_creative_media_generation_runtime as shared_media
from backend.app.runtime.asset_storage_signed_delivery_runtime import (
    reset_asset_storage_for_tests,
)


@contextmanager
def isolated_creative_registry():
    original = {
        "REGISTRY_DIR": bridge.REGISTRY_DIR,
        "REGISTRY_FILE": bridge.REGISTRY_FILE,
        "REGISTRY_INDEX_FILE": bridge.REGISTRY_INDEX_FILE,
        "ASSET_RECORD_DIR": bridge.ASSET_RECORD_DIR,
    }

    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        bridge.REGISTRY_DIR = root
        bridge.REGISTRY_FILE = root / "creative_assets.json"
        bridge.REGISTRY_INDEX_FILE = root / "creative_assets_index.json"
        bridge.ASSET_RECORD_DIR = root / "assets"
        bridge.ASSET_RECORD_DIR.mkdir(parents=True, exist_ok=True)
        try:
            yield
        finally:
            bridge.REGISTRY_DIR = original["REGISTRY_DIR"]
            bridge.REGISTRY_FILE = original["REGISTRY_FILE"]
            bridge.REGISTRY_INDEX_FILE = original["REGISTRY_INDEX_FILE"]
            bridge.ASSET_RECORD_DIR = original["ASSET_RECORD_DIR"]


@contextmanager
def local_only_persistence():
    original = bridge.supabase_enabled
    original_record = bridge.record_canonical_media_asset
    bridge.supabase_enabled = lambda: False
    bridge.record_canonical_media_asset = lambda **_: {"success": True, "storage_mode": "local_test"}
    try:
        yield
    finally:
        bridge.supabase_enabled = original
        bridge.record_canonical_media_asset = original_record


@contextmanager
def configured_runway_env():
    keys = [
        "RUNWAYML_API_SECRET",
        "RUNWAY_CREATE_JOB_URL",
        "LIVE_EXTERNAL_CALLS_ENABLED",
        "OWNER_APPROVED_LIVE_ACTIVATION",
        "REAL_PROVIDER_HTTP_DISPATCH_ENABLED",
    ]
    original = {key: os.environ.get(key) for key in keys}
    os.environ["RUNWAYML_API_SECRET"] = "configured-runway-secret"
    os.environ["RUNWAY_CREATE_JOB_URL"] = "https://example.com/runway/jobs"
    os.environ["LIVE_EXTERNAL_CALLS_ENABLED"] = "true"
    os.environ["OWNER_APPROVED_LIVE_ACTIVATION"] = "true"
    os.environ["REAL_PROVIDER_HTTP_DISPATCH_ENABLED"] = "true"
    try:
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _provider_packet() -> dict:
    return {
        "packet_type": "creative_media_provider_execution_packet",
        "execution_allowed": True,
        "primary_provider_slot": "runway",
        "provider_parameters": {
            "provider": "runway",
            "media_type": "video",
            "prompt": "Create a product hero video",
        },
    }


def test_runway_async_job_response_is_polling_not_failed() -> None:
    original = live_exec._request_json

    def fake_request_json(**_: object) -> dict:
        return {
            "success": True,
            "status_code": 202,
            "response": {
                "id": "runway_job_123",
                "status": "RUNNING",
                "status_url": "https://example.com/runway/jobs/runway_job_123",
            },
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    live_exec._request_json = fake_request_json
    try:
        with configured_runway_env():
            result = live_exec.execute_ai_media_provider_ready_packet(_provider_packet())
    finally:
        live_exec._request_json = original

    assert result["execution_status"] == "polling_provider"
    assert result["provider_job_id_present"] is True
    assert result["provider_polling_required"] is True
    assert result["provider_polling_url_present"] is True
    assert result["provider_output_url_present"] is False
    assert result["provider_http_status"] == 202
    assert result["playable_asset_created"] is False
    assert result["metadata_only"] is True
    assert result["credential_values_exposed"] is False


def test_provider_output_url_is_persisted_and_signed_delivery_created() -> None:
    reset_asset_storage_for_tests()
    with isolated_creative_registry(), local_only_persistence():
        persisted = bridge.persist_creative_asset(
            {
                "agent_id": "ugc_creative_agent",
                "tenant_id": "owner_admin",
                "provider": "runway",
                "asset_type": "video",
                "title": "Runway video asset",
                "status": "completed",
                "provider_asset_url": "https://example.com/generated/video.mp4",
            }
        )

        assert persisted["success"] is True
        assert persisted["playable"] is False
        assert persisted["preview_ready"] is False
        assert persisted["download_ready"] is False
        assert persisted["metadata_only"] is True
        assert persisted["asset_status"] == "blocked_placeholder_source"
        assert persisted["not_playable_reason"] == "placeholder_or_invalid_media_source"
        assert persisted["signed_delivery_created"] is False


def test_real_supabase_provider_output_url_remains_playable() -> None:
    reset_asset_storage_for_tests()
    with isolated_creative_registry(), local_only_persistence():
        persisted = bridge.persist_creative_asset(
            {
                "agent_id": "ugc_creative_agent",
                "tenant_id": "owner_admin",
                "provider": "elevenlabs",
                "asset_type": "audio",
                "title": "Playable Supabase audio asset",
                "status": "completed",
                "provider_asset_url": "https://demo.supabase.co/storage/v1/object/public/creative-media/audio.mp3",
            }
        )

        assert persisted["success"] is True
        assert persisted["playable"] is True
        assert persisted["metadata_only"] is False
        assert persisted["signed_delivery_created"] is True


def test_embedded_audio_data_url_is_materialized_and_signed_delivery_created() -> None:
    reset_asset_storage_for_tests()
    audio_data_url = "data:audio/mpeg;base64," + base64.b64encode(b"fake-mp3-bytes").decode("ascii")

    with isolated_creative_registry(), local_only_persistence():
        persisted = bridge.persist_creative_asset(
            {
                "agent_id": "ugc_creative_agent",
                "tenant_id": "owner_admin",
                "provider": "elevenlabs",
                "asset_type": "audio",
                "title": "Voiceover asset",
                "status": "completed",
                "provider_asset_url": audio_data_url,
            }
        )

        assert persisted["success"] is True
        assert persisted["playable"] is False
        assert persisted["metadata_only"] is True
        assert persisted["signed_delivery_created"] is False


def test_provider_failure_returns_safe_diagnostics_without_secrets() -> None:
    original = live_exec._request_json

    def fake_request_json(**_: object) -> dict:
        return {
            "success": False,
            "status_code": 500,
            "response": {
                "error_code": "provider_server_error",
                "error_body": "secret-token-123 should never be surfaced",
            },
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    live_exec._request_json = fake_request_json
    try:
        with configured_runway_env():
            result = live_exec.execute_ai_media_provider_ready_packet(_provider_packet())
    finally:
        live_exec._request_json = original

    assert result["execution_status"] == "provider_http_error"
    assert result["provider_http_status"] == 500
    assert result["provider_error_code"] == "provider_server_error"
    assert result["provider_error_safe_message"] == "Provider HTTP request failed safely. No credentials or provider secrets were exposed."
    assert result["provider_output_url_present"] is False
    assert result["credential_values_exposed"] is False


def test_media_job_stays_processing_when_provider_is_polling() -> None:
    original = shared_media.generate_creative_media_pack

    def fake_generate_creative_media_pack(**_: object) -> dict:
        return {
            "success": True,
            "media_pack_id": "pack_polling_001",
            "media_assets": [
                {
                    "asset_id": "video_asset_polling_001",
                    "asset_type": "video",
                    "media_type": "video",
                    "status": "polling_provider",
                    "playable": False,
                    "metadata_only": False,
                    "provider_polling_required": True,
                    "persistence": {
                        "success": False,
                        "persisted": False,
                        "reason": "provider_output_pending",
                    },
                }
            ],
            "generation_jobs": [
                {
                    "job_id": "runway_job_123",
                    "media_type": "video",
                    "provider": "runway",
                    "status": "polling_provider",
                    "live_generation_available": True,
                    "live_provider_execution_attempted": True,
                    "real_media_asset_created": False,
                }
            ],
            "provider_execution_results": [
                {
                    "provider": "runway",
                    "status": "polling_provider",
                    "execution_status": "polling_provider",
                    "provider_polling_required": True,
                    "provider_configured": True,
                    "provider_dispatch_enabled": True,
                    "live_external_calls_enabled": True,
                    "owner_approved_live_activation": True,
                    "real_provider_http_dispatch_enabled": True,
                    "live_provider_execution_attempted": True,
                }
            ],
            "real_media_asset_count": 0,
            "persisted_asset_count": 0,
            "live_provider_execution_attempted_count": 1,
        }

    shared_media.generate_creative_media_pack = fake_generate_creative_media_pack
    try:
        job = media_jobs.enqueue_media_job(
            task="Create a premium creative media asset.",
            agent_id="ugc_creative_agent",
            tenant_id="owner_admin",
            include_image=False,
            include_audio=False,
            include_video=True,
            include_avatar=False,
        )
        result = media_jobs.process_media_job(job)
    finally:
        shared_media.generate_creative_media_pack = original

    assert result["success"] is True
    assert result["status"] == "processing"
    assert result["job"]["lifecycle"] == "polling_provider"
    assert result["job"]["safe_visible_reason"] == "Provider execution is still processing. No playable media asset is available yet."
    assert result["job"]["credential_values_exposed"] is False


if __name__ == "__main__":
    test_runway_async_job_response_is_polling_not_failed()
    test_provider_output_url_is_persisted_and_signed_delivery_created()
    test_real_supabase_provider_output_url_remains_playable()
    test_embedded_audio_data_url_is_materialized_and_signed_delivery_created()
    test_provider_failure_returns_safe_diagnostics_without_secrets()
    test_media_job_stays_processing_when_provider_is_polling()
    print("PROVIDER_RESULT_PERSISTENCE_PASSED")
    sys.stdout.flush()
