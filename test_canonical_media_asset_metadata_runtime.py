from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from backend.app.media.durable_media_store import list_media_assets as compat_list_media_assets
from backend.app.media.durable_media_store import register_media_asset as compat_register_media_asset
from backend.app.runtime import canonical_media_asset_metadata_runtime as runtime


@contextmanager
def patched_env(**values: str):
    previous = {key: os.environ.get(key) for key in values}
    try:
        for key, value in values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@contextmanager
def preserved_file(path: str):
    target = Path(path)
    existed = target.exists()
    original = target.read_bytes() if existed else b""
    try:
        yield
    finally:
        if existed:
            target.write_bytes(original)
        elif target.exists():
            target.unlink()


def reset_env_dev() -> None:
    for key in ["DATABASE_URL", "POSTGRES_URL", "ENVIRONMENT", "APP_ENV", "FASTAPI_ENV", "NODE_ENV", "RENDER", "VERCEL_ENV", "PRODUCTION"]:
        os.environ.pop(key, None)
    runtime.reset_dev_media_asset_metadata_for_tests()


def test_record_and_list_media_asset() -> None:
    reset_env_dev()
    recorded = runtime.record_media_asset(
        tenant_id="tenant_media_001",
        asset_id="asset_playable_001",
        asset_type="image",
        preview_url="https://cdn.example.com/asset.png",
        download_url="https://cdn.example.com/asset.png",
        preview_ready=True,
        download_ready=True,
        playable=True,
        metadata_only=False,
        source_runtime="test",
    )
    assert recorded["success"] is True
    assert recorded["dev_only"] is True
    listed = runtime.list_media_assets(tenant_id="tenant_media_001")
    assert listed["asset_count"] == 1
    assert listed["assets"][0]["asset_id"] == "asset_playable_001"
    assert listed["assets"][0]["authority"] if "authority" in listed["assets"][0] else True


def test_metadata_only_asset_is_not_playable_or_ready() -> None:
    reset_env_dev()
    recorded = runtime.record_media_asset(
        tenant_id="tenant_media_001",
        asset_id="asset_metadata_only_001",
        asset_type="creative_strategy",
        preview_ready=True,
        download_ready=True,
        playable=True,
        metadata_only=True,
        source_runtime="test",
    )
    asset = recorded["asset"]
    assert asset["metadata_only"] is True
    assert asset["playable"] is False
    assert asset["preview_ready"] is False
    assert asset["download_ready"] is False


def test_playable_asset_can_be_ready() -> None:
    reset_env_dev()
    recorded = runtime.record_media_asset(
        tenant_id="tenant_media_001",
        asset_id="asset_playable_002",
        asset_type="video",
        provider_url="https://provider.example.com/video.mp4",
        preview_url="https://provider.example.com/video.mp4",
        download_url="https://provider.example.com/video.mp4",
        preview_ready=True,
        download_ready=True,
        playable=True,
    )
    asset = recorded["asset"]
    assert asset["metadata_only"] is False
    assert asset["playable"] is True
    assert asset["preview_ready"] is True
    assert asset["download_ready"] is True


def test_link_asset_to_deliverable() -> None:
    reset_env_dev()
    runtime.record_media_asset(
        tenant_id="tenant_media_001",
        asset_id="asset_linked_001",
        preview_url="https://cdn.example.com/linked.png",
        playable=True,
        preview_ready=True,
    )
    linked = runtime.link_asset_to_deliverable(
        tenant_id="tenant_media_001",
        deliverable_id="deliverable_001",
        asset_id="asset_linked_001",
        execution_id="execution_001",
    )
    assert linked["success"] is True
    listed = runtime.list_deliverable_assets(tenant_id="tenant_media_001", deliverable_id="deliverable_001")
    assert listed["count"] == 1
    assert listed["assets"][0]["asset_id"] == "asset_linked_001"


def test_record_delivery_packet_and_access_event() -> None:
    reset_env_dev()
    packet = runtime.record_asset_delivery_packet(
        tenant_id="tenant_media_001",
        asset_id="asset_delivery_001",
        delivery_status="ready",
        preview_ready=True,
        signed_preview_url="/asset-delivery/preview/asset_delivery_001",
    )
    assert packet["success"] is True
    packets = runtime.list_asset_delivery_packets(tenant_id="tenant_media_001", asset_id="asset_delivery_001")
    assert packets["count"] == 1

    event = runtime.record_asset_access_event(
        tenant_id="tenant_media_001",
        asset_id="asset_delivery_001",
        event_type="preview_requested",
        actor_role="client",
        payload={"token": "should_be_removed", "safe": True},
    )
    assert event["success"] is True
    assert "token" not in event["event"]["payload"]


def test_dev_fallback_marked_dev_only() -> None:
    reset_env_dev()
    readiness = runtime.ensure_media_asset_metadata_tables()
    assert readiness["success"] is True
    assert readiness["storage_mode"] == "dev_memory"
    assert readiness["dev_only"] is True
    assert readiness["production_fail_closed"] is False


def test_production_unavailable_fails_closed() -> None:
    reset_env_dev()
    with patched_env(APP_ENV="production", DATABASE_URL=None, POSTGRES_URL=None):
        readiness = runtime.ensure_media_asset_metadata_tables()
    assert readiness["success"] is False
    assert readiness["production_fail_closed"] is True
    assert readiness["credential_values_exposed"] is False


def test_compatibility_wrapper_preserves_existing_response_shape() -> None:
    reset_env_dev()
    with preserved_file("backend/app/data/durable_media_registry.json"):
        asset = compat_register_media_asset(
            tenant_id="tenant_media_compat",
            url="https://cdn.example.com/compat.png",
            title="Compat Asset",
            asset_type="image",
        )
        assert asset["id"]
        assert asset["url"] == "https://cdn.example.com/compat.png"
        assert asset["title"] == "Compat Asset"
        assert asset["authority"] == "backend_canonical"
        listed = compat_list_media_assets("tenant_media_compat")
        assert listed
        assert listed[0]["url"] == "https://cdn.example.com/compat.png"


def test_frontend_media_route_authority_markers() -> None:
    text = Path("frontend/src/app/api/client-media-assets/route.ts").read_text(encoding="utf-8")
    for needle in [
        'authority: "backend_canonical"',
        'authority: "frontend_advisory"',
        "production_fail_closed: true",
        "fallback_used: true",
        "dev_only: true",
        "credential_values_exposed: false",
        "getMediaAssets",
        "getLatestMediaAsset",
    ]:
        assert needle in text


if __name__ == "__main__":
    test_record_and_list_media_asset()
    test_metadata_only_asset_is_not_playable_or_ready()
    test_playable_asset_can_be_ready()
    test_link_asset_to_deliverable()
    test_record_delivery_packet_and_access_event()
    test_dev_fallback_marked_dev_only()
    test_production_unavailable_fails_closed()
    test_compatibility_wrapper_preserves_existing_response_shape()
    test_frontend_media_route_authority_markers()
    print("CANONICAL_MEDIA_ASSET_METADATA_RUNTIME_PASSED")
