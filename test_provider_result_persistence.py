from __future__ import annotations

import base64
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.app.runtime import ai_media_live_provider_execution as live_exec
from backend.app.runtime import admin_ugc_live_media_execution_bridge as ugc_bridge
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
    assert result["provider_output_url_present"] is True
    assert result["provider_output_url_rejected"] is True
    assert result["placeholder_output_detected"] is True
    assert result["provider_http_status"] == 202
    assert result["playable_asset_created"] is False
    assert result["metadata_only"] is True
    assert result["credential_values_exposed"] is False


def test_example_provider_output_url_is_rejected_and_not_playable() -> None:
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
        assert persisted["provider_output_url_present"] is True
        assert persisted["provider_output_url_rejected"] is True
        assert persisted["placeholder_output_detected"] is True
        assert persisted["provider_output_url_rejection_reason"] == "placeholder_domain_example"
        assert persisted["playable"] is False
        assert persisted["metadata_only"] is True
        assert persisted["signed_delivery_created"] is False


def test_placeholder_mock_and_test_urls_are_rejected() -> None:
    reset_asset_storage_for_tests()
    candidate_urls = [
        "https://mock-provider.local/generated/video.mp4",
        "https://cdn.placeholder-provider.com/asset.mp4",
        "http://localhost/generated/video.mp4",
        "https://assets.test-only-provider.com/video.mp4",
    ]

    with isolated_creative_registry(), local_only_persistence():
        for candidate in candidate_urls:
            persisted = bridge.persist_creative_asset(
                {
                    "agent_id": "ugc_creative_agent",
                    "tenant_id": "owner_admin",
                    "provider": "runway",
                    "asset_type": "video",
                    "title": "Runway video asset",
                    "status": "completed",
                    "provider_asset_url": candidate,
                }
            )
            assert persisted["success"] is True
            assert persisted["provider_output_url_present"] is True
            assert persisted["provider_output_url_rejected"] is True
            assert persisted["playable"] is False
            assert persisted["metadata_only"] is True
            assert persisted["signed_delivery_created"] is False


def test_valid_provider_output_url_remains_persistable() -> None:
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
                "provider_asset_url": "https://media.real-provider-cdn.com/output/video.mp4",
            }
        )

        assert persisted["success"] is True
        assert persisted["provider_output_url_present"] is True
        assert persisted["provider_output_url_rejected"] is False
        assert persisted["placeholder_output_detected"] is False
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
        assert persisted["playable"] is True
        assert persisted["metadata_only"] is False
        assert persisted["signed_delivery_created"] is True


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


def test_direct_fallback_path_persists_local_playable_asset() -> None:
    reset_asset_storage_for_tests()
    original_plan = ugc_bridge.create_runtime_creative_execution_plan
    original_tts = ugc_bridge.run_elevenlabs_tts_quality_test
    original_video = ugc_bridge.run_runway_text_to_video_quality_test
    original_compose = ugc_bridge.compose_audio_video_asset

    with TemporaryDirectory() as temp_dir:
        audio_file = Path(temp_dir) / "voiceover.mp3"
        audio_file.write_bytes(b"fake-audio-bytes")

        ugc_bridge.create_runtime_creative_execution_plan = lambda **_: {"success": True, "status": "ok"}
        ugc_bridge.run_elevenlabs_tts_quality_test = lambda **_: {
            "success": True,
            "status": "completed",
            "audio_saved": True,
            "audio_path": str(audio_file),
            "test_label": "fallback_voiceover",
            "credential_values_exposed": False,
        }
        ugc_bridge.run_runway_text_to_video_quality_test = lambda **_: {
            "success": False,
            "status": "runway_unavailable",
            "video_saved": False,
            "credential_values_exposed": False,
        }
        ugc_bridge.compose_audio_video_asset = lambda **_: {
            "success": False,
            "status": "composition_skipped_missing_audio_or_video",
            "composed_video_saved": False,
            "credential_values_exposed": False,
        }

        try:
            with isolated_creative_registry(), local_only_persistence():
                result = ugc_bridge.run_admin_ugc_live_media_execution_fallback(
                    task="Create a fallback creative media asset.",
                    owner_approved_live_execution=True,
                )
        finally:
            ugc_bridge.create_runtime_creative_execution_plan = original_plan
            ugc_bridge.run_elevenlabs_tts_quality_test = original_tts
            ugc_bridge.run_runway_text_to_video_quality_test = original_video
            ugc_bridge.compose_audio_video_asset = original_compose

    assert result["success"] is True
    assert result["status"] == "ugc_live_media_execution_completed"
    assert result["playable_asset_count"] >= 1
    assert result["persisted_asset_count"] >= 1
    assert any(bool(item.get("playable")) for item in result.get("persisted_asset_records", []))
    assert result["credential_values_exposed"] is False


