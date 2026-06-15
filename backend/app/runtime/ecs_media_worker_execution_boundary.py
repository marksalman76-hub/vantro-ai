from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

from backend.app.runtime.aws_option_a_runtime_contract import aws_option_a_readiness
from backend.app.runtime.api_job_acceptance_boundary import build_api_job_acceptance_envelope
from backend.app.runtime.ffmpeg_worker_readiness_boundary import build_ffmpeg_worker_readiness_contract
from backend.app.runtime.media_queue_adapter_boundary import build_media_queue_message, validate_media_queue_message


WORKER_LIFECYCLE_STATES = [
    "received",
    "claimed",
    "validating",
    "planning",
    "provider_preflight_ready",
    "provider_execution_disabled",
    "composing_disabled",
    "asset_persistence_disabled",
    "completed_local_noop",
    "failed_safe",
]

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
    "stripe_secret_key",
    "secret",
    "token",
)

SAFE_BOOLEAN_MARKER_KEYS = {
    "credential_values_exposed",
    "provider_secret_values_visible",
    "requires_aws_credentials_now",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def clean_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


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
            if key_l in SAFE_BOOLEAN_MARKER_KEYS:
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    return value


def is_accepted_envelope(value: Mapping[str, Any]) -> bool:
    return "status_lifecycle" in value and "queue_message" in value


def is_queue_message(value: Mapping[str, Any]) -> bool:
    return "message_id" in value and "workflow_type" in value and "queue_routing" in value


def normalise_worker_input(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    payload = dict(payload or {})
    if is_accepted_envelope(payload):
        envelope = payload
        queue_message = dict(envelope.get("queue_message") or {})
    elif is_queue_message(payload):
        queue_message = dict(payload)
        envelope = build_api_job_acceptance_envelope(queue_message)
    else:
        envelope = build_api_job_acceptance_envelope(payload)
        queue_message = dict(envelope.get("queue_message") or build_media_queue_message(payload))

    return {
        "accepted_envelope": redact_secret_values(envelope),
        "queue_message": redact_secret_values(queue_message),
    }


def validate_worker_task(worker_input: Mapping[str, Any]) -> Dict[str, Any]:
    envelope = dict(worker_input.get("accepted_envelope") or {})
    queue_message = dict(worker_input.get("queue_message") or {})
    errors: List[str] = []

    for key in ("job_id", "task_type", "workflow_type", "selected_agent"):
        if not clean_text(queue_message.get(key) or envelope.get(key)):
            errors.append(f"missing_{key}")

    queue_validation = validate_media_queue_message(queue_message)
    if not queue_validation.get("valid"):
        errors.extend([f"queue_{error}" for error in queue_validation.get("errors") or []])

    return {
        "valid": not errors,
        "errors": errors,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_worker_authority(queue_message: Mapping[str, Any], envelope: Mapping[str, Any]) -> Dict[str, Any]:
    authority = dict(queue_message.get("authority") or {})
    authority_role = clean_text(authority.get("role"), 80).lower()
    envelope_role = clean_text(envelope.get("requested_by_role"), 80).lower()
    requested_by_role = authority_role if authority_role in {"admin", "owner"} else envelope_role
    if requested_by_role in {"admin", "owner"}:
        authority["portal_mode"] = "admin"
        authority["role"] = requested_by_role
        authority["is_admin"] = True
        authority["is_owner"] = requested_by_role == "owner" or clean_bool(authority.get("is_owner"))
        authority["client_safe_output_required"] = False
    authority.setdefault("hide_provider_secrets", True)
    return redact_secret_values(authority)


def build_lifecycle_events(valid: bool) -> List[Dict[str, Any]]:
    states = WORKER_LIFECYCLE_STATES[:-1] if valid else ["received", "validating", "failed_safe"]
    return [
        {
            "state": state,
            "at": utc_now(),
            "external_side_effects_started": False,
        }
        for state in states
    ]


@dataclass(frozen=True)
class EcsMediaWorkerTaskEnvelope:
    job_id: str
    message_id: str = ""
    task_type: str = "media_generation"
    workflow_type: str = "universal_complete_media"
    customer_id: str = ""
    account_id: str = ""
    tenant_id: str = ""
    selected_agent: str = ""
    selected_agents: List[str] = field(default_factory=list)
    agent_ids: List[str] = field(default_factory=list)
    multi_agent_media_execution: bool = False
    media_type: str = "complete_video"
    asset_type: str = "video"
    output_type: str = "complete_video"
    duration_seconds: int = 0
    aspect_ratio: str = ""
    provider_preferences: Dict[str, Any] = field(default_factory=dict)
    authority: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)
    lifecycle_events: List[Dict[str, Any]] = field(default_factory=list)
    future_worker_hooks: Dict[str, Any] = field(default_factory=dict)
    retry_dlq: Dict[str, Any] = field(default_factory=dict)
    ffmpeg_readiness: Dict[str, Any] = field(default_factory=dict)
    runtime_readiness: Dict[str, Any] = field(default_factory=dict)
    accepted_envelope: Dict[str, Any] = field(default_factory=dict)
    queue_message: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    customer_safe: bool = True
    credential_values_exposed: bool = False
    internal_config_exposed: bool = False
    provider_execution_started: bool = False
    ffmpeg_invoked: bool = False
    asset_persistence_started: bool = False
    billing_credit_finalization_started: bool = False
    aws_credentials_required: bool = False
    final_27_agent_catalogue_not_modified: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def build_worker_task_envelope(
    payload: Mapping[str, Any] | None,
    env: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    worker_input = normalise_worker_input(payload)
    envelope = dict(worker_input.get("accepted_envelope") or {})
    queue_message = dict(worker_input.get("queue_message") or {})
    validation = validate_worker_task(worker_input)
    readiness = aws_option_a_readiness(env or {})
    ffmpeg_readiness = build_ffmpeg_worker_readiness_contract(env=env or {})

    task = EcsMediaWorkerTaskEnvelope(
        job_id=clean_text(first_value(queue_message, ("job_id",), envelope.get("job_id") or "pending_worker_job"), 180),
        message_id=clean_text(queue_message.get("message_id"), 180),
        task_type=clean_text(first_value(queue_message, ("task_type",), envelope.get("task_type") or "media_generation"), 120),
        workflow_type=clean_text(first_value(queue_message, ("workflow_type",), envelope.get("workflow_type") or "universal_complete_media"), 160),
        customer_id=clean_text(first_value(queue_message, ("customer_id",), envelope.get("customer_id") or ""), 180),
        account_id=clean_text(first_value(queue_message, ("account_id",), envelope.get("account_id") or ""), 180),
        tenant_id=clean_text(first_value(queue_message, ("tenant_id",), envelope.get("tenant_id") or ""), 180),
        selected_agent=clean_text(first_value(queue_message, ("selected_agent",), envelope.get("selected_agent") or ""), 180),
        selected_agents=ensure_list(queue_message.get("selected_agents") or envelope.get("selected_agents")),
        agent_ids=ensure_list(queue_message.get("agent_ids") or envelope.get("agent_ids")),
        multi_agent_media_execution=clean_bool(queue_message.get("multi_agent_media_execution") or envelope.get("multi_agent_media_execution")),
        media_type=clean_text(first_value(queue_message, ("media_type",), envelope.get("media_type") or "complete_video"), 120),
        asset_type=clean_text(first_value(queue_message, ("asset_type",), envelope.get("asset_type") or "video"), 120),
        output_type=clean_text(first_value(queue_message, ("output_type",), envelope.get("output_type") or "complete_video"), 180),
        duration_seconds=int(queue_message.get("duration_seconds") or envelope.get("duration_seconds") or 0),
        aspect_ratio=clean_text(queue_message.get("aspect_ratio") or envelope.get("aspect_ratio") or "", 40),
        provider_preferences=redact_secret_values(queue_message.get("provider_preferences") or envelope.get("provider_preferences") or {}),
        authority=build_worker_authority(queue_message, envelope),
        audit=redact_secret_values({
            **dict(envelope.get("audit") or {}),
            **dict(queue_message.get("audit") or {}),
            "audit_event_type": "ecs_media_worker_boundary_prepared",
        }),
        lifecycle_events=build_lifecycle_events(bool(validation.get("valid"))),
        future_worker_hooks={
            "provider_execution": "disabled_until_AWS_worker_cutover",
            "duration_aware_segmentation": "planned_not_executed",
            "ffmpeg_composition": "disabled_until_worker_image_row",
            "asset_persistence": "disabled_until_storage_cutover",
            "status_updates": "planned_not_persisted",
            "audit_evidence": "planned_not_persisted",
            "billing_credit_finalization": "disabled_until_credit_cutover",
        },
        retry_dlq={
            "retry_enabled_now": False,
            "dlq_enabled_now": False,
            "future_dlq_target": queue_message.get("queue_routing", {}).get("dlq_target") or "media_generation_dead_letter",
        },
        ffmpeg_readiness=ffmpeg_readiness,
        runtime_readiness=readiness,
        accepted_envelope=envelope,
        queue_message=queue_message,
        provider_execution_started=False,
        ffmpeg_invoked=False,
        asset_persistence_started=False,
        billing_credit_finalization_started=False,
        aws_credentials_required=False,
        final_27_agent_catalogue_not_modified=True,
    )
    return task.to_dict()


def process_worker_task_locally_or_noop(
    payload: Mapping[str, Any] | None,
    env: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    task = build_worker_task_envelope(payload, env=env)
    validation = validate_worker_task({
        "accepted_envelope": task.get("accepted_envelope") or {},
        "queue_message": task.get("queue_message") or {},
    })
    if not validation.get("valid"):
        return {
            "success": False,
            "status": "failed_safe",
            "worker_result": "failed_safe",
            "errors": validation.get("errors") or [],
            "task": task,
            "provider_execution_started": False,
            "ffmpeg_invoked": False,
            "asset_persistence_started": False,
            "billing_credit_finalization_started": False,
            "aws_calls_started": False,
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return {
        "success": True,
        "status": "completed_local_noop",
        "worker_result": "completed_local_noop",
        "job_id": task.get("job_id"),
        "message_id": task.get("message_id"),
        "task": task,
        "provider_execution_started": False,
        "provider_preflight_ready": True,
        "ffmpeg_invoked": False,
        "composition_started": False,
        "asset_persistence_started": False,
        "billing_credit_finalization_started": False,
        "aws_calls_started": False,
        "worker_loop_started": False,
        "final_27_agent_catalogue_not_modified": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_admin_worker_result_view(result_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    result = (
        dict(result_or_payload or {})
        if "worker_result" in dict(result_or_payload or {})
        else process_worker_task_locally_or_noop(result_or_payload)
    )
    task = dict(result.get("task") or {})
    return redact_secret_values({
        "success": result.get("success"),
        "status": result.get("status"),
        "worker_result": result.get("worker_result"),
        "job_id": result.get("job_id") or task.get("job_id"),
        "message_id": result.get("message_id") or task.get("message_id"),
        "task_type": task.get("task_type"),
        "workflow_type": task.get("workflow_type"),
        "selected_agent": task.get("selected_agent"),
        "selected_agents": task.get("selected_agents") or [],
        "agent_ids": task.get("agent_ids") or [],
        "multi_agent_media_execution": bool(task.get("multi_agent_media_execution")),
        "media_type": task.get("media_type"),
        "asset_type": task.get("asset_type"),
        "output_type": task.get("output_type"),
        "duration_seconds": task.get("duration_seconds"),
        "aspect_ratio": task.get("aspect_ratio"),
        "provider_preferences": task.get("provider_preferences") or {},
        "authority": task.get("authority") or {},
        "audit": task.get("audit") or {},
        "lifecycle_events": task.get("lifecycle_events") or [],
        "future_worker_hooks": task.get("future_worker_hooks") or {},
        "retry_dlq": task.get("retry_dlq") or {},
        "ffmpeg_readiness": task.get("ffmpeg_readiness") or {},
        "provider_execution_started": result.get("provider_execution_started"),
        "ffmpeg_invoked": result.get("ffmpeg_invoked"),
        "asset_persistence_started": result.get("asset_persistence_started"),
        "billing_credit_finalization_started": result.get("billing_credit_finalization_started"),
        "aws_calls_started": result.get("aws_calls_started"),
        "final_27_agent_catalogue_not_modified": result.get("final_27_agent_catalogue_not_modified"),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    })


def build_client_worker_result_view(result_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    result = (
        dict(result_or_payload or {})
        if "worker_result" in dict(result_or_payload or {})
        else process_worker_task_locally_or_noop(result_or_payload)
    )
    task = dict(result.get("task") or {})
    return {
        "success": bool(result.get("success")),
        "status": "processing_not_yet_enabled",
        "message": "Your media job is prepared for worker processing. Production worker execution is not enabled yet.",
        "job_id": result.get("job_id") or task.get("job_id"),
        "media_type": task.get("media_type"),
        "asset_type": task.get("asset_type"),
        "output_type": task.get("output_type"),
        "duration_seconds": task.get("duration_seconds"),
        "aspect_ratio": task.get("aspect_ratio"),
        "selected_agent": task.get("selected_agent"),
        "selected_agents": task.get("selected_agents") or [],
        "agent_ids": task.get("agent_ids") or [],
        "multi_agent_media_execution": bool(task.get("multi_agent_media_execution")),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
    }


class LocalNoopEcsMediaWorkerExecutionBoundary:
    """
    Safe AWS-06 ECS/Fargate media worker execution boundary.

    This boundary validates accepted jobs/queue messages and emits lifecycle
    evidence. It does not run loops, poll SQS, call AWS, call providers, invoke
    ffmpeg, persist assets, finalize credits, or mutate Stripe/package state.
    """

    def __init__(self, env: Optional[Mapping[str, Any]] = None):
        self.env = dict(env or {})

    def process(self, payload: Mapping[str, Any] | None) -> Dict[str, Any]:
        result = process_worker_task_locally_or_noop(payload, env=self.env)
        result["admin_view"] = build_admin_worker_result_view(result)
        result["client_view"] = build_client_worker_result_view(result)
        return redact_secret_values(result)
