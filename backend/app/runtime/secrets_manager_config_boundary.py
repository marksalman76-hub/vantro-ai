from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping, Optional
import re

from backend.app.runtime.aws_option_a_runtime_contract import aws_option_a_readiness


SECRET_CATEGORIES = {
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

MEDIA_SECRET_CAPABILITY_GROUPS = {
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

SENSITIVE_VALUE_KEYS = {
    "value",
    "current_value",
    "secret_value",
    "raw_value",
    "env_value",
    "token_value",
    "password_value",
    "credential_value",
}

PUBLIC_SECRET_READINESS_LABEL = "configured_secret_readiness_boundary"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def clean_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in {"1", "true", "yes", "on", "enabled"}:
        return True
    if text in {"0", "false", "no", "off", "disabled"}:
        return False
    return default


def sanitise_secret_path_segment(value: Any, fallback: str = "secret") -> str:
    text = clean_text(value, 180).lower()
    text = re.sub(r"[^a-z0-9/_-]+", "-", text).strip("/-_")
    return text or fallback


def value_is_present(env: Mapping[str, Any], env_names: Iterable[str]) -> bool:
    return any(clean_text(env.get(name)) != "" for name in env_names)


def redact_sensitive_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_VALUE_KEYS:
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_sensitive_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_sensitive_values(item) for item in value]
    return value


@dataclass(frozen=True)
class SecretInventoryDefinition:
    logical_name: str
    category: str
    current_env_name: str
    required_for: tuple[str, ...]
    tenant_scope: str = "platform"
    rotation_required: bool = True
    rotation_interval: str = "90d"
    alternative_env_names: tuple[str, ...] = ()
    optional: bool = False
    future_suffix: str = ""
    capability_group: str = ""


@dataclass(frozen=True)
class CanonicalSecretReference:
    secret_id: str
    logical_name: str
    category: str
    current_env_name: str
    alternative_env_names: list[str] = field(default_factory=list)
    future_secrets_manager_name: str = ""
    required_for: list[str] = field(default_factory=list)
    capability_group: str = ""
    tenant_scope: str = "platform"
    rotation_required: bool = True
    rotation_interval: str = "90d"
    status: str = "missing"
    value_present: bool = False
    last_checked_at: str = field(default_factory=utc_now)
    required_now: bool = False
    optional: bool = False
    aws_fetch_attempted: bool = False
    secrets_manager_call_attempted: bool = False
    credentials_required_now: bool = False
    current_env_behavior_changed: bool = False
    credential_values_exposed: bool = False
    customer_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return redact_sensitive_values(asdict(self))


SECRET_INVENTORY_DEFINITIONS: tuple[SecretInventoryDefinition, ...] = (
    SecretInventoryDefinition(
        logical_name="runway_provider_key",
        category="media_providers",
        current_env_name="RUNWAY_API_KEY",
        required_for=("runway_video_generation", "universal_complete_media"),
        future_suffix="providers/runway/api-key",
        capability_group="video_generation_providers",
    ),
    SecretInventoryDefinition(
        logical_name="elevenlabs_provider_key",
        category="media_providers",
        current_env_name="ELEVENLABS_API_KEY",
        required_for=("voiceover_generation", "universal_complete_media"),
        future_suffix="providers/elevenlabs/api-key",
        capability_group="audio_voice_providers",
    ),
    SecretInventoryDefinition(
        logical_name="kling_provider_key",
        category="media_providers",
        current_env_name="KLING_API_KEY",
        required_for=("fallback_video_generation",),
        optional=True,
        future_suffix="providers/kling/api-key",
        capability_group="fallback_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_video_generation_provider_adapter",
        category="media_providers",
        current_env_name="VIDEO_GENERATION_PROVIDER_API_KEY",
        required_for=("future_video_generation_adapter", "pluggable_media_stack"),
        optional=True,
        future_suffix="providers/media/video-generation/api-key",
        capability_group="video_generation_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_image_generation_provider_adapter",
        category="media_providers",
        current_env_name="IMAGE_GENERATION_PROVIDER_API_KEY",
        required_for=("future_image_generation_adapter", "product_visuals", "ad_creative_images"),
        optional=True,
        future_suffix="providers/media/image-generation/api-key",
        capability_group="image_generation_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_audio_voice_provider_adapter",
        category="media_providers",
        current_env_name="AUDIO_VOICE_PROVIDER_API_KEY",
        required_for=("future_audio_voice_adapter", "voiceover_generation"),
        optional=True,
        future_suffix="providers/media/audio-voice/api-key",
        capability_group="audio_voice_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_avatar_human_presenter_provider_adapter",
        category="media_providers",
        current_env_name="AVATAR_PRESENTER_PROVIDER_API_KEY",
        required_for=("future_avatar_presenter_adapter", "human_led_media"),
        optional=True,
        future_suffix="providers/media/avatar-human-presenter/api-key",
        capability_group="avatar_human_presenter_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_lip_sync_provider_adapter",
        category="media_providers",
        current_env_name="LIP_SYNC_PROVIDER_API_KEY",
        required_for=("future_lip_sync_adapter", "avatar_video_sync"),
        optional=True,
        future_suffix="providers/media/lip-sync/api-key",
        capability_group="lip_sync_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_music_sfx_provider_adapter",
        category="media_providers",
        current_env_name="MUSIC_SFX_PROVIDER_API_KEY",
        required_for=("future_music_sfx_adapter", "soundtrack_generation", "sound_effect_generation"),
        optional=True,
        future_suffix="providers/media/music-sfx/api-key",
        capability_group="music_sfx_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_caption_transcription_provider_adapter",
        category="media_providers",
        current_env_name="CAPTION_TRANSCRIPTION_PROVIDER_API_KEY",
        required_for=("future_caption_transcription_adapter", "captions", "transcripts"),
        optional=True,
        future_suffix="providers/media/caption-transcription/api-key",
        capability_group="caption_transcription_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_composition_rendering_service_adapter",
        category="media_providers",
        current_env_name="COMPOSITION_RENDERING_SERVICE_API_KEY",
        required_for=("future_composition_rendering_service", "cloud_rendering", "media_stitching"),
        optional=True,
        future_suffix="providers/media/composition-rendering/api-key",
        capability_group="composition_rendering_services",
    ),
    SecretInventoryDefinition(
        logical_name="future_storage_delivery_service_adapter",
        category="media_providers",
        current_env_name="MEDIA_DELIVERY_SERVICE_API_KEY",
        required_for=("future_media_delivery_service", "signed_asset_delivery", "cdn_delivery"),
        optional=True,
        future_suffix="providers/media/storage-delivery/api-key",
        capability_group="storage_delivery_services",
    ),
    SecretInventoryDefinition(
        logical_name="future_moderation_safety_provider_adapter",
        category="media_providers",
        current_env_name="MEDIA_MODERATION_PROVIDER_API_KEY",
        required_for=("future_media_moderation_adapter", "brand_safety", "content_safety"),
        optional=True,
        future_suffix="providers/media/moderation-safety/api-key",
        capability_group="moderation_safety_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_fallback_media_provider_adapter",
        category="media_providers",
        current_env_name="FALLBACK_MEDIA_PROVIDER_API_KEY",
        required_for=("future_fallback_media_adapter", "provider_failover"),
        optional=True,
        future_suffix="providers/media/fallback/api-key",
        capability_group="fallback_providers",
    ),
    SecretInventoryDefinition(
        logical_name="future_pluggable_media_provider_adapter",
        category="media_providers",
        current_env_name="PLUGGABLE_MEDIA_PROVIDER_API_KEY",
        required_for=("future_pluggable_provider_adapter", "provider_registry"),
        optional=True,
        future_suffix="providers/media/pluggable-adapter/api-key",
        capability_group="future_pluggable_provider_adapters",
    ),
    SecretInventoryDefinition(
        logical_name="openai_api_key",
        category="llm_api_providers",
        current_env_name="OPENAI_API_KEY",
        required_for=("agent_reasoning", "script_generation", "general_llm_execution"),
        future_suffix="providers/openai/api-key",
    ),
    SecretInventoryDefinition(
        logical_name="anthropic_api_key",
        category="llm_api_providers",
        current_env_name="ANTHROPIC_API_KEY",
        required_for=("optional_llm_provider",),
        optional=True,
        future_suffix="providers/anthropic/api-key",
    ),
    SecretInventoryDefinition(
        logical_name="stripe_secret_key",
        category="stripe_billing",
        current_env_name="STRIPE_SECRET_KEY",
        required_for=("billing", "checkout", "subscription_management"),
        future_suffix="billing/stripe/secret-key",
    ),
    SecretInventoryDefinition(
        logical_name="stripe_webhook_secret",
        category="stripe_billing",
        current_env_name="STRIPE_WEBHOOK_SECRET",
        required_for=("stripe_webhook_verification", "billing_event_integrity"),
        future_suffix="billing/stripe/webhook-secret",
    ),
    SecretInventoryDefinition(
        logical_name="rds_database_url",
        category="rds_database",
        current_env_name="DATABASE_URL",
        alternative_env_names=("AWS_RDS_SECRET_ARN",),
        required_for=("rds_postgres_persistence", "api_service", "media_worker"),
        rotation_required=True,
        rotation_interval="managed-by-rds-secret",
        future_suffix="database/rds/credentials",
    ),
    SecretInventoryDefinition(
        logical_name="media_s3_bucket_config",
        category="s3_storage",
        current_env_name="AWS_MEDIA_S3_BUCKET",
        alternative_env_names=("MEDIA_S3_BUCKET",),
        required_for=("generated_media_storage", "signed_asset_delivery"),
        rotation_required=False,
        rotation_interval="not-secret-config-reference",
        future_suffix="storage/s3/media-bucket",
        capability_group="storage_delivery_services",
    ),
    SecretInventoryDefinition(
        logical_name="uploads_s3_bucket_config",
        category="s3_storage",
        current_env_name="AWS_UPLOADS_S3_BUCKET",
        alternative_env_names=("UPLOADS_S3_BUCKET",),
        required_for=("client_upload_storage", "reference_asset_storage"),
        rotation_required=False,
        rotation_interval="not-secret-config-reference",
        future_suffix="storage/s3/uploads-bucket",
        capability_group="storage_delivery_services",
    ),
    SecretInventoryDefinition(
        logical_name="media_queue_url_config",
        category="sqs_queue",
        current_env_name="AWS_MEDIA_QUEUE_URL",
        required_for=("media_job_queueing", "ecs_worker_dispatch"),
        rotation_required=False,
        rotation_interval="not-secret-config-reference",
        future_suffix="queue/sqs/media-queue-url",
    ),
    SecretInventoryDefinition(
        logical_name="media_dlq_url_config",
        category="sqs_queue",
        current_env_name="AWS_MEDIA_DLQ_URL",
        required_for=("dead_letter_recovery", "support_diagnostics"),
        rotation_required=False,
        rotation_interval="not-secret-config-reference",
        future_suffix="queue/sqs/media-dlq-url",
    ),
    SecretInventoryDefinition(
        logical_name="jwt_session_secret",
        category="auth_session_admin_tokens",
        current_env_name="JWT_SECRET",
        alternative_env_names=("SECRET_KEY", "SESSION_SECRET", "NEXTAUTH_SECRET"),
        required_for=("api_auth", "portal_sessions"),
        future_suffix="auth/session/jwt-secret",
    ),
    SecretInventoryDefinition(
        logical_name="admin_platform_token",
        category="auth_session_admin_tokens",
        current_env_name="ADMIN_PLATFORM_TOKEN",
        alternative_env_names=("ADMIN_TOKEN",),
        required_for=("owner_admin_authority", "admin_support_recovery"),
        future_suffix="auth/admin/platform-token",
    ),
    SecretInventoryDefinition(
        logical_name="client_portal_session_secret",
        category="client_portal_session",
        current_env_name="CLIENT_PORTAL_SESSION_SECRET",
        alternative_env_names=("CLIENT_SESSION_SECRET",),
        required_for=("client_portal_sessions", "client_safe_views"),
        future_suffix="auth/client/session-secret",
    ),
    SecretInventoryDefinition(
        logical_name="webhook_signing_secret",
        category="integrations_webhooks",
        current_env_name="WEBHOOK_SIGNING_SECRET",
        required_for=("inbound_webhook_verification", "integration_event_integrity"),
        tenant_scope="per_tenant",
        future_suffix="integrations/webhooks/signing-secret",
    ),
    SecretInventoryDefinition(
        logical_name="shopify_integration_secret",
        category="integrations_webhooks",
        current_env_name="SHOPIFY_API_SECRET",
        alternative_env_names=("SHOPIFY_WEBHOOK_SECRET",),
        required_for=("shopify_integration", "ecommerce_agent"),
        tenant_scope="per_tenant",
        optional=True,
        future_suffix="integrations/shopify/secret",
    ),
    SecretInventoryDefinition(
        logical_name="observability_ingest_token",
        category="observability",
        current_env_name="SENTRY_DSN",
        alternative_env_names=("DATADOG_API_KEY", "LOGTAIL_TOKEN"),
        required_for=("production_error_monitoring", "support_diagnostics"),
        optional=True,
        future_suffix="observability/ingest-token",
    ),
)


def build_future_secret_name(definition: SecretInventoryDefinition, prefix: str = "") -> str:
    clean_prefix = sanitise_secret_path_segment(prefix or "/ecommerce-ai-agent-platform/aws-option-a", "ecommerce-ai-agent-platform/aws-option-a")
    clean_suffix = sanitise_secret_path_segment(definition.future_suffix or definition.logical_name, definition.logical_name)
    return f"/{clean_prefix}/{clean_suffix}".replace("//", "/")


def build_secret_reference(
    definition: SecretInventoryDefinition,
    env: Optional[Mapping[str, Any]] = None,
    secrets_prefix: str = "",
) -> Dict[str, Any]:
    env = env or {}
    env_names = (definition.current_env_name, *definition.alternative_env_names)
    present = value_is_present(env, env_names)
    required_now = not definition.optional
    status = "env_placeholder_present" if present else ("not_configured" if definition.optional else "missing")
    reference = CanonicalSecretReference(
        secret_id=f"secret_ref_{sanitise_secret_path_segment(definition.logical_name, 'secret')}",
        logical_name=definition.logical_name,
        category=definition.category,
        current_env_name=definition.current_env_name,
        alternative_env_names=list(definition.alternative_env_names),
        future_secrets_manager_name=build_future_secret_name(definition, secrets_prefix),
        required_for=list(definition.required_for),
        capability_group=definition.capability_group,
        tenant_scope=definition.tenant_scope,
        rotation_required=definition.rotation_required,
        rotation_interval=definition.rotation_interval,
        status=status,
        value_present=present,
        required_now=required_now,
        optional=definition.optional,
        aws_fetch_attempted=False,
        secrets_manager_call_attempted=False,
        credentials_required_now=False,
        current_env_behavior_changed=False,
    )
    return reference.to_dict()


def build_secret_inventory(env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    env = env or {}
    readiness = aws_option_a_readiness(env)
    prefix = clean_text(env.get("AWS_PROVIDER_SECRETS_PREFIX") or readiness.get("provider_secrets_prefix"))
    references = [build_secret_reference(definition, env=env, secrets_prefix=prefix) for definition in SECRET_INVENTORY_DEFINITIONS]
    missing_required = [
        ref["logical_name"]
        for ref in references
        if ref["required_now"] and not ref["value_present"]
    ]
    categories = sorted({ref["category"] for ref in references})
    media_capability_groups = sorted(
        {
            ref.get("capability_group")
            for ref in references
            if ref.get("category") == "media_providers" and ref.get("capability_group")
        }
    )
    return {
        "boundary": "aws10_secrets_manager_config_boundary",
        "last_checked_at": utc_now(),
        "secret_references": references,
        "categories": categories,
        "media_secret_capability_groups": media_capability_groups,
        "category_count": len(categories),
        "total_secret_reference_count": len(references),
        "missing_required_logical_names": missing_required,
        "all_required_values_present": not missing_required,
        "aws_fetch_attempted": False,
        "secrets_manager_call_attempted": False,
        "credentials_required_now": False,
        "current_env_behavior_changed": False,
        "provider_execution_changed": False,
        "stripe_behavior_changed": False,
        "auth_session_behavior_changed": False,
        "frontend_behavior_changed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def validate_secret_inventory_no_values(inventory_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    inventory = dict(inventory_or_payload or {})
    errors: list[str] = []
    references = inventory.get("secret_references") or []
    if not isinstance(references, list) or not references:
        errors.append("missing_secret_references")
    for ref in references:
        if not isinstance(ref, dict):
            errors.append("invalid_secret_reference")
            continue
        for key in ("secret_id", "logical_name", "category", "current_env_name", "future_secrets_manager_name", "status"):
            if not clean_text(ref.get(key)):
                errors.append(f"missing_{key}")
        if ref.get("category") not in SECRET_CATEGORIES:
            errors.append("unsupported_secret_category")
        if ref.get("category") == "media_providers" and ref.get("capability_group") not in MEDIA_SECRET_CAPABILITY_GROUPS:
            errors.append("unsupported_media_capability_group")
        if not isinstance(ref.get("value_present"), bool):
            errors.append("value_present_must_be_boolean")
        if ref.get("aws_fetch_attempted"):
            errors.append("aws_fetch_attempted")
        if ref.get("secrets_manager_call_attempted"):
            errors.append("secrets_manager_call_attempted")
        if ref.get("credentials_required_now"):
            errors.append("credentials_required_now")
        if any(str(key).lower() in SENSITIVE_VALUE_KEYS for key in ref.keys()):
            errors.append("raw_value_key_serialized")
    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "aws_fetch_attempted": False,
        "secrets_manager_call_attempted": False,
        "credentials_required_now": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_admin_safe_secret_readiness_view(env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    inventory = build_secret_inventory(env)
    return redact_sensitive_values(
        {
            "boundary": inventory["boundary"],
            "last_checked_at": inventory["last_checked_at"],
            "categories": inventory["categories"],
            "media_secret_capability_groups": inventory["media_secret_capability_groups"],
            "category_count": inventory["category_count"],
            "total_secret_reference_count": inventory["total_secret_reference_count"],
            "missing_required_logical_names": inventory["missing_required_logical_names"],
            "all_required_values_present": inventory["all_required_values_present"],
            "secret_references": inventory["secret_references"],
            "aws_fetch_attempted": False,
            "secrets_manager_call_attempted": False,
            "credentials_required_now": False,
            "current_env_behavior_changed": False,
            "credential_values_exposed": False,
            "provider_secret_values_visible": False,
            "customer_safe": True,
        }
    )


def build_client_safe_secret_readiness_view(env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    inventory = build_secret_inventory(env)
    return {
        "configuration_readiness": PUBLIC_SECRET_READINESS_LABEL,
        "required_configuration_ready": bool(inventory.get("all_required_values_present")),
        "category_count": inventory.get("category_count"),
        "media_secret_capability_group_count": len(inventory.get("media_secret_capability_groups") or []),
        "missing_required_count": len(inventory.get("missing_required_logical_names") or []),
        "aws_fetch_attempted": False,
        "secrets_manager_call_attempted": False,
        "credentials_required_now": False,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    }


def build_secrets_manager_boundary_readiness(env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    inventory = build_secret_inventory(env)
    validation = validate_secret_inventory_no_values(inventory)
    return {
        "boundary": inventory["boundary"],
        "valid": validation["valid"],
        "categories": inventory["categories"],
        "media_secret_capability_groups": inventory["media_secret_capability_groups"],
        "total_secret_reference_count": inventory["total_secret_reference_count"],
        "required_configuration_ready": inventory["all_required_values_present"],
        "aws_fetch_attempted": False,
        "secrets_manager_call_attempted": False,
        "credentials_required_now": False,
        "current_env_behavior_changed": False,
        "provider_execution_changed": False,
        "stripe_behavior_changed": False,
        "auth_session_behavior_changed": False,
        "frontend_behavior_changed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
