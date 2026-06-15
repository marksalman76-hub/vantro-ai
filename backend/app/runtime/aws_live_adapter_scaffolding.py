from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping, Optional
import uuid

from backend.app.runtime.aws_option_a_runtime_contract import aws_option_a_readiness
from backend.app.runtime.secrets_manager_config_boundary import MEDIA_SECRET_CAPABILITY_GROUPS
from backend.app.runtime.real_agent_component_catalogue import (
    CLIENT_FACING_AGENTS,
    FINAL_APPROVED_VISIBLE_AGENT_COUNT,
    FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
    SYSTEM_AGENTS,
)


TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}
AWS_LIVE_ADAPTER_SERVICE_FLAGS = {
    "rds": "AWS_RDS_LIVE_ADAPTER_ENABLED",
    "sqs_dlq": "AWS_SQS_LIVE_ADAPTER_ENABLED",
    "s3": "AWS_S3_LIVE_ADAPTER_ENABLED",
    "secrets_manager": "AWS_SECRETS_MANAGER_LIVE_ADAPTER_ENABLED",
}
AWS_LIVE_ADAPTER_REQUIRED_ENV = {
    "rds": ("DATABASE_URL", "AWS_RDS_SECRET_ARN"),
    "sqs_dlq": ("AWS_MEDIA_QUEUE_URL", "AWS_MEDIA_DLQ_URL"),
    "s3": ("AWS_MEDIA_S3_BUCKET", "AWS_UPLOADS_S3_BUCKET"),
    "secrets_manager": ("AWS_PROVIDER_SECRETS_PREFIX",),
}

SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "database_url",
    "password",
    "private_key",
    "provider_api_key",
    "stripe_secret_key",
    "secret",
    "token",
    "queue_url",
    "bucket",
)