def test_media_job_uses_direct_fallback_when_provider_output_not_playable() -> None:
    original_generate = shared_media.generate_creative_media_pack
    original_fallback = ugc_bridge.run_admin_ugc_live_media_execution_fallback

    def fake_generate_creative_media_pack(**_: object) -> dict:
        return {
            "success": True,
            "media_pack_id": "pack_no_playable_001",
            "media_assets": [
                {
                    "asset_id": "asset_meta_only_001",
                    "asset_type": "video",
                    "media_type": "video",
                    "status": "provider_execution_attempted_no_asset_url",
                    "playable": False,
                    "metadata_only": True,
                }
            ],
            "generation_jobs": [
                {
                    "job_id": "runway_job_missing_output",
                    "media_type": "video",
                    "provider": "runway",
                    "status": "provider_execution_attempted_no_asset_url",
                    "live_generation_available": True,
                    "live_provider_execution_attempted": True,
                }
            ],
            "provider_execution_results": [
                {
                    "provider": "runway",
                    "status": "provider_execution_attempted_no_asset_url",
                    "execution_status": "provider_execution_attempted_no_asset_url",
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

    def fake_fallback(**_: object) -> dict:
        return {
            "success": True,
            "status": "ugc_live_media_execution_completed",
            "fallback_runtime": "direct_live_media",
            "persisted_asset_count": 1,
            "playable_asset_count": 1,
            "persisted_asset_records": [
                {
                    "asset_id": "fallback_asset_001",
                    "asset_type": "audio",
                    "status": "persisted",
                    "playable": True,
                    "preview_ready": True,
                    "download_ready": True,
                    "storage_provider": "local",
                }
            ],
            "credential_values_exposed": False,
        }

    shared_media.generate_creative_media_pack = fake_generate_creative_media_pack
    ugc_bridge.run_admin_ugc_live_media_execution_fallback = fake_fallback
    try:
        job = media_jobs.enqueue_media_job(
            task="Create fallback media deliverable.",
            agent_id="ugc_creative_agent",
            tenant_id="owner_admin",
            include_image=False,
            include_audio=True,
            include_video=True,
            include_avatar=False,
        )
        result = media_jobs.process_media_job(job)
    finally:
        shared_media.generate_creative_media_pack = original_generate
        ugc_bridge.run_admin_ugc_live_media_execution_fallback = original_fallback

    assert result["success"] is True
    assert result["job"]["status"] == "completed"
    assert result["job"]["direct_fallback_used"] is True
    assert result["job"]["playable_asset_created"] is True
    assert result["job"]["signed_delivery_created"] is True
    assert result["job"]["metadata_only"] is False
    assert result["job"]["credential_values_exposed"] is False


if __name__ == "__main__":
    test_runway_async_job_response_is_polling_not_failed()
    test_example_provider_output_url_is_rejected_and_not_playable()
    test_placeholder_mock_and_test_urls_are_rejected()
    test_valid_provider_output_url_remains_persistable()
    test_embedded_audio_data_url_is_materialized_and_signed_delivery_created()
    test_provider_failure_returns_safe_diagnostics_without_secrets()
    test_media_job_stays_processing_when_provider_is_polling()
    test_direct_fallback_path_persists_local_playable_asset()
    test_media_job_uses_direct_fallback_when_provider_output_not_playable()
    print("PROVIDER_RESULT_PERSISTENCE_PASSED")
    sys.stdout.flush()