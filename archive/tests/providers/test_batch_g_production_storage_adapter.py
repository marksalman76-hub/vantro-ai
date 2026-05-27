import json

from backend.app.media.production_storage_adapter import (
    build_public_asset_url,
    prepare_upload_reference,
    storage_status,
)

status = storage_status()
upload = prepare_upload_reference(
    tenant_id="client_batch_g_storage_test",
    filename="campaign-preview.png",
    content_type="image/png",
)
public_url = build_public_asset_url("tenants/client_batch_g_storage_test/media/campaign-preview.png")

results = {
    "status_success": status.get("success") is True,
    "fallback_ready": status.get("fallback") == "durable_media_registry",
    "supported_supabase": "supabase" in status.get("supported_providers", []),
    "supported_r2": "r2" in status.get("supported_providers", []),
    "supported_s3": "s3" in status.get("supported_providers", []),
    "upload_reference_success": upload.get("success") is True,
    "object_key_created": upload.get("object_key") == "tenants/client_batch_g_storage_test/media/campaign-preview.png",
    "public_url_created": bool(public_url),
    "upload_ready_or_fallback": upload.get("upload_ready") is True or upload.get("fallback_registry_ready") is True,
    "status": status,
    "upload": upload,
    "public_url": public_url,
}

print("BATCH_G_PRODUCTION_STORAGE_RESULTS")
print(json.dumps(results, indent=2))

required = [
    "status_success",
    "fallback_ready",
    "supported_supabase",
    "supported_r2",
    "supported_s3",
    "upload_reference_success",
    "object_key_created",
    "public_url_created",
    "upload_ready_or_fallback",
]

if not all(results[k] for k in required):
    raise SystemExit("BATCH_G_PRODUCTION_STORAGE_FAILED")

print("BATCH_G_PRODUCTION_STORAGE_OK")
