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
    s3_boundary = load_module(
        "backend/app/runtime/s3_asset_delivery_boundary.py",
        "s3_asset_delivery_boundary_under_test",
    )
    asset_boundary = load_module(
        "backend/app/runtime/durable_asset_storage_adapter_boundary.py",
        "durable_asset_storage_adapter_boundary_for_s3_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_s3_test",
    )

    source = read("backend/app/runtime/s3_asset_delivery_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    forbidden_runtime_call_markers = [
        "import boto3",
        "from boto3",
        ".put_object(",
        ".upload_file(",
        "generate_presigned_url(",
        "requests.",
        "httpx.",
        "subprocess.",
    ]
    for marker in forbidden_runtime_call_markers:
        require(marker not in source, f"AWS-09 boundary must not contain live upload/network marker: {marker}")

    local_asset = asset_boundary.build_asset_reference_from_local_path(
        "runtime_outputs/universal_complete_media/job_123/final.mp4",
        "final_video",
        asset_id="asset_s3_local_test",
        customer_id="client_789",
        account_id="acct_789",
        job_id="job_789",
        media_type="video",
        source_type="composed_output",
        source_metadata={
            "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
            "safe_stage": "composition",
        },
        correlation_id="corr_s3_local",
    )
    local_s3 = s3_boundary.build_s3_object_reference_from_asset_reference(
        local_asset,
        env={
            "AWS_REGION": "ap-southeast-2",
            "AWS_MEDIA_S3_BUCKET": "future-media-bucket",
            "AWS_UPLOADS_S3_BUCKET": "future-upload-bucket",
        },
    )
    provider_s3 = s3_boundary.build_s3_object_reference_from_provider_url(
        "https://provider.example/output/final.mp4",
        "provider_video",
        asset_id="asset_s3_provider_test",
        customer_id="client_789",
        job_id="job_789",
        source_type="provider_output",
        source_metadata={"authorization": "Bearer SHOULD_NOT_LEAK"},
    )

    validation = s3_boundary.validate_s3_object_reference(local_s3)
    require(validation["valid"] is True, f"Local S3 object reference should validate: {validation}")
    require(validation["s3_upload_attempted"] is False, "Validation must not upload to S3.")
    require(validation["aws_calls_started"] is False, "Validation must not start AWS calls.")
    require(validation["credentials_required_now"] is False, "Boundary must not require credentials now.")

    for key in [
        "asset_id",
        "job_id",
        "customer_id",
        "account_id",
        "asset_type",
        "source_type",
        "content_type",
        "size_bytes",
        "checksum_sha256",
        "s3_bucket",
        "s3_key",
        "aws_region",
        "storage_class",
        "client_safe_url",
        "admin_url",
        "support_url",
        "signed_url_required",
        "public_access_allowed",
        "retention_policy",
        "created_at",
    ]:
        require(key in local_s3, f"Canonical S3 object reference missing field: {key}")

    require(local_s3["asset_id"] == "asset_s3_local_test", "S3 reference must preserve asset_id.")
    require(local_s3["job_id"] == "job_789", "S3 reference must preserve job_id.")
    require(local_s3["customer_id"] == "client_789", "S3 reference must preserve customer reference.")
    require(local_s3["source_type"] == "composed_output", "S3 reference must preserve source_type.")
    require(local_s3["s3_bucket"] == "future-media-bucket", "Media asset should target the media bucket placeholder.")
    require(local_s3["aws_region"] == "ap-southeast-2", "S3 reference should preserve region placeholder.")
    require(local_s3["public_access_allowed"] is False, "Public access must default false.")
    require(local_s3["signed_url_required"] is True, "Signed URL must default true.")
    require(local_s3["s3_upload_attempted"] is False, "S3 reference builder must not upload.")
    require(local_s3["aws_calls_started"] is False, "S3 reference builder must not call AWS.")
    require(local_s3["credentials_required_now"] is False, "S3 reference builder must not require credentials.")
    require("RUNWAY_SECRET_SHOULD_NOT_LEAK" not in str(local_s3), "S3 reference must redact source secrets.")
    require("SHOULD_NOT_LEAK" not in str(provider_s3), "Provider S3 reference must redact source secrets.")

    key_strategy = local_s3["key_strategy"]
    for key in [
        "customer_namespace",
        "job_namespace",
        "asset_type_folder",
        "source_type_folder",
        "sanitized_filename",
        "collision_safe_suffix",
        "local_absolute_path_leaked_to_client",
    ]:
        require(key in key_strategy, f"S3 key strategy missing field: {key}")
    require(key_strategy["customer_namespace"] == "customers/client_789", "S3 key strategy must use customer namespace.")
    require(key_strategy["job_namespace"] == "jobs/job_789", "S3 key strategy must use job namespace.")
    require(key_strategy["sanitized_filename"] == "final.mp4", "S3 key strategy must sanitize filename only.")
    require("/" not in key_strategy["sanitized_filename"], "Sanitized filename must not include path separators.")
    require("\\" not in key_strategy["sanitized_filename"], "Sanitized filename must not include Windows path separators.")
    require(key_strategy["local_absolute_path_leaked_to_client"] is False, "S3 key strategy must declare no path leakage.")

    client_view = s3_boundary.build_client_safe_s3_delivery_view(local_s3)
    admin_view = s3_boundary.build_admin_safe_s3_readiness_view(local_s3)
    for hidden_key in [
        "local_path",
        "s3_bucket",
        "s3_key",
        "provider_url",
        "source_metadata",
        "admin_url",
        "support_url",
        "key_strategy",
        "retention_policy",
    ]:
        require(hidden_key not in client_view, f"Client-safe S3 delivery view must hide {hidden_key}.")
    require("runtime_outputs" not in str(client_view), "Client-safe view must not leak local runtime output paths.")
    require("future-media-bucket" not in str(client_view), "Client-safe view must not leak bucket names.")
    require("customers/client_789" not in str(client_view), "Client-safe view must not leak S3 key namespaces.")
    require(client_view["client_safe_url"] in ("", None), "Client-safe view should not invent a URL before signed delivery exists.")
    require(client_view["signed_url_required"] is True, "Client-safe view must show signed URL is required.")
    require(client_view["public_access_allowed"] is False, "Client-safe view must show public access is not allowed.")

    require(admin_view["local_path"].endswith("final.mp4"), "Admin-safe view may include local path for support.")
    require(admin_view["s3_bucket"] == "future-media-bucket", "Admin-safe view may include bucket placeholder.")
    require(admin_view["s3_key"], "Admin-safe view must include key placeholder.")
    require(admin_view["readiness"]["s3_upload_attempted"] is False, "Admin readiness must prove no S3 upload occurred.")
    require(admin_view["readiness"]["requires_aws_credentials_now"] is False, "Admin readiness must prove no credentials are required now.")
    require("RUNWAY_SECRET_SHOULD_NOT_LEAK" not in str(admin_view), "Admin view must redact secret values.")

    required_source_types = {
        "upload": "client_upload",
        "generated": "generated_image",
        "site": "generated_site_bundle",
        "document": "generated_document",
        "evidence": "execution_evidence",
        "support_attachment": "support_attachment",
        "provider_output": "provider_video",
        "composed_output": "final_video",
        "audio": "voiceover_audio",
        "caption": "caption_file",
        "transcript": "transcript_file",
        "thumbnail": "thumbnail",
        "preview": "preview_video",
    }
    for source_type, asset_type in required_source_types.items():
        ref = s3_boundary.build_s3_object_reference(
            {
                "asset_id": f"s3_{source_type}",
                "source_type": source_type,
                "asset_type": asset_type,
                "customer_id": "client_source_type",
                "job_id": "job_source_type",
                "filename": f"{source_type}.bin",
            },
            env={"AWS_MEDIA_S3_BUCKET": "future-media-bucket", "AWS_UPLOADS_S3_BUCKET": "future-upload-bucket"},
        )
        result = s3_boundary.validate_s3_object_reference(ref)
        require(result["valid"] is True, f"S3 boundary should support source_type={source_type}: {result}")
        if source_type == "upload":
            require(ref["s3_bucket"] == "future-upload-bucket", "Upload source type should target upload bucket placeholder.")

    readiness = s3_boundary.build_s3_delivery_boundary_readiness({})
    require(readiness["boundary"] == "aws09_s3_asset_delivery_boundary", "S3 readiness boundary marker missing.")
    require(readiness["requires_aws_credentials_now"] is False, "AWS-09 readiness must not require credentials.")
    require(readiness["s3_upload_attempted"] is False, "AWS-09 readiness must not upload to S3.")
    require(readiness["aws_calls_started"] is False, "AWS-09 readiness must not call AWS.")
    require(readiness["live_delivery_behavior_changed"] is False, "AWS-09 must not change live delivery behavior.")
    require(readiness["public_access_allowed_default"] is False, "AWS-09 must default public access false.")
    require(readiness["signed_url_required_default"] is True, "AWS-09 must default signed URL required.")

    visible = catalogue.list_final_approved_visible_agents()
    selectable = catalogue.list_client_selectable_agents()
    enterprise_selectable = catalogue.list_client_selectable_agents("enterprise")
    require(visible["count"] == 27, "AWS-09 must not alter final 27 visible catalogue count.")
    require(enterprise_selectable["count"] == 27, "AWS-09 must not alter enterprise-visible catalogue count.")
    system_keys = {agent["key"] for agent in catalogue.SYSTEM_AGENTS}
    selectable_keys = {agent["key"] for agent in selectable["agents"]}
    enterprise_selectable_keys = {agent["key"] for agent in enterprise_selectable["agents"]}
    require(not system_keys.intersection(selectable_keys), "AWS-09 must not expose SYSTEM_AGENTS as business-plan client-selectable.")
    require(not system_keys.intersection(enterprise_selectable_keys), "AWS-09 must not expose SYSTEM_AGENTS as enterprise client-selectable.")

    for marker in [
        "AWS-09",
        "S3 asset delivery boundary",
        "verify_s3_asset_delivery_boundary.py",
        "no S3 upload or AWS call",
        "client-safe asset delivery views",
        "admin-safe support/recovery views",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-09 marker: {marker}")

    print("S3_ASSET_DELIVERY_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
