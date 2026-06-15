from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional
import uuid

from backend.app.runtime.aws_option_a_runtime_contract import aws_option_a_readiness
from backend.app.runtime.durable_asset_storage_adapter_boundary import (
    build_admin_safe_asset_view,
    build_asset_reference,
    build_client_safe_asset_view,
)
from backend.app.runtime.durable_media_job_status_adapter import (
    build_admin_media_job_status_view,
    build_client_media_job_status_view,
    build_durable_media_job_status_record,
)
from backend.app.runtime.media_queue_adapter_boundary import (
    build_media_queue_message,
    enqueue_media_work_locally_or_noop,
)


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


def safe_id(prefix: str = "accepted_job") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


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


def build_acceptance_asset_placeholders(payload: Mapping[str, Any], job_id: str) -> List[Dict[str, Any]]:
    placeholders: List[Dict[str, Any]] = []
    raw_assets = payload.get("assets")
    if isinstance(raw_assets, list):
        for asset in raw_assets:
            if isinstance(asset, dict):
                placeholders.append(build_asset_reference({"job_id": job_id, **asset}))

    for key, asset_type in {
        "expected_output_asset_type": "expected_output",
        "preview_url": "preview",
        "asset_url": "provider_output",
        "final_video_url": "final_video",
        "final_output_path": "final_output",
    }.items():
        value = payload.get(key)
        if not value:
            continue
        source_type = "provider_output" if "url" in key else "generated"
        placeholders.append(build_asset_reference({
            "job_id": job_id,
            "asset_type": asset_type,
            "source_type": source_type,
            "client_safe_url": value if "url" in key else "",
            "local_path": value if "path" in key else "",
            "customer_id": first_value(payload, ("customer_id", "client_id"), ""),
            "tenant_id": payload.get("tenant_id") or "",
        }))

    if not placeholders:
        placeholders.append(build_asset_reference({
            "asset_id": safe_id("asset_placeholder"),
            "job_id": job_id,
            "asset_type": clean_text(first_value(payload, ("asset_type", "output_asset_type"), "final_output"), 120),
            "media_type": clean_text(payload.get("media_type") or "complete_video", 120),
            "source_type": "generated",
            "customer_id": first_value(payload, ("customer_id", "client_id"), ""),
            "tenant_id": payload.get("tenant_id") or "",
        }))

    return [redact_secret_values(item) for item in placeholders]


