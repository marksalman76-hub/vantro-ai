from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional
import uuid

from backend.app.runtime.aws_option_a_runtime_contract import aws_option_a_readiness


SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "password",
    "private_key",
    "provider_api_key",
    "runway_api_key",
    "elevenlabs_api_key",
    "secret",
    "token",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(prefix: str = "media_queue") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def clean_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def clean_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def ensure_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [clean_text(item, 180) for item in value if clean_text(item)]
    if isinstance(value, tuple):
        return [clean_text(item, 180) for item in value if clean_text(item)]
    if clean_text(value):
        return [clean_text(value, 180)]
    return []


def first_value(payload: Mapping[str, Any], keys: Iterable[str], default: Any = "") -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return default


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    return value


def has_unredacted_secret_value(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            key_l = str(key).lower()
            if any(marker in key_l for marker in SECRET_KEY_MARKERS) and item != "[redacted]":
                return True
            if has_unredacted_secret_value(item):
                return True
        return False
    if isinstance(value, list):
        return any(has_unredacted_secret_value(item) for item in value)
    return False


@dataclass(frozen=True)
class CanonicalMediaQueueMessage:
    message_id: str
    job_id: str
    customer_id: str = ""
    account_id: str = ""
    tenant_id: str = ""
    requested_from: str = "runtime"
    task_type: str = "media_generation"
    workflow_type: str = "universal_complete_media"
    media_type: str = "complete_video"
    asset_type: str = "video"
    output_type: str = "complete_video"
    prompt_metadata: Dict[str, Any] = field(default_factory=dict)
    selected_agent: str = ""
    selected_agents: List[str] = field(default_factory=list)
    agent_ids: List[str] = field(default_factory=list)
    multi_agent_media_execution: bool = False
    duration_seconds: int = 0
    aspect_ratio: str = ""
    provider_preferences: Dict[str, Any] = field(default_factory=dict)
    execution_flags: Dict[str, Any] = field(default_factory=dict)
    authority: Dict[str, Any] = field(default_factory=dict)
    approval_controls: Dict[str, Any] = field(default_factory=dict)
    credit_reservation: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)
    queue_routing: Dict[str, Any] = field(default_factory=dict)
    future_sqs: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    customer_safe: bool = True
    credential_values_exposed: bool = False
    internal_config_exposed: bool = False
    paid_provider_calls_started: bool = False
    aws_sqs_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def build_prompt_metadata(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return redact_secret_values({
        "prompt": clean_text(first_value(payload, ("prompt", "task", "creative_brief"), ""), 1500),
        "media_prompt": clean_text(payload.get("media_prompt"), 1500),
        "business_name": clean_text(payload.get("business_name"), 240),
        "product_or_service": clean_text(payload.get("product_or_service"), 240),
        "platform": clean_text(payload.get("platform"), 120),
        "human_avatar_mode": clean_text(first_value(payload, ("human_avatar_mode", "human_mode"), ""), 180),
    })


def build_provider_preferences(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return redact_secret_values({
        "video_provider": clean_text(first_value(payload, ("video_provider", "visual_provider"), "runway"), 80),
        "audio_provider": clean_text(payload.get("audio_provider") or "elevenlabs", 80),
        "fallback_provider": clean_text(payload.get("fallback_provider"), 80),
        "composition_provider": clean_text(payload.get("composition_provider") or "ffmpeg", 80),
    })


def build_execution_flags(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "dry_run": clean_bool(payload.get("dry_run")),
        "preflight_only": clean_bool(payload.get("preflight_only")),
        "smoke_test_mode": clean_bool(payload.get("smoke_test_mode")),
        "credit_risk_acknowledged": clean_bool(payload.get("credit_risk_acknowledged")),
        "cost_safety_confirmed": clean_bool(payload.get("cost_safety_confirmed")),
        "paid_provider_risk_confirmed": clean_bool(payload.get("paid_provider_risk_confirmed")),
    }


def build_authority_markers(payload: Mapping[str, Any]) -> Dict[str, Any]:
    portal_mode = clean_text(first_value(payload, ("portal_mode", "source_portal", "requested_from_portal"), ""), 80)
    role = clean_text(first_value(payload, ("role", "actor_role"), ""), 80)
    is_admin = clean_bool(payload.get("is_admin")) or portal_mode.lower() in {"admin", "owner", "admin_portal"}
    return {
        "portal_mode": portal_mode or ("admin" if is_admin else "client"),
        "actor_id": clean_text(first_value(payload, ("actor_id", "admin_id", "client_id"), ""), 160),
        "role": role or ("admin" if is_admin else "client"),
        "is_owner": clean_bool(payload.get("is_owner")) or role.lower() == "owner",
        "is_admin": is_admin,
        "client_safe_output_required": not is_admin,
        "hide_provider_secrets": True,
    }


def build_media_queue_message(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    payload = dict(payload or {})
    selected_agent = clean_text(first_value(payload, ("selected_agent", "agent_id"), ""), 180)
    selected_agents = ensure_list(payload.get("selected_agents") or payload.get("agent_ids") or selected_agent)
    agent_ids = ensure_list(payload.get("agent_ids") or selected_agents)
    multi_agent = clean_bool(payload.get("multi_agent_media_execution")) or len(selected_agents or agent_ids) > 1
    requested_from = clean_text(payload.get("requested_from") or "complete_media_popup", 160)
    task_type = clean_text(payload.get("task_type") or "media_generation", 120)
    workflow_type = clean_text(payload.get("workflow_type") or "universal_complete_media", 160)

    message = CanonicalMediaQueueMessage(
        message_id=clean_text(payload.get("message_id") or safe_id("media_queue_message"), 180),
        job_id=clean_text(first_value(payload, ("job_id", "parent_job_id"), safe_id("media_job")), 180),
        customer_id=clean_text(first_value(payload, ("customer_id", "client_id"), ""), 180),
        account_id=clean_text(first_value(payload, ("account_id", "tenant_id"), ""), 180),
        tenant_id=clean_text(payload.get("tenant_id"), 180),
        requested_from=requested_from,
        task_type=task_type,
        workflow_type=workflow_type,
        media_type=clean_text(first_value(payload, ("media_type", "asset_type"), "complete_video"), 120),
        asset_type=clean_text(first_value(payload, ("asset_type", "output_asset_type"), "video"), 120),
        output_type=clean_text(first_value(payload, ("output_type", "media_type"), "complete_video"), 180),
        prompt_metadata=build_prompt_metadata(payload),
        selected_agent=selected_agent,
        selected_agents=selected_agents,
        agent_ids=agent_ids,
        multi_agent_media_execution=multi_agent,
        duration_seconds=clean_int(first_value(payload, ("duration_seconds", "duration"), 0), 0),
        aspect_ratio=clean_text(payload.get("aspect_ratio") or "16:9", 40),
        provider_preferences=build_provider_preferences(payload),
        execution_flags=build_execution_flags(payload),
        authority=build_authority_markers(payload),
        approval_controls={
            "approval_required": payload.get("approval_required"),
            "owner_approval_required": payload.get("owner_approval_required"),
            "approval_status": clean_text(payload.get("approval_status") or "not_evaluated", 120),
        },
        credit_reservation={
            "credit_check_required": payload.get("requires_credit_check"),
            "package_check_required": payload.get("requires_package_check"),
            "credit_reservation_id": clean_text(payload.get("credit_reservation_id"), 180),
            "credit_reservation_status": clean_text(payload.get("credit_reservation_status") or "not_reserved", 120),
        },
        audit={
            "correlation_id": clean_text(payload.get("correlation_id") or safe_id("corr"), 180),
            "request_id": clean_text(payload.get("request_id"), 180),
            "idempotency_key": clean_text(payload.get("idempotency_key"), 180),
            "audit_event_type": "queue_message_prepared",
        },
        queue_routing={
            "queue_name": clean_text(payload.get("queue_name") or "media_generation", 120),
            "priority": clean_int(payload.get("priority"), 100),
            "max_attempts": clean_int(payload.get("max_attempts"), 3),
            "dlq_target": "media_generation_dead_letter",
        },
        future_sqs={
            "target_backend": "aws_sqs",
            "message_group_strategy": "job_or_customer_id",
            "deduplication_strategy": "idempotency_key_or_job_id",
            "sqs_send_enabled": False,
            "requires_aws_credentials_now": False,
        },
        paid_provider_calls_started=False,
        aws_sqs_required=False,
    )
    return message.to_dict()


def validate_media_queue_message(message: Mapping[str, Any] | None) -> Dict[str, Any]:
    message = dict(message or {})
    errors: List[str] = []
    for key in ("message_id", "job_id", "task_type", "workflow_type", "media_type", "selected_agent", "created_at"):
        if not clean_text(message.get(key)):
            errors.append(f"missing_{key}")

    if clean_int(message.get("duration_seconds"), 0) < 0:
        errors.append("duration_seconds_invalid")
    if has_unredacted_secret_value(message):
        errors.append("possible_unredacted_secret_marker")

    return {
        "valid": not errors,
        "errors": errors,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


class LocalNoopMediaQueueAdapter:
    """
    Safe AWS-03 queue boundary adapter.

    It prepares canonical queue messages and reports local/no-op enqueue results
    while AWS_OPTION_A_ENABLED is false. It does not send to SQS, start workers,
    call providers, reserve credits, change Stripe/package enforcement, or alter
    portal session/auth behavior.
    """

    def __init__(self, env: Optional[Mapping[str, Any]] = None):
        self.env = dict(env or {})
        self.readiness = aws_option_a_readiness(self.env)

    def enqueue(self, payload_or_message: Mapping[str, Any] | None) -> Dict[str, Any]:
        message = (
            dict(payload_or_message or {})
            if "message_id" in dict(payload_or_message or {}) and "workflow_type" in dict(payload_or_message or {})
            else build_media_queue_message(payload_or_message)
        )
        validation = validate_media_queue_message(message)
        if not validation.get("valid"):
            return {
                "success": False,
                "accepted": False,
                "status": "queue_message_invalid",
                "errors": validation.get("errors") or [],
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        if not self.readiness.get("aws_option_a_enabled"):
            return {
                "success": True,
                "accepted": True,
                "status": "local_noop_enqueued",
                "queue_backend": "local_noop",
                "message_id": message.get("message_id"),
                "job_id": message.get("job_id"),
                "message": message,
                "sqs_send_attempted": False,
                "paid_provider_calls_started": False,
                "stripe_or_credit_reservation_attempted": False,
                "portal_auth_or_session_changed": False,
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        return {
            "success": False,
            "accepted": False,
            "status": "aws_sqs_adapter_not_enabled_yet",
            "queue_backend": "aws_sqs_future_adapter",
            "message_id": message.get("message_id"),
            "job_id": message.get("job_id"),
            "sqs_send_attempted": False,
            "paid_provider_calls_started": False,
            "customer_safe": True,
            "credential_values_exposed": False,
        }


def enqueue_media_work_locally_or_noop(
    payload_or_message: Mapping[str, Any] | None,
    env: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    return LocalNoopMediaQueueAdapter(env=env).enqueue(payload_or_message)
