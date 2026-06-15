from __future__ import annotations

from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parent


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8", errors="ignore")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise AssertionError(f"Could not load module: {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    assets = load_module(
        "backend/app/runtime/durable_asset_storage_adapter_boundary.py",
        "durable_asset_storage_adapter_boundary_under_test",
    )
    aws_contract = load_module(
        "backend/app/runtime/aws_option_a_runtime_contract.py",
        "aws_option_a_runtime_contract_for_asset_test",
    )
    source = read("backend/app/runtime/durable_asset_storage_adapter_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    local_ref = assets.build_asset_reference_from_local_path(
        "runtime_outputs/universal_complete_media/job_123/final.mp4",
        "final_video",
        asset_id="asset_local_aws04_test",
        customer_id="client_789",
        job_id="job_789",
        media_type="video",
        source_type="composed_output",
        created_by_role="system",
        provider="runway",
        provider_job_id="runway_job_789",
        source_metadata={
            "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
            "safe_stage": "composition",
        },
        correlation_id="corr_asset_local",
    )
    provider_ref = assets.build_asset_reference_from_url(
        "https://provider.example/output/final.mp4",
        "provider_video",
        asset_id="asset_url_aws04_test",
        customer_id="client_789",
        job_id="job_789",
        media_type="video",
        source_type="provider_output",
        content_type="video/mp4",
        provider="runway",
        source_metadata={"authorization": "Bearer SHOULD_NOT_LEAK"},
    )

    local_validation = assets.validate_asset_reference(local_ref)
    provider_validation = assets.validate_asset_reference(provider_ref)
    client_view = assets.build_client_safe_asset_view(local_ref)
    admin_view = assets.build_admin_safe_asset_view(local_ref)
    persisted = assets.persist_asset_reference_locally_or_noop(local_ref, env={"AWS_OPTION_A_ENABLED": "false"})
    enabled_result = assets.persist_asset_reference_locally_or_noop(local_ref, env={"AWS_OPTION_A_ENABLED": "true"})
    local_contract = aws_contract.aws_option_a_readiness({})

    require(local_validation["valid"] is True, f"Local path asset reference should validate: {local_validation}")
    require(provider_validation["valid"] is True, f"Provider URL asset reference should validate: {provider_validation}")
    require(local_ref["asset_id"] == "asset_local_aws04_test", "Asset reference must preserve asset_id.")
    require(local_ref["customer_id"] == "client_789", "Asset reference must preserve customer/account reference.")
    require(local_ref["job_id"] == "job_789", "Asset reference must preserve job_id.")
    require(local_ref["asset_type"] == "final_video", "Asset reference must preserve asset_type.")
    require(local_ref["media_type"] == "video", "Asset reference must preserve media_type.")
    require(local_ref["source_type"] == "composed_output", "Asset reference must preserve source_type.")
    require(local_ref["local_path"], "Local path reference must preserve local_path for admin/support use.")
    require(local_ref["future_s3"]["target_backend"] == "aws_s3", "Asset reference must include future S3 metadata.")
    require(local_ref["future_s3"]["s3_upload_enabled"] is False, "AWS-04 must not enable S3 upload.")
    require(local_ref["future_s3"]["requires_aws_credentials_now"] is False, "AWS-04 must not require AWS credentials.")

    require(provider_ref["client_safe_url"] == "https://provider.example/output/final.mp4", "Provider URL reference must preserve client URL.")
    require(provider_ref["storage_backend"] == "external_url", "Provider URL reference must use external_url storage backend.")

    for hidden_key in [
        "local_path",
        "future_s3",
        "admin_url",
        "provider_source_metadata",
        "diagnostics_visibility_rules",
        "storage_backend",
        "storage_key",
    ]:
        require(hidden_key not in client_view, f"Client-safe asset view must hide {hidden_key}.")
    require(client_view["client_safe_url"] is not None, "Client-safe asset view must expose client-safe URL field.")
    require(client_view["customer_safe"] is True, "Client-safe asset view must be customer_safe.")
    require(client_view["credential_values_exposed"] is False, "Client-safe asset view must not expose credentials.")

    require("local_path" in admin_view, "Admin-safe asset view must include local_path for support diagnostics.")
    require("future_s3" in admin_view, "Admin-safe asset view must include future_s3 metadata.")
    require("provider_source_metadata" in admin_view, "Admin-safe asset view must include provider/source metadata.")
    require("RUNWAY_SECRET_SHOULD_NOT_LEAK" not in str(admin_view), "Admin view must redact provider secret values.")
    require("SHOULD_NOT_LEAK" not in str(client_view), "Client view must not leak secret values.")
    require("SHOULD_NOT_LEAK" not in str(provider_ref), "Provider reference must redact secret values.")

    source_types = {
        "upload": "client_upload",
        "generated": "generated_image",
        "site": "generated_site_bundle",
        "document": "report_pdf",
        "evidence": "execution_evidence",
        "support_attachment": "support_attachment",
        "caption": "caption_file",
        "transcript": "transcript_file",
        "audio": "voiceover_audio",
        "thumbnail": "thumbnail",
        "preview": "preview_video",
    }
    for source_type, asset_type in source_types.items():
        ref = assets.build_asset_reference({
            "asset_id": f"asset_{source_type}",
            "source_type": source_type,
            "asset_type": asset_type,
            "client_safe_url": f"/assets/{source_type}",
        })
        result = assets.validate_asset_reference(ref)
        require(result["valid"] is True, f"Asset reference should support source_type={source_type}: {result}")

    require(local_contract["aws_option_a_enabled"] is False, "AWS Option A must remain disabled by default.")
    require(persisted["success"] is True, "AWS disabled asset boundary should accept local/no-op persistence.")
    require(persisted["status"] == "local_noop_asset_reference_persisted", "AWS disabled asset boundary must use local/no-op behavior.")
    require(persisted["s3_upload_attempted"] is False, "AWS disabled asset boundary must not upload to S3.")
    require(persisted["paid_provider_calls_started"] is False, "Asset boundary must not start provider calls.")
    require(persisted["portal_upload_behavior_changed"] is False, "Asset boundary must not rewrite portal upload behavior.")
    require(enabled_result["status"] == "aws_s3_adapter_not_enabled_yet", "AWS enabled path must remain disabled S3 stub.")
    require(enabled_result["s3_upload_attempted"] is False, "AWS-04 must not upload to live S3 even when env flag is true.")

    for marker in [
        "CanonicalAssetReference",
        "build_asset_reference_from_local_path",
        "build_asset_reference_from_url",
        "validate_asset_reference",
        "build_client_safe_asset_view",
        "build_admin_safe_asset_view",
        "LocalNoopAssetStorageAdapter",
        "persist_asset_reference_locally_or_noop",
        "SUPPORTED_SOURCE_TYPES",
    ]:
        require(marker in source, f"Asset adapter source missing marker: {marker}")

    for marker in [
        "AWS-04",
        "durable asset storage adapter boundary",
        "verify_durable_asset_storage_adapter_boundary.py",
        "local/no-op asset reference persistence",
        "S3-ready asset reference",
        "future non-media agent outputs",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-04 marker: {marker}")

    print("DURABLE_ASSET_STORAGE_ADAPTER_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
