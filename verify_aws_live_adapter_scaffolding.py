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


def assert_no_live_call(result: dict) -> None:
    for key in [
        "live_call_attempted",
        "db_connection_attempted",
        "migration_attempted",
        "sqs_send_attempted",
        "s3_upload_attempted",
        "secret_fetch_attempted",
        "aws_call_attempted",
        "credentials_required_now",
    ]:
        require(result.get(key) is False, f"AWS-14 scaffold must not perform live behavior: {key}")


def main() -> int:
    adapters = load_module(
        "backend/app/runtime/aws_live_adapter_scaffolding.py",
        "aws_live_adapter_scaffolding_under_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_aws14_test",
    )
    source = read("backend/app/runtime/aws_live_adapter_scaffolding.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for marker in [
        "import boto3",
        "from boto3",
        "psycopg",
        "sqlite3",
        ".connect(",
        ".execute(",
        ".send_message(",
        ".put_object(",
        ".upload_file(",
        "get_secret_value(",
        "requests.",
        "httpx.",
        "stripe.",
    ]:
        require(marker not in source, f"AWS-14 live adapter scaffold must not contain live SDK/network marker: {marker}")

    default_readiness = adapters.build_all_aws_live_adapter_readiness({})
    require(default_readiness["boundary"] == "aws14_live_adapter_scaffolding", "AWS-14 boundary marker missing.")
    require(default_readiness["all_disabled_by_default"] is True, "All adapters must be disabled by default.")
    require(default_readiness["credentials_required_now"] is False, "Default readiness must not require credentials.")
    require(default_readiness["network_call_attempted"] is False, "Default readiness must not attempt network calls.")
    require(default_readiness["db_connection_attempted"] is False, "Default readiness must not connect to DB.")
    require(default_readiness["sqs_send_attempted"] is False, "Default readiness must not send SQS.")
    require(default_readiness["s3_upload_attempted"] is False, "Default readiness must not upload S3.")
    require(default_readiness["secret_fetch_attempted"] is False, "Default readiness must not fetch secrets.")

    expected_flags = {
        "rds": "AWS_RDS_LIVE_ADAPTER_ENABLED",
        "sqs_dlq": "AWS_SQS_LIVE_ADAPTER_ENABLED",
        "s3": "AWS_S3_LIVE_ADAPTER_ENABLED",
        "secrets_manager": "AWS_SECRETS_MANAGER_LIVE_ADAPTER_ENABLED",
    }
    require(default_readiness["service_enable_flags"] == expected_flags, "AWS-14 service-specific enable flags must be explicit.")
    for service, readiness in default_readiness["adapters"].items():
        require(readiness["status"] == "disabled_by_default", f"{service} should be disabled by default.")
        require(readiness["live_behavior_authorized_by_flags"] is False, f"{service} should need AWS flag plus service flag.")
        require(readiness["live_behavior_implemented"] is False, f"{service} scaffold must not implement live behavior yet.")
        assert_no_live_call(readiness)

    enabled_env = {
        "AWS_OPTION_A_ENABLED": "true",
        "AWS_RDS_LIVE_ADAPTER_ENABLED": "true",
        "AWS_SQS_LIVE_ADAPTER_ENABLED": "true",
        "AWS_S3_LIVE_ADAPTER_ENABLED": "true",
        "AWS_SECRETS_MANAGER_LIVE_ADAPTER_ENABLED": "true",
        "AWS_REGION": "ap-southeast-2",
        "DATABASE_URL": "postgres://DB_SECRET_SHOULD_NOT_LEAK",
        "AWS_MEDIA_QUEUE_URL": "https://sqs.example/QUEUE_SHOULD_NOT_LEAK",
        "AWS_MEDIA_DLQ_URL": "https://sqs.example/DLQ_SHOULD_NOT_LEAK",
        "AWS_MEDIA_S3_BUCKET": "MEDIA_BUCKET_SHOULD_NOT_LEAK",
        "AWS_UPLOADS_S3_BUCKET": "UPLOAD_BUCKET_SHOULD_NOT_LEAK",
        "AWS_PROVIDER_SECRETS_PREFIX": "/SECRET_PREFIX_SHOULD_NOT_LEAK",
    }
    ready = adapters.build_all_aws_live_adapter_readiness(enabled_env)
    require(ready["all_disabled_by_default"] is False, "Enabled flags should change readiness away from default-disabled.")
    for service, readiness in ready["adapters"].items():
        require(readiness["live_behavior_authorized_by_flags"] is True, f"{service} should show double-flag authorization.")
        require(readiness["status"] == "live_adapter_scaffold_ready_not_executing", f"{service} should be scaffold-ready but non-executing.")
        require(readiness["live_behavior_implemented"] is False, f"{service} live behavior must remain unimplemented.")
        require(readiness["required_config_present"] is True, f"{service} required config presence should be detected as booleans.")
        assert_no_live_call(readiness)

    combined_text = str(ready)
    for forbidden_value in [
        "DB_SECRET_SHOULD_NOT_LEAK",
        "QUEUE_SHOULD_NOT_LEAK",
        "DLQ_SHOULD_NOT_LEAK",
        "MEDIA_BUCKET_SHOULD_NOT_LEAK",
        "UPLOAD_BUCKET_SHOULD_NOT_LEAK",
        "SECRET_PREFIX_SHOULD_NOT_LEAK",
    ]:
        require(forbidden_value not in combined_text, f"AWS-14 readiness leaked config/secret value: {forbidden_value}")

    rds_operation = adapters.RdsLiveAdapterScaffold(enabled_env).plan_repository_write({"job_id": "job_aws14_rds"})
    migration_operation = adapters.RdsLiveAdapterScaffold(enabled_env).plan_migration_dry_run({"migration_id": "migration_aws14"})
    sqs_operation = adapters.SqsDlqLiveAdapterScaffold(enabled_env).plan_send_message({"message_id": "msg_aws14", "job_id": "job_aws14_sqs"})
    s3_operation = adapters.S3LiveAdapterScaffold(enabled_env).plan_upload_asset({"asset_id": "asset_aws14", "job_id": "job_aws14_s3"})
    secret_operation = adapters.SecretsManagerLiveAdapterScaffold(enabled_env).plan_secret_fetch({"logical_name": "runway_provider_key"})
    for operation in [rds_operation, migration_operation, sqs_operation, s3_operation, secret_operation]:
        require(operation["live_behavior_implemented"] is False, "Operations must stay scaffold-only.")
        assert_no_live_call(operation)
    require(rds_operation["rds_write_attempted"] is False, "RDS scaffold must not write.")
    require(migration_operation["rds_write_attempted"] is False, "RDS migration scaffold must not write.")
    require(sqs_operation["dlq_send_attempted"] is False, "SQS/DLQ scaffold must not send DLQ.")
    require(s3_operation["signed_url_generated"] is False, "S3 scaffold must not generate signed URL.")
    require(secret_operation["secret_value_loaded"] is False, "Secrets scaffold must not load secret value.")

    admin_view = adapters.build_admin_safe_live_adapter_view(enabled_env)
    client_view = adapters.build_client_safe_live_adapter_view(enabled_env)
    require("adapters" in admin_view, "Admin view must include adapter readiness.")
    require("service_enable_flags" in admin_view, "Admin view must include enable flag names.")
    require("adapters" not in client_view, "Client view must hide adapter internals.")
    require("service_enable_flags" not in client_view, "Client view must hide flag names.")
    require(client_view["credentials_required_now"] is False, "Client view must show no credentials required.")
    require(client_view["network_call_attempted"] is False, "Client view must show no network call.")
    require(client_view["internal_config_exposed"] is False, "Client view must hide internal config.")
    require("DB_SECRET_SHOULD_NOT_LEAK" not in str(admin_view), "Admin view must not leak DB values.")
    require("SECRET_PREFIX_SHOULD_NOT_LEAK" not in str(admin_view), "Admin view must not leak secret prefix values.")

    expected_media_groups = {
        "video_generation_providers",
        "image_generation_providers",
        "audio_voice_providers",
        "avatar_human_presenter_providers",
        "lip_sync_providers",
        "music_sfx_providers",
        "caption_transcription_providers",
        "composition_rendering_services",
        "storage_delivery_services",
        "moderation_safety_providers",
        "fallback_providers",
        "future_pluggable_provider_adapters",
    }
    require(expected_media_groups.issubset(set(default_readiness["broad_media_capability_groups"])), "AWS-14 must preserve broad pluggable media stack coverage.")

    visible = catalogue.list_final_approved_visible_agents()
    enterprise_selectable = catalogue.list_client_selectable_agents("enterprise")
    system_keys = {agent["key"] for agent in catalogue.SYSTEM_AGENTS}
    selectable_keys = {agent["key"] for agent in enterprise_selectable["agents"]}
    require(visible["count"] == 27, "AWS-14 must not alter final 27 visible catalogue count.")
    require(enterprise_selectable["count"] == 27, "AWS-14 must not alter enterprise selectable count.")
    require(not system_keys.intersection(selectable_keys), "AWS-14 must not expose SYSTEM_AGENTS as client-selectable.")

    for marker in [
        "RdsLiveAdapterScaffold",
        "SqsDlqLiveAdapterScaffold",
        "S3LiveAdapterScaffold",
        "SecretsManagerLiveAdapterScaffold",
        "AWS_RDS_LIVE_ADAPTER_ENABLED",
        "AWS_SQS_LIVE_ADAPTER_ENABLED",
        "AWS_S3_LIVE_ADAPTER_ENABLED",
        "AWS_SECRETS_MANAGER_LIVE_ADAPTER_ENABLED",
        "build_all_aws_live_adapter_readiness",
    ]:
        require(marker in source, f"AWS-14 source missing marker: {marker}")

    for marker in [
        "AWS-14",
        "AWS live adapter scaffolding",
        "verify_aws_live_adapter_scaffolding.py",
        "disabled by default",
        "service-specific enable flags",
        "no DB/RDS/SQS/S3/Secrets Manager/AWS calls",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-14 marker: {marker}")

    print("AWS_LIVE_ADAPTER_SCAFFOLDING_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
