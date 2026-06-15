from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping


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
    "secret",
    "token",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any, limit: int = 500) -> str:
    text = str(value or "").strip()
    return text[:limit]


def clean_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def ensure_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [clean_text(item, 160) for item in value if clean_text(item)]
    if isinstance(value, tuple):
        return [clean_text(item, 160) for item in value if clean_text(item)]
    if clean_text(value):
        return [clean_text(value, 160)]
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


def provider_attempt_count(payload: Mapping[str, Any]) -> int:
    explicit = first_value(
        payload,
        (
            "provider_attempt_count",
            "provider_attempts_count",
            "paid_provider_attempt_count",
            "paid_visual_provider_attempts_possible",
        ),
        None,
    )
    if explicit is not None:
        try:
            return max(0, int(explicit))
        except Exception:
            pass

    child_jobs = payload.get("child_jobs") if isinstance(payload.get("child_jobs"), dict) else {}
    count = 0
    for key in ("visual_attempts", "visual_segments", "audio_attempts", "composition_attempts"):
        items = child_jobs.get(key)
        if isinstance(items, list):
            count += len(items)
    for key in ("provider_attempts", "generated_segments"):
        items = payload.get(key)
        if isinstance(items, list):
            count += len(items)
    return count


def build_provider_summary(payload: Mapping[str, Any]) -> Dict[str, Any]:
    risk = payload.get("estimated_credit_risk") if isinstance(payload.get("estimated_credit_risk"), dict) else {}
    summary = {
        "video_provider": clean_text(first_value(payload, ("video_provider", "visual_provider"), "")),
        "audio_provider": clean_text(payload.get("audio_provider")),
        "fallback_provider": clean_text(payload.get("fallback_provider")),
        "composition_provider": clean_text(first_value(payload, ("composition_provider", "composition_path"), "")),
        "provider_job_id": clean_text(first_value(payload, ("provider_job_id", "runway_job_id", "external_job_id"), "")),
        "risk_level": clean_text(risk.get("risk_level") or payload.get("risk_level")),
        "paid_visual_provider_attempts_possible": risk.get("paid_visual_provider_attempts_possible"),
        "paid_audio_provider_attempts_possible": risk.get("paid_audio_provider_attempts_possible"),
    }
    return redact_secret_values({key: value for key, value in summary.items() if value not in ("", None)})


