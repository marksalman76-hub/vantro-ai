from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.app.runtime.ai_media_live_provider_execution import execute_ai_media_provider_ready_packet
from backend.app.runtime import creative_asset_persistence_bridge as bridge
from backend.app.runtime.asset_storage_signed_delivery_runtime import (
    create_asset_record,
    create_signed_asset_delivery_packet,
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
def provider_env_disabled():
    keys = [
        "OPENAI_API_KEY",
        "RUNWAYML_API_SECRET",
        "KLING_ACCESS_KEY",
        "KLING_SECRET_KEY",
        "HEYGEN_API_KEY",
        "ELEVENLABS_API_KEY",
        "LIVE_EXTERNAL_CALLS_ENABLED",
        "OWNER_APPROVED_LIVE_ACTIVATION",
        "REAL_PROVIDER_HTTP_DISPATCH_ENABLED",
    ]
    original = {key: os.environ.get(key) for key in keys}
    for key in keys:
        os.environ.pop(key, None)
    try:
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_provider_unavailable_diagnostics_are_safe_and_explicit() -> None:
    with provider_env_disabled():
        result = execute_ai_media_provider_ready_packet(
            {
                "packet_type": "creative_media_provider_execution_packet",
                "execution_allowed": True,
                "primary_provider_slot": "elevenlabs",
                "provider_parameters": {
                    "provider": "elevenlabs",
                    "media_type": "audio",
                    "prompt": "Generate voiceover",
                },
            }
        )

    assert result["execution_status"] == "prepared_no_live_provider_configured"
    assert result["credential_values_exposed"] is False
    assert result["live_provider_execution_attempted"] is True
    route = result.get("route") or {}
    assert route.get("provider_available") is False
    assert route.get("live_dispatch_enabled") is False


def test_completed_without_playable_source_is_not_persisted_as_completed() -> None:
    with isolated_creative_registry():
        persisted = bridge.persist_creative_asset(
            {
                "agent_id": "ugc_creative_agent",
                "provider": "elevenlabs",
                "asset_type": "audio",
                "title": "Voiceover asset",
                "status": "completed",
                "summary": "Provider completed with metadata only",
            }
        )

        assert persisted["success"] is True
        assert persisted["metadata_only"] is True
        assert persisted["playable"] is False
        assert persisted["credential_values_exposed"] is False

        listed = bridge.get_persisted_creative_assets(limit=5)
        assert listed["success"] is True
        asset = listed["assets"][0]
        assert asset["status"] == "metadata_only_not_playable"
        assert asset["metadata_only"] is True
        assert asset["playable"] is False


def test_signed_delivery_packet_exists_for_playable_asset_and_no_credential_leak() -> None:
    reset_asset_storage_for_tests()

    record = create_asset_record(
        tenant_id="owner_admin",
        request_id="req_signed_001",
        provider_key="elevenlabs",
        asset_type="audio",
        asset_status="completed",
        source_url="https://example.com/audio.mp3",
        metadata={"safe": True, "api_key": "should_be_removed"},
    )

    assert record["credential_values_exposed"] is False

    packet = create_signed_asset_delivery_packet(
        tenant_id="owner_admin",
        asset_id=record["asset_id"],
        delivery_type="preview",
    )

    assert packet["status"] == "ready"
    assert packet["signed_delivery_token_present"] is True
    assert packet["credential_values_exposed"] is False


if __name__ == "__main__":
    test_provider_unavailable_diagnostics_are_safe_and_explicit()
    test_completed_without_playable_source_is_not_persisted_as_completed()
    test_signed_delivery_packet_exists_for_playable_asset_and_no_credential_leak()
    print("PROVIDER_DELIVERY_DIAGNOSTICS_PASSED")
    sys.stdout.flush()