@dataclass(frozen=True)
class AcceptedApiJobEnvelope:
    job_id: str
    task_type: str = "media_generation"
    workflow_type: str = "universal_complete_media"
    customer_id: str = ""
    account_id: str = ""
    tenant_id: str = ""
    requested_from: str = "complete_media_popup"
    requested_by_role: str = "client"
    approval_controls: Dict[str, Any] = field(default_factory=dict)
    package_credit_controls: Dict[str, Any] = field(default_factory=dict)
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
    audit: Dict[str, Any] = field(default_factory=dict)
    status_lifecycle: Dict[str, Any] = field(default_factory=dict)
    durable_job_record: Dict[str, Any] = field(default_factory=dict)
    queue_message: Dict[str, Any] = field(default_factory=dict)
    queue_result: Dict[str, Any] = field(default_factory=dict)
    asset_placeholders: List[Dict[str, Any]] = field(default_factory=list)
    runtime_readiness: Dict[str, Any] = field(default_factory=dict)
    admin_diagnostics: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    customer_safe: bool = True
    credential_values_exposed: bool = False
    internal_config_exposed: bool = False
    paid_provider_calls_started: bool = False
    aws_credentials_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def build_api_job_acceptance_envelope(
    payload: Mapping[str, Any] | None,
    env: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    payload = dict(payload or {})
    readiness = aws_option_a_readiness(env or {})
    job_id = clean_text(first_value(payload, ("job_id", "parent_job_id"), safe_id("api_job")), 180)
    selected_agent = clean_text(first_value(payload, ("selected_agent", "agent_id"), ""), 180)
    selected_agents = ensure_list(payload.get("selected_agents") or payload.get("agent_ids") or selected_agent)
    agent_ids = ensure_list(payload.get("agent_ids") or selected_agents)
    multi_agent = clean_bool(payload.get("multi_agent_media_execution")) or len(selected_agents or agent_ids) > 1
    requested_by_role = clean_text(first_value(payload, ("requested_by_role", "role", "actor_role"), "client"), 80)
    requested_from = clean_text(payload.get("requested_from") or "complete_media_popup", 160)

    normalized_payload = {
        **payload,
        "job_id": job_id,
        "status": payload.get("status") or "accepted",
        "client_safe_status": payload.get("client_safe_status") or "queued",
        "selected_agent": selected_agent,
        "selected_agents": selected_agents,
        "agent_ids": agent_ids,
        "multi_agent_media_execution": multi_agent,
        "requested_from": requested_from,
        "task_type": payload.get("task_type") or "media_generation",
        "workflow_type": payload.get("workflow_type") or "universal_complete_media",
    }

    durable_record = build_durable_media_job_status_record(normalized_payload)
    queue_message = build_media_queue_message(normalized_payload)
    queue_result = enqueue_media_work_locally_or_noop(queue_message, env=env or {})
    asset_placeholders = build_acceptance_asset_placeholders(normalized_payload, job_id)

    envelope = AcceptedApiJobEnvelope(
        job_id=job_id,
        task_type=clean_text(normalized_payload["task_type"], 120),
        workflow_type=clean_text(normalized_payload["workflow_type"], 160),
        customer_id=clean_text(first_value(normalized_payload, ("customer_id", "client_id"), ""), 180),
        account_id=clean_text(first_value(normalized_payload, ("account_id", "tenant_id"), ""), 180),
        tenant_id=clean_text(normalized_payload.get("tenant_id"), 180),
        requested_from=requested_from,
        requested_by_role=requested_by_role,
        approval_controls={
            "approval_required": normalized_payload.get("approval_required"),
            "owner_approval_required": normalized_payload.get("owner_approval_required"),
            "approval_status": clean_text(normalized_payload.get("approval_status") or "not_evaluated", 120),
            "owner_control_status": clean_text(normalized_payload.get("owner_control_status") or "not_evaluated", 120),
        },
        package_credit_controls={
            "package_check_required": normalized_payload.get("requires_package_check"),
            "credit_check_required": normalized_payload.get("requires_credit_check"),
            "credit_reservation_id": clean_text(normalized_payload.get("credit_reservation_id"), 180),
            "credit_reservation_status": clean_text(normalized_payload.get("credit_reservation_status") or "not_reserved", 120),
            "billing_mutation_attempted": False,
            "stripe_mutation_attempted": False,
        },
        selected_agent=selected_agent,
        selected_agents=selected_agents,
        agent_ids=agent_ids,
        multi_agent_media_execution=multi_agent,
        media_type=clean_text(first_value(normalized_payload, ("media_type", "asset_type"), "complete_video"), 120),
        asset_type=clean_text(first_value(normalized_payload, ("asset_type", "output_asset_type"), "video"), 120),
        output_type=clean_text(first_value(normalized_payload, ("output_type", "media_type"), "complete_video"), 180),
        duration_seconds=int(queue_message.get("duration_seconds") or 0),
        aspect_ratio=clean_text(queue_message.get("aspect_ratio") or "", 40),
        provider_preferences=queue_message.get("provider_preferences") or {},
        audit={
            "correlation_id": clean_text(normalized_payload.get("correlation_id") or queue_message.get("audit", {}).get("correlation_id"), 180),
            "request_id": clean_text(normalized_payload.get("request_id"), 180),
            "idempotency_key": clean_text(normalized_payload.get("idempotency_key"), 180),
            "audit_event_type": "api_job_acceptance_prepared",
        },
        status_lifecycle={
            "accepted": True,
            "status": "accepted",
            "queue_status": queue_result.get("status"),
            "queue_mode": queue_result.get("queue_backend") or "local_noop",
            "local_compatibility": not bool(readiness.get("aws_option_a_enabled")),
        },
        durable_job_record=durable_record,
        queue_message=queue_message,
        queue_result=queue_result,
        asset_placeholders=asset_placeholders,
        runtime_readiness=readiness,
        admin_diagnostics={
            "boundary": "AWS-05_api_job_acceptance_boundary",
            "rds_write_attempted": False,
            "sqs_send_attempted": bool(queue_result.get("sqs_send_attempted")),
            "s3_upload_attempted": False,
            "paid_provider_calls_started": False,
            "billing_mutation_attempted": False,
            "portal_submission_switched": False,
        },
        paid_provider_calls_started=False,
        aws_credentials_required=False,
    )
    return envelope.to_dict()


def build_admin_api_job_acceptance_view(envelope_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    envelope = (
        dict(envelope_or_payload or {})
        if "status_lifecycle" in dict(envelope_or_payload or {})
        else build_api_job_acceptance_envelope(envelope_or_payload)
    )
    return redact_secret_values({
        "accepted": True,
        "job_id": envelope.get("job_id"),
        "status": envelope.get("status_lifecycle", {}).get("status") or "accepted",
        "task_type": envelope.get("task_type"),
        "workflow_type": envelope.get("workflow_type"),
        "customer_id": envelope.get("customer_id"),
        "account_id": envelope.get("account_id"),
        "tenant_id": envelope.get("tenant_id"),
        "requested_from": envelope.get("requested_from"),
        "requested_by_role": envelope.get("requested_by_role"),
        "approval_controls": envelope.get("approval_controls") or {},
        "package_credit_controls": envelope.get("package_credit_controls") or {},
        "selected_agent": envelope.get("selected_agent"),
        "selected_agents": envelope.get("selected_agents") or [],
        "agent_ids": envelope.get("agent_ids") or [],
        "multi_agent_media_execution": bool(envelope.get("multi_agent_media_execution")),
        "media_type": envelope.get("media_type"),
        "asset_type": envelope.get("asset_type"),
        "output_type": envelope.get("output_type"),
        "duration_seconds": envelope.get("duration_seconds"),
        "aspect_ratio": envelope.get("aspect_ratio"),
        "provider_preferences": envelope.get("provider_preferences") or {},
        "audit": envelope.get("audit") or {},
        "status_lifecycle": envelope.get("status_lifecycle") or {},
        "durable_job_record": envelope.get("durable_job_record") or {},
        "queue_message": envelope.get("queue_message") or {},
        "queue_result": envelope.get("queue_result") or {},
        "asset_placeholders": [
            build_admin_safe_asset_view(asset) for asset in envelope.get("asset_placeholders") or []
        ],
        "runtime_readiness": envelope.get("runtime_readiness") or {},
        "admin_diagnostics": envelope.get("admin_diagnostics") or {},
        "created_at": envelope.get("created_at"),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    })


def build_client_api_job_acceptance_view(envelope_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    envelope = (
        dict(envelope_or_payload or {})
        if "status_lifecycle" in dict(envelope_or_payload or {})
        else build_api_job_acceptance_envelope(envelope_or_payload)
    )
    return {
        "accepted": True,
        "job_id": envelope.get("job_id"),
        "status": "queued",
        "message": "Your media job has been accepted and is queued for processing.",
        "task_type": envelope.get("task_type"),
        "workflow_type": envelope.get("workflow_type"),
        "requested_from": envelope.get("requested_from"),
        "selected_agent": envelope.get("selected_agent"),
        "selected_agents": envelope.get("selected_agents") or [],
        "agent_ids": envelope.get("agent_ids") or [],
        "multi_agent_media_execution": bool(envelope.get("multi_agent_media_execution")),
        "media_type": envelope.get("media_type"),
        "asset_type": envelope.get("asset_type"),
        "output_type": envelope.get("output_type"),
        "duration_seconds": envelope.get("duration_seconds"),
        "aspect_ratio": envelope.get("aspect_ratio"),
        "asset_placeholders": [
            build_client_safe_asset_view(asset) for asset in envelope.get("asset_placeholders") or []
        ],
        "created_at": envelope.get("created_at"),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
    }


class LocalCompatibilityApiJobAcceptanceBoundary:
    """
    Safe AWS-05 API acceptance facade.

    It composes AWS-01 through AWS-04 boundary records and returns an accepted
    envelope. It does not switch live routes, write RDS, send SQS, upload S3,
    mutate Stripe/credits/packages, or call paid providers.
    """

    def __init__(self, env: Optional[Mapping[str, Any]] = None):
        self.env = dict(env or {})

    def accept(self, payload: Mapping[str, Any] | None) -> Dict[str, Any]:
        envelope = build_api_job_acceptance_envelope(payload, env=self.env)
        return {
            "success": True,
            "accepted": True,
            "status": envelope.get("status_lifecycle", {}).get("status") or "accepted",
            "job_id": envelope.get("job_id"),
            "envelope": envelope,
            "admin_view": build_admin_api_job_acceptance_view(envelope),
            "client_view": build_client_api_job_acceptance_view(envelope),
            "rds_write_attempted": False,
            "sqs_send_attempted": bool(envelope.get("admin_diagnostics", {}).get("sqs_send_attempted")),
            "s3_upload_attempted": False,
            "paid_provider_calls_started": False,
            "billing_mutation_attempted": False,
            "stripe_mutation_attempted": False,
            "customer_safe": True,
            "credential_values_exposed": False,
        }


def accept_api_job_locally_or_noop(
    payload: Mapping[str, Any] | None,
    env: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    return LocalCompatibilityApiJobAcceptanceBoundary(env=env).accept(payload)
