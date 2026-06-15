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
    secrets = load_module(
        "backend/app/runtime/secrets_manager_config_boundary.py",
        "secrets_manager_config_boundary_under_test",
    )
    aws_contract = load_module(
        "backend/app/runtime/aws_option_a_runtime_contract.py",
        "aws_option_a_runtime_contract_for_secrets_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_secrets_test",
    )

    source = read("backend/app/runtime/secrets_manager_config_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for marker in [
        "import boto3",
        "from boto3",
        "get_secret_value(",
        "secretsmanager",
        "SecretId=",
        "requests.",
        "httpx.",
        "subprocess.",
    ]:
        require(marker not in source, f"AWS-10 boundary must not contain live secret/network marker: {marker}")

    env = {
        "AWS_OPTION_A_ENABLED": "true",
        "AWS_REGION": "ap-southeast-2",
        "AWS_PROVIDER_SECRETS_PREFIX": "/prod/ecommerce-ai-agent-platform",
        "RUNWAY_API_KEY": "RUNWAY_VALUE_MUST_NOT_LEAK",
        "ELEVENLABS_API_KEY": "ELEVENLABS_VALUE_MUST_NOT_LEAK",
        "OPENAI_API_KEY": "OPENAI_VALUE_MUST_NOT_LEAK",
        "STRIPE_SECRET_KEY": "STRIPE_VALUE_MUST_NOT_LEAK",
        "STRIPE_WEBHOOK_SECRET": "STRIPE_WEBHOOK_VALUE_MUST_NOT_LEAK",
        "DATABASE_URL": "postgres://USER:PASSWORD_VALUE_MUST_NOT_LEAK@example/db",
        "AWS_MEDIA_S3_BUCKET": "future-media-bucket",
        "AWS_UPLOADS_S3_BUCKET": "future-upload-bucket",
        "AWS_MEDIA_QUEUE_URL": "https://sqs.example/media",
        "AWS_MEDIA_DLQ_URL": "https://sqs.example/media-dlq",
        "JWT_SECRET": "JWT_VALUE_MUST_NOT_LEAK",
        "ADMIN_PLATFORM_TOKEN": "ADMIN_TOKEN_VALUE_MUST_NOT_LEAK",
        "CLIENT_PORTAL_SESSION_SECRET": "CLIENT_SESSION_VALUE_MUST_NOT_LEAK",
        "WEBHOOK_SIGNING_SECRET": "WEBHOOK_VALUE_MUST_NOT_LEAK",
        "SENTRY_DSN": "SENTRY_VALUE_MUST_NOT_LEAK",
        "IMAGE_GENERATION_PROVIDER_API_KEY": "IMAGE_PROVIDER_VALUE_MUST_NOT_LEAK",
        "AVATAR_PRESENTER_PROVIDER_API_KEY": "AVATAR_PROVIDER_VALUE_MUST_NOT_LEAK",
        "LIP_SYNC_PROVIDER_API_KEY": "LIPSYNC_PROVIDER_VALUE_MUST_NOT_LEAK",
        "MUSIC_SFX_PROVIDER_API_KEY": "MUSIC_SFX_VALUE_MUST_NOT_LEAK",
        "CAPTION_TRANSCRIPTION_PROVIDER_API_KEY": "CAPTION_PROVIDER_VALUE_MUST_NOT_LEAK",
        "COMPOSITION_RENDERING_SERVICE_API_KEY": "RENDER_PROVIDER_VALUE_MUST_NOT_LEAK",
        "MEDIA_DELIVERY_SERVICE_API_KEY": "DELIVERY_PROVIDER_VALUE_MUST_NOT_LEAK",
        "MEDIA_MODERATION_PROVIDER_API_KEY": "MODERATION_PROVIDER_VALUE_MUST_NOT_LEAK",
        "FALLBACK_MEDIA_PROVIDER_API_KEY": "FALLBACK_PROVIDER_VALUE_MUST_NOT_LEAK",
        "PLUGGABLE_MEDIA_PROVIDER_API_KEY": "PLUGGABLE_PROVIDER_VALUE_MUST_NOT_LEAK",
    }
    env_before = dict(env)
    inventory = secrets.build_secret_inventory(env)
    admin_view = secrets.build_admin_safe_secret_readiness_view(env)
    client_view = secrets.build_client_safe_secret_readiness_view(env)
    readiness = secrets.build_secrets_manager_boundary_readiness(env)
    validation = secrets.validate_secret_inventory_no_values(inventory)
    aws_readiness_before = aws_contract.aws_option_a_readiness(env_before)
    aws_readiness_after = aws_contract.aws_option_a_readiness(env)

    require(env == env_before, "Secrets boundary must not mutate current environment mapping.")
    require(aws_readiness_before == aws_readiness_after, "Secrets boundary must not change current AWS env behavior.")
    require(validation["valid"] is True, f"Secret inventory should validate without values: {validation}")
    require(readiness["valid"] is True, "Secrets boundary readiness should be valid.")
    require(readiness["aws_fetch_attempted"] is False, "Secrets boundary must not fetch from AWS.")
    require(readiness["secrets_manager_call_attempted"] is False, "Secrets boundary must not call Secrets Manager.")
    require(readiness["credentials_required_now"] is False, "Secrets boundary must not require AWS credentials.")
    require(readiness["provider_execution_changed"] is False, "Secrets boundary must not change provider execution.")
    require(readiness["stripe_behavior_changed"] is False, "Secrets boundary must not change Stripe behavior.")
    require(readiness["auth_session_behavior_changed"] is False, "Secrets boundary must not change auth/session behavior.")
    require(readiness["frontend_behavior_changed"] is False, "Secrets boundary must not change frontend behavior.")

    expected_categories = {
        "media_providers",
        "llm_api_providers",
        "stripe_billing",
        "rds_database",
        "s3_storage",
        "sqs_queue",
        "auth_session_admin_tokens",
        "client_portal_session",
        "integrations_webhooks",
        "observability",
    }
    require(expected_categories.issubset(set(inventory["categories"])), "AWS-10 must cover the full paid SaaS secret/config surface.")
    require(inventory["total_secret_reference_count"] >= 25, "AWS-10 inventory should include broad platform secret/config references.")
    expected_media_capability_groups = {
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
    require(
        expected_media_capability_groups.issubset(set(inventory["media_secret_capability_groups"])),
        "AWS-10B must cover the complete pluggable production media secret surface, not only named current providers.",
    )

    serialized_inventory = str(inventory)
    serialized_admin = str(admin_view)
    serialized_client = str(client_view)
    for forbidden_value in [
        "RUNWAY_VALUE_MUST_NOT_LEAK",
        "ELEVENLABS_VALUE_MUST_NOT_LEAK",
        "OPENAI_VALUE_MUST_NOT_LEAK",
        "STRIPE_VALUE_MUST_NOT_LEAK",
        "STRIPE_WEBHOOK_VALUE_MUST_NOT_LEAK",
        "PASSWORD_VALUE_MUST_NOT_LEAK",
        "JWT_VALUE_MUST_NOT_LEAK",
        "ADMIN_TOKEN_VALUE_MUST_NOT_LEAK",
        "CLIENT_SESSION_VALUE_MUST_NOT_LEAK",
        "WEBHOOK_VALUE_MUST_NOT_LEAK",
        "SENTRY_VALUE_MUST_NOT_LEAK",
        "IMAGE_PROVIDER_VALUE_MUST_NOT_LEAK",
        "AVATAR_PROVIDER_VALUE_MUST_NOT_LEAK",
        "LIPSYNC_PROVIDER_VALUE_MUST_NOT_LEAK",
        "MUSIC_SFX_VALUE_MUST_NOT_LEAK",
        "CAPTION_PROVIDER_VALUE_MUST_NOT_LEAK",
        "RENDER_PROVIDER_VALUE_MUST_NOT_LEAK",
        "DELIVERY_PROVIDER_VALUE_MUST_NOT_LEAK",
        "MODERATION_PROVIDER_VALUE_MUST_NOT_LEAK",
        "FALLBACK_PROVIDER_VALUE_MUST_NOT_LEAK",
        "PLUGGABLE_PROVIDER_VALUE_MUST_NOT_LEAK",
    ]:
        require(forbidden_value not in serialized_inventory, f"Inventory leaked raw secret value: {forbidden_value}")
        require(forbidden_value not in serialized_admin, f"Admin view leaked raw secret value: {forbidden_value}")
        require(forbidden_value not in serialized_client, f"Client view leaked raw secret value: {forbidden_value}")

    for ref in inventory["secret_references"]:
        require("value_present" in ref, "Each secret reference must include value_present boolean.")
        require(isinstance(ref["value_present"], bool), "value_present must be boolean only.")
        require("value" not in ref, "Secret reference must not serialize a raw value key.")
        require("current_value" not in ref, "Secret reference must not serialize current_value.")
        require("secret_value" not in ref, "Secret reference must not serialize secret_value.")
        require(ref["aws_fetch_attempted"] is False, "Secret reference must not fetch AWS.")
        require(ref["secrets_manager_call_attempted"] is False, "Secret reference must not call Secrets Manager.")
        require(ref["credentials_required_now"] is False, "Secret reference must not require credentials now.")
        require(ref["future_secrets_manager_name"].startswith("/"), "Future Secrets Manager name placeholder must be path-like.")
        require(ref["status"] in {"env_placeholder_present", "missing", "not_configured"}, "Unexpected secret readiness status.")
        if ref["category"] == "media_providers":
            require(ref["capability_group"] in expected_media_capability_groups, "Media provider reference missing broad capability group.")

    runway_ref = next(ref for ref in inventory["secret_references"] if ref["logical_name"] == "runway_provider_key")
    require(runway_ref["current_env_name"] == "RUNWAY_API_KEY", "Admin inventory must preserve current env name for Runway.")
    require(runway_ref["value_present"] is True, "Runway key presence must be represented as boolean true.")
    require(runway_ref["status"] == "env_placeholder_present", "Present env placeholder should report env_placeholder_present.")
    require(runway_ref["capability_group"] == "video_generation_providers", "Runway must remain a current video provider example.")
    elevenlabs_ref = next(ref for ref in inventory["secret_references"] if ref["logical_name"] == "elevenlabs_provider_key")
    require(elevenlabs_ref["capability_group"] == "audio_voice_providers", "ElevenLabs must remain a current audio/voice provider example.")

    required_future_media_placeholders = {
        "future_video_generation_provider_adapter",
        "future_image_generation_provider_adapter",
        "future_audio_voice_provider_adapter",
        "future_avatar_human_presenter_provider_adapter",
        "future_lip_sync_provider_adapter",
        "future_music_sfx_provider_adapter",
        "future_caption_transcription_provider_adapter",
        "future_composition_rendering_service_adapter",
        "future_storage_delivery_service_adapter",
        "future_moderation_safety_provider_adapter",
        "future_fallback_media_provider_adapter",
        "future_pluggable_media_provider_adapter",
    }
    logical_names = {ref["logical_name"] for ref in inventory["secret_references"]}
    require(
        required_future_media_placeholders.issubset(logical_names),
        "AWS-10B must include future/pluggable media provider placeholders.",
    )

    missing_inventory = secrets.build_secret_inventory({})
    missing_runway = next(ref for ref in missing_inventory["secret_references"] if ref["logical_name"] == "runway_provider_key")
    optional_kling = next(ref for ref in missing_inventory["secret_references"] if ref["logical_name"] == "kling_provider_key")
    require(missing_runway["value_present"] is False, "Missing secret presence must be boolean false.")
    require(missing_runway["status"] == "missing", "Required missing secret should report missing.")
    require(optional_kling["status"] == "not_configured", "Optional missing secret should report not_configured.")

    for hidden in [
        "RUNWAY_API_KEY",
        "STRIPE_SECRET_KEY",
        "DATABASE_URL",
        "AWS_MEDIA_QUEUE_URL",
        "JWT_SECRET",
        "ADMIN_PLATFORM_TOKEN",
        "IMAGE_GENERATION_PROVIDER_API_KEY",
        "AVATAR_PRESENTER_PROVIDER_API_KEY",
        "PLUGGABLE_MEDIA_PROVIDER_API_KEY",
        "future_secrets_manager_name",
        "secret_references",
        "media_secret_capability_groups",
        "missing_required_logical_names",
    ]:
        require(hidden not in serialized_client, f"Client-safe view must hide secret/internal name: {hidden}")
    require(client_view["credential_values_exposed"] is False, "Client view must not expose credential values.")
    require(client_view["internal_config_exposed"] is False, "Client view must not expose internal config.")

    require("RUNWAY_API_KEY" in serialized_admin, "Admin-safe view may include env names for readiness.")
    require("future_secrets_manager_name" in serialized_admin, "Admin-safe view must include future Secrets Manager placeholders.")
    require(admin_view["credential_values_exposed"] is False, "Admin view must not expose credential values.")
    require(admin_view["provider_secret_values_visible"] is False, "Admin view must not expose provider secret values.")

    visible = catalogue.list_final_approved_visible_agents()
    enterprise_selectable = catalogue.list_client_selectable_agents("enterprise")
    system_keys = {agent["key"] for agent in catalogue.SYSTEM_AGENTS}
    selectable_keys = {agent["key"] for agent in enterprise_selectable["agents"]}
    require(visible["count"] == 27, "AWS-10 must not alter final 27 visible catalogue count.")
    require(enterprise_selectable["count"] == 27, "AWS-10 must not alter enterprise selectable count.")
    require(not system_keys.intersection(selectable_keys), "AWS-10 must not expose SYSTEM_AGENTS as client-selectable.")

    for marker in [
        "AWS-10",
        "Secrets Manager config boundary",
        "verify_secrets_manager_config_boundary.py",
        "no AWS/Secrets Manager call",
        "full paid SaaS secret/config surface",
        "value_present booleans only",
        "pluggable media provider adapters",
        "broad media capability groups",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-10 marker: {marker}")

    print("SECRETS_MANAGER_CONFIG_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