SAFE_BOOLEAN_MARKER_KEYS = {
    "credential_values_exposed",
    "provider_secret_values_visible",
    "credentials_required_now",
    "live_call_attempted",
    "db_connection_attempted",
    "migration_attempted",
    "sqs_send_attempted",
    "s3_upload_attempted",
    "secret_fetch_attempted",
    "aws_call_attempted",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(prefix: str = "aws_live_adapter") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def enabled(value: Any) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def env_present(env: Mapping[str, Any], key: str) -> bool:
    return clean_text(env.get(key)) != ""


def any_env_present(env: Mapping[str, Any], keys: Iterable[str]) -> bool:
    return any(env_present(env, key) for key in keys)


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if key_l in SAFE_BOOLEAN_MARKER_KEYS or isinstance(item, bool):
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    return value


@dataclass(frozen=True)
class AwsLiveAdapterReadiness:
    adapter_name: str
    service: str
    service_enable_flag: str
    aws_option_a_enabled: bool = False
    service_enable_flag_present: bool = False
    live_behavior_authorized_by_flags: bool = False
    live_behavior_implemented: bool = False
    status: str = "disabled_by_default"
    required_env_presence: Dict[str, bool] = field(default_factory=dict)
    required_config_present: bool = False
    missing_required_env: list[str] = field(default_factory=list)
    readiness_checked_at: str = field(default_factory=utc_now)
    credentials_required_now: bool = False
    live_call_attempted: bool = False
    db_connection_attempted: bool = False
    migration_attempted: bool = False
    sqs_send_attempted: bool = False
    s3_upload_attempted: bool = False
    secret_fetch_attempted: bool = False
    aws_call_attempted: bool = False
    credential_values_exposed: bool = False
    provider_secret_values_visible: bool = False
    customer_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def build_service_readiness(service: str, env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    env = dict(env or {})
    runtime = aws_option_a_readiness(env)
    flag = AWS_LIVE_ADAPTER_SERVICE_FLAGS[service]
    required_keys = AWS_LIVE_ADAPTER_REQUIRED_ENV[service]
    aws_enabled = bool(runtime.get("aws_option_a_enabled"))
    flag_enabled = enabled(env.get(flag))
    if service == "rds":
        required_present = any_env_present(env, required_keys)
        required_presence = {key: env_present(env, key) for key in required_keys}
    else:
        required_present = all(env_present(env, key) for key in required_keys)
        required_presence = {key: env_present(env, key) for key in required_keys}
    authorized = aws_enabled and flag_enabled
    if not authorized:
        status = "disabled_by_default"
    elif not required_present:
        status = "not_configured"
    else:
        status = "live_adapter_scaffold_ready_not_executing"
    readiness = AwsLiveAdapterReadiness(
        adapter_name=f"{service}_live_adapter_scaffold",
        service=service,
        service_enable_flag=flag,
        aws_option_a_enabled=aws_enabled,
        service_enable_flag_present=flag_enabled,
        live_behavior_authorized_by_flags=authorized,
        live_behavior_implemented=False,
        status=status,
        required_env_presence=required_presence,
        required_config_present=required_present,
        missing_required_env=[key for key, present in required_presence.items() if not present],
        credentials_required_now=False,
        live_call_attempted=False,
        db_connection_attempted=False,
        migration_attempted=False,
        sqs_send_attempted=False,
        s3_upload_attempted=False,
        secret_fetch_attempted=False,
        aws_call_attempted=False,
    )
    return readiness.to_dict()


class RdsLiveAdapterScaffold:
    service = "rds"

    def __init__(self, env: Optional[Mapping[str, Any]] = None):
        self.env = dict(env or {})

    def readiness(self) -> Dict[str, Any]:
        return build_service_readiness(self.service, self.env)

    def plan_migration_dry_run(self, operation: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return build_disabled_live_adapter_operation(
            "rds_migration_dry_run_scaffold",
            self.service,
            self.env,
            operation,
            {"migration_attempted": False, "db_connection_attempted": False, "rds_write_attempted": False},
        )

    def plan_repository_write(self, operation: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return build_disabled_live_adapter_operation(
            "rds_repository_write_scaffold",
            self.service,
            self.env,
            operation,
            {"db_connection_attempted": False, "rds_write_attempted": False},
        )


class SqsDlqLiveAdapterScaffold:
    service = "sqs_dlq"

    def __init__(self, env: Optional[Mapping[str, Any]] = None):
        self.env = dict(env or {})

    def readiness(self) -> Dict[str, Any]:
        return build_service_readiness(self.service, self.env)

    def plan_send_message(self, message: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return build_disabled_live_adapter_operation(
            "sqs_send_message_scaffold",
            self.service,
            self.env,
            message,
            {"sqs_send_attempted": False, "dlq_send_attempted": False},
        )


class S3LiveAdapterScaffold:
    service = "s3"

    def __init__(self, env: Optional[Mapping[str, Any]] = None):
        self.env = dict(env or {})

    def readiness(self) -> Dict[str, Any]:
        return build_service_readiness(self.service, self.env)

    def plan_upload_asset(self, asset_reference: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return build_disabled_live_adapter_operation(
            "s3_upload_asset_scaffold",
            self.service,
            self.env,
            asset_reference,
            {"s3_upload_attempted": False, "signed_url_generated": False},
        )


class SecretsManagerLiveAdapterScaffold:
    service = "secrets_manager"

    def __init__(self, env: Optional[Mapping[str, Any]] = None):
        self.env = dict(env or {})

    def readiness(self) -> Dict[str, Any]:
        return build_service_readiness(self.service, self.env)

    def plan_secret_fetch(self, secret_reference: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        return build_disabled_live_adapter_operation(
            "secrets_manager_fetch_scaffold",
            self.service,
            self.env,
            secret_reference,
            {"secret_fetch_attempted": False, "secret_value_loaded": False},
        )


def build_disabled_live_adapter_operation(
    operation_type: str,
    service: str,
    env: Optional[Mapping[str, Any]] = None,
    payload: Optional[Mapping[str, Any]] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    readiness = build_service_readiness(service, env)
    payload = dict(payload or {})
    extra = dict(extra or {})
    return redact_secret_values({
        "operation_id": safe_id(operation_type),
        "operation_type": operation_type,
        "service": service,
        "status": readiness.get("status"),
        "adapter_readiness": readiness,
        "payload_reference": {
            "job_id": clean_text(payload.get("job_id") or payload.get("parent_job_id"), 180),
            "asset_id": clean_text(payload.get("asset_id"), 180),
            "message_id": clean_text(payload.get("message_id"), 180),
            "logical_name": clean_text(payload.get("logical_name"), 180),
        },
        "live_call_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "aws_call_attempted": False,
        "credentials_required_now": False,
        "live_behavior_implemented": False,
        "created_at": utc_now(),
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
        **extra,
    })


def build_all_aws_live_adapter_readiness(env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    env = dict(env or {})
    adapters = {
        "rds": RdsLiveAdapterScaffold(env).readiness(),
        "sqs_dlq": SqsDlqLiveAdapterScaffold(env).readiness(),
        "s3": S3LiveAdapterScaffold(env).readiness(),
        "secrets_manager": SecretsManagerLiveAdapterScaffold(env).readiness(),
    }
    return {
        "boundary": "aws14_live_adapter_scaffolding",
        "adapters": adapters,
        "service_enable_flags": dict(AWS_LIVE_ADAPTER_SERVICE_FLAGS),
        "all_disabled_by_default": all(item["status"] == "disabled_by_default" for item in adapters.values()),
        "credentials_required_now": False,
        "network_call_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "aws_call_attempted": False,
        "live_routes_switched": False,
        "frontend_behavior_changed": False,
        "broad_media_capability_groups": sorted(MEDIA_SECRET_CAPABILITY_GROUPS),
        "final_visible_agent_catalogue": {
            "source": FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
            "expected_count": FINAL_APPROVED_VISIBLE_AGENT_COUNT,
            "actual_count": len(CLIENT_FACING_AGENTS),
            "system_agents_visible_or_selectable": False,
            "system_agent_count_internal_only": len(SYSTEM_AGENTS),
        },
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    }


def build_admin_safe_live_adapter_view(env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    readiness = build_all_aws_live_adapter_readiness(env)
    return redact_secret_values({
        **readiness,
        "admin_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    })


def build_client_safe_live_adapter_view(env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    readiness = build_all_aws_live_adapter_readiness(env)
    return {
        "status": "aws_live_adapter_scaffolding_prepared",
        "adapters_ready_for_future_cutover_count": sum(
            1 for item in readiness["adapters"].values()
            if item.get("status") == "live_adapter_scaffold_ready_not_executing"
        ),
        "all_disabled_by_default": bool(readiness.get("all_disabled_by_default")),
        "live_routes_switched": False,
        "frontend_behavior_changed": False,
        "credentials_required_now": False,
        "network_call_attempted": False,
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
    }
