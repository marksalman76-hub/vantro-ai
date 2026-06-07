from __future__ import annotations

import base64
import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.app.runtime import canonical_product_asset_metadata_runtime as runtime
from backend.app.runtime import creative_product_asset_library as library


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
def patched_asset_root():
    old_root = library.ASSET_ROOT
    old_registry = library.REGISTRY_PATH
    with TemporaryDirectory() as temp_dir:
        library.ASSET_ROOT = Path(temp_dir)
        library.REGISTRY_PATH = library.ASSET_ROOT / "creative_product_asset_registry.json"
        try:
            yield library.ASSET_ROOT
        finally:
            library.ASSET_ROOT = old_root
            library.REGISTRY_PATH = old_registry


def reset_env_dev() -> None:
    for key in ["DATABASE_URL", "POSTGRES_URL", "ENVIRONMENT", "APP_ENV", "FASTAPI_ENV", "NODE_ENV", "RENDER", "VERCEL_ENV", "PRODUCTION"]:
        os.environ.pop(key, None)
    runtime.reset_dev_product_asset_metadata_for_tests()


def encoded_png() -> str:
    return base64.b64encode(b"fake-png-bytes").decode("ascii")


def test_record_list_get_product_asset() -> None:
    reset_env_dev()
    recorded = runtime.record_product_asset(
        asset_id="product_asset_test_001",
        tenant_id="tenant_product_001",
        project_id="campaign_001",
        uploaded_by="client",
        asset_type="product_image",
        filename="hero.png",
        original_filename="hero.png",
        mime_type="image/png",
        byte_size=14,
        checksum="abc123",
        storage_provider="supabase",
        bucket="creative-product-assets",
        object_key="tenants/tenant_product_001/product_image/hero.png",
        preview_ready=True,
        download_ready=True,
    )
    assert recorded["success"] is True
    assert recorded["dev_only"] is True
    asset = recorded["asset"]
    assert asset["asset_id"] == "product_asset_test_001"
    assert asset["preview_ready"] is True
    assert asset["download_ready"] is True
    assert asset["storage_bucket"] == "creative-product-assets"

    listed = runtime.list_product_assets(tenant_id="tenant_product_001", project_id="campaign_001")
    assert listed["asset_count"] == 1
    assert listed["assets"][0]["asset_id"] == "product_asset_test_001"

    fetched = runtime.get_product_asset("product_asset_test_001", tenant_id="tenant_product_001")
    assert fetched["success"] is True
    assert fetched["asset"]["asset_type"] == "product_image"


def test_preview_download_readiness_not_unconditional() -> None:
    reset_env_dev()
    recorded = runtime.record_product_asset(
        asset_id="product_asset_local_only",
        tenant_id="tenant_product_001",
        asset_type="reference_asset",
        filename="brief.pdf",
        mime_type="application/pdf",
        storage_provider="local_runtime_fallback",
        local_path="runtime_outputs/creative_product_assets/brief.pdf",
        preview_ready=True,
        download_ready=True,
    )
    asset = recorded["asset"]
    assert asset["preview_ready"] is False
    assert asset["download_ready"] is False


def test_upload_metadata_records_storage_fields_and_checksum() -> None:
    reset_env_dev()
    with patched_asset_root():
        uploaded = library.upload_creative_product_asset(
            tenant_id="tenant_upload_001",
            filename="catalog.png",
            content_base64=encoded_png(),
            asset_type="product",
            uploaded_by="client",
            campaign_id="campaign_upload_001",
            metadata={"token": "hidden", "safe_note": "keep"},
        )
    assert uploaded["success"] is True
    assert uploaded["authority"] == "backend_canonical"
    assert uploaded["credential_values_exposed"] is False
    asset = uploaded["asset"]
    assert asset["storage_provider"] == "local_runtime_fallback"
    assert asset["bucket"] == ""
    assert asset["object_key"] == ""
    assert asset["sha256"]
    assert asset["preview_ready"] is False
    assert asset["download_ready"] is False
    assert "token" not in asset["metadata"]

    listed = library.list_creative_product_assets(tenant_id="tenant_upload_001", campaign_id="campaign_upload_001")
    assert listed["asset_count"] == 1
    assert listed["assets"][0]["asset_id"] == asset["asset_id"]