def build_asset_references(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    assets: List[Dict[str, Any]] = []
    raw_assets = payload.get("assets")
    if isinstance(raw_assets, list):
        for asset in raw_assets:
            if isinstance(asset, dict):
                assets.append(redact_secret_values(dict(asset)))

    for key in (
        "final_asset",
        "final_output",
        "final_video",
        "generated_media",
        "output_asset",
    ):
        value = payload.get(key)
        if isinstance(value, dict):
            assets.append(redact_secret_values({"source_field": key, **value}))

    for key in ("asset_url", "output_url", "final_url", "final_video_url", "preview_url", "download_url"):
        value = clean_text(payload.get(key), 1000)
        if value:
            assets.append({"source_field": key, "url": value, "customer_safe": True})

    return assets


def build_error_summary(payload: Mapping[str, Any]) -> Dict[str, Any]:
    safe_error = clean_text(
        first_value(
            payload,
            ("safe_error_summary", "client_safe_error", "error_summary", "message", "error"),
            "",
        ),
        500,
    )
    provider_error = clean_text(first_value(payload, ("provider_error", "provider_execution_error"), ""), 500)
    if not safe_error and provider_error:
        safe_error = "Provider execution failed. Admin diagnostics are available."

    return {
        "safe_error_summary": safe_error,
        "has_provider_error": bool(provider_error),
        "customer_safe": True,
    }


def client_status_from_internal(status: str) -> str:
    status_l = clean_text(status).lower()
    if not status_l:
        return "preparing"
    if "complete" in status_l or "ready" in status_l:
        return "completed"
    if "fail" in status_l or "error" in status_l:
        return "needs_attention"
    if "blocked" in status_l or "approval" in status_l or "confirm" in status_l:
        return "awaiting_confirmation"
    if "queued" in status_l:
        return "queued"
    if "running" in status_l or "processing" in status_l or "generating" in status_l:
        return "running"
    return status_l


@dataclass(frozen=True)
class DurableMediaJobStatusRecord:
    job_id: str
    customer_id: str = ""
    account_id: str = ""
    tenant_id: str = ""
    owner_admin_visible: bool = True
    client_visible: bool = True
    client_safe_status: str = "preparing"
    internal_status: str = "received"
    media_type: str = "complete_video"
    asset_type: str = "video"
    selected_agent: str = ""
    selected_agents: List[str] = field(default_factory=list)
    agent_ids: List[str] = field(default_factory=list)
    multi_agent_media_execution: bool = False
    provider_summary: Dict[str, Any] = field(default_factory=dict)
    provider_attempt_count: int = 0
    asset_references: List[Dict[str, Any]] = field(default_factory=list)
    output_references: List[Dict[str, Any]] = field(default_factory=list)
    error_summary: Dict[str, Any] = field(default_factory=dict)
    diagnostics_visibility_rules: Dict[str, Any] = field(default_factory=dict)
    credit_billing: Dict[str, Any] = field(default_factory=dict)
    provider_diagnostics: Dict[str, Any] = field(default_factory=dict)
    internal_diagnostics: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    customer_safe: bool = True
    credential_values_exposed: bool = False
    internal_config_exposed: bool = False
    aws_rds_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_durable_media_job_status_record(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    payload = dict(payload or {})
    internal_status = clean_text(first_value(payload, ("internal_status", "status"), "received"), 160)
    selected_agent = clean_text(first_value(payload, ("selected_agent", "agent_id"), ""), 160)
    selected_agents = ensure_list(payload.get("selected_agents") or payload.get("agent_ids"))
    agent_ids = ensure_list(payload.get("agent_ids") or selected_agents)
    multi_agent = clean_bool(payload.get("multi_agent_media_execution")) or len(selected_agents or agent_ids) > 1

    diagnostics = {
        "provider_diagnostics": payload.get("provider_diagnostics") if isinstance(payload.get("provider_diagnostics"), dict) else {},
        "failed_preflight_checks": payload.get("failed_preflight_checks") if isinstance(payload.get("failed_preflight_checks"), list) else [],
        "blocked_provider_calls": payload.get("blocked_provider_calls") if isinstance(payload.get("blocked_provider_calls"), list) else [],
        "child_jobs": payload.get("child_jobs") if isinstance(payload.get("child_jobs"), dict) else {},
    }

    record = DurableMediaJobStatusRecord(
        job_id=clean_text(first_value(payload, ("job_id", "parent_job_id", "id"), "pending_media_job"), 160),
        customer_id=clean_text(first_value(payload, ("customer_id", "client_id"), ""), 160),
        account_id=clean_text(first_value(payload, ("account_id", "tenant_id"), ""), 160),
        tenant_id=clean_text(payload.get("tenant_id"), 160),
        owner_admin_visible=True,
        client_visible=not clean_bool(payload.get("admin_only")),
        client_safe_status=clean_text(payload.get("client_safe_status") or client_status_from_internal(internal_status), 160),
        internal_status=internal_status,
        media_type=clean_text(first_value(payload, ("media_type", "output_type"), "complete_video"), 160),
        asset_type=clean_text(first_value(payload, ("asset_type", "output_asset_type"), "video"), 160),
        selected_agent=selected_agent,
        selected_agents=selected_agents,
        agent_ids=agent_ids,
        multi_agent_media_execution=multi_agent,
        provider_summary=build_provider_summary(payload),
        provider_attempt_count=provider_attempt_count(payload),
        asset_references=build_asset_references(payload),
        output_references=build_asset_references(payload),
        error_summary=build_error_summary(payload),
        diagnostics_visibility_rules={
            "admin_view_includes_provider_diagnostics": True,
            "client_view_hides_provider_diagnostics": True,
            "client_view_hides_internal_status": True,
            "secret_values_always_redacted": True,
        },
        credit_billing={
            "credit_check_required": payload.get("requires_credit_check"),
            "package_check_required": payload.get("requires_package_check"),
            "estimated_credit_risk": redact_secret_values(payload.get("estimated_credit_risk") or {}),
            "billing_status": clean_text(payload.get("billing_status"), 160),
        },
        provider_diagnostics=redact_secret_values(diagnostics),
        internal_diagnostics=redact_secret_values({
            "raw_status_available": True,
            "source_status": internal_status,
            "portal_mode": payload.get("portal_mode"),
        }),
        created_at=clean_text(payload.get("created_at") or utc_now(), 80),
        updated_at=clean_text(payload.get("updated_at") or utc_now(), 80),
    )
    return redact_secret_values(record.to_dict())


def build_admin_media_job_status_view(record_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    record = (
        dict(record_or_payload or {})
        if "diagnostics_visibility_rules" in dict(record_or_payload or {})
        else build_durable_media_job_status_record(record_or_payload)
    )
    return redact_secret_values({
        "job_id": record.get("job_id"),
        "status": record.get("internal_status"),
        "client_safe_status": record.get("client_safe_status"),
        "internal_status": record.get("internal_status"),
        "media_type": record.get("media_type"),
        "asset_type": record.get("asset_type"),
        "selected_agent": record.get("selected_agent"),
        "selected_agents": record.get("selected_agents") or [],
        "agent_ids": record.get("agent_ids") or [],
        "multi_agent_media_execution": bool(record.get("multi_agent_media_execution")),
        "provider_summary": record.get("provider_summary") or {},
        "provider_attempt_count": int(record.get("provider_attempt_count") or 0),
        "asset_references": record.get("asset_references") or [],
        "output_references": record.get("output_references") or [],
        "error_summary": record.get("error_summary") or {},
        "provider_diagnostics": record.get("provider_diagnostics") or {},
        "internal_diagnostics": record.get("internal_diagnostics") or {},
        "diagnostics_visibility_rules": record.get("diagnostics_visibility_rules") or {},
        "credit_billing": record.get("credit_billing") or {},
        "created_at": record.get("created_at"),
        "updated_at": record.get("updated_at"),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    })


def build_client_media_job_status_view(record_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    record = (
        dict(record_or_payload or {})
        if "diagnostics_visibility_rules" in dict(record_or_payload or {})
        else build_durable_media_job_status_record(record_or_payload)
    )
    return {
        "job_id": record.get("job_id"),
        "status": record.get("client_safe_status"),
        "media_type": record.get("media_type"),
        "asset_type": record.get("asset_type"),
        "selected_agent": record.get("selected_agent"),
        "selected_agents": record.get("selected_agents") or [],
        "agent_ids": record.get("agent_ids") or [],
        "multi_agent_media_execution": bool(record.get("multi_agent_media_execution")),
        "asset_references": record.get("asset_references") or [],
        "output_references": record.get("output_references") or [],
        "error_summary": record.get("error_summary") or {},
        "created_at": record.get("created_at"),
        "updated_at": record.get("updated_at"),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
    }


def map_media_job_status_for_portal(payload: Mapping[str, Any] | None, portal_mode: str = "client") -> Dict[str, Any]:
    record = build_durable_media_job_status_record(payload)
    if clean_text(portal_mode).lower() in {"admin", "owner", "admin_portal", "owner_portal"}:
        return build_admin_media_job_status_view(record)
    return build_client_media_job_status_view(record)