def test_delete_tombstones_product_asset() -> None:
    reset_env_dev()
    runtime.record_product_asset(
        asset_id="product_asset_delete_001",
        tenant_id="tenant_product_001",
        asset_type="logo",
        filename="logo.png",
        storage_provider="supabase",
        bucket="creative-product-assets",
        object_key="tenants/tenant_product_001/logo/logo.png",
        preview_ready=True,
        download_ready=True,
    )
    deleted = runtime.delete_product_asset(asset_id="product_asset_delete_001", tenant_id="tenant_product_001", actor_role="owner_admin")
    assert deleted["success"] is True
    assert deleted["status"] == "deleted"
    assert deleted["asset"]["deleted_at"]
    assert deleted["asset"]["preview_ready"] is False
    assert runtime.get_product_asset("product_asset_delete_001", tenant_id="tenant_product_001")["success"] is False


def test_event_recording_scrubs_sensitive_payload() -> None:
    reset_env_dev()
    event = runtime.record_product_asset_event(
        asset_id="product_asset_event_001",
        tenant_id="tenant_product_001",
        project_id="campaign_001",
        event_type="asset_uploaded",
        actor_role="client",
        payload={"password": "hidden", "safe": True},
    )
    assert event["success"] is True
    assert event["event"]["payload"]["safe"] is True
    assert "password" not in event["event"]["payload"]


def test_dev_fallback_marked_dev_only() -> None:
    reset_env_dev()
    readiness = runtime.ensure_product_asset_metadata_tables()
    assert readiness["success"] is True
    assert readiness["storage_mode"] == "dev_memory"
    assert readiness["dev_only"] is True
    assert readiness["production_fail_closed"] is False


def test_production_unavailable_fails_closed() -> None:
    reset_env_dev()
    with patched_env(APP_ENV="production", DATABASE_URL=None, POSTGRES_URL=None):
        readiness = runtime.ensure_product_asset_metadata_tables()
        uploaded = library.upload_creative_product_asset(
            tenant_id="tenant_upload_001",
            filename="catalog.png",
            content_base64=encoded_png(),
            asset_type="product",
            uploaded_by="client",
        )
    assert readiness["success"] is False
    assert readiness["production_fail_closed"] is True
    assert uploaded["success"] is False
    assert uploaded["production_fail_closed"] is True
    assert uploaded["credential_values_exposed"] is False


def test_compatibility_wrapper_preserves_existing_response_shape() -> None:
    reset_env_dev()
    with patched_asset_root():
        uploaded = library.upload_creative_product_asset(
            tenant_id="tenant_shape_001",
            filename="reference.png",
            content_base64=encoded_png(),
            asset_type="reference",
            campaign_id="campaign_shape_001",
        )
    assert uploaded["success"] is True
    assert uploaded["status"] == "creative_product_asset_uploaded"
    assert uploaded["asset_id"] == uploaded["asset"]["asset_id"]
    assert uploaded["storage_provider"] == uploaded["asset"]["storage_provider"]
    assert uploaded["authority"] == "backend_canonical"

    listed = library.list_creative_product_assets(tenant_id="tenant_shape_001", campaign_id="campaign_shape_001")
    assert listed["success"] is True
    assert listed["layer"] == "creative_product_asset_library"
    assert isinstance(listed["assets"], list)
    assert listed["credential_values_exposed"] is False


def test_client_route_uses_client_backend_authority_and_hides_credentials() -> None:
    client_list = Path("frontend/src/app/api/client-creative-product-assets/route.ts").read_text(encoding="utf-8")
    client_upload = Path("frontend/src/app/api/client-creative-product-assets-upload/route.ts").read_text(encoding="utf-8")
    assert "/client/creative/product-assets" in client_list
    assert "/admin/creative/product-assets" not in client_list
    assert "/client/creative/product-assets/upload" in client_upload
    assert "/admin/creative/product-assets/upload" not in client_upload
    assert "credential_values_exposed: false" in client_list
    assert "credential_values_exposed: false" in client_upload


if __name__ == "__main__":
    test_record_list_get_product_asset()
    test_preview_download_readiness_not_unconditional()
    test_upload_metadata_records_storage_fields_and_checksum()
    test_delete_tombstones_product_asset()
    test_event_recording_scrubs_sensitive_payload()
    test_dev_fallback_marked_dev_only()
    test_production_unavailable_fails_closed()
    test_compatibility_wrapper_preserves_existing_response_shape()
    test_client_route_uses_client_backend_authority_and_hides_credentials()
    print("CANONICAL_PRODUCT_ASSET_METADATA_RUNTIME_PASSED")
