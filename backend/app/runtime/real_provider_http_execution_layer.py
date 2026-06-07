from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, Optional

from backend.app.runtime.asset_storage_signed_delivery_runtime import (
    create_asset_record,
    create_customer_safe_asset_preview,
    update_asset_status,
)
from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    persist_dispatch_attempt_bridge,
    persist_latency_metric_bridge,
    persist_provider_execution_record_bridge,
    persist_worker_event_bridge,
)
from backend.app.runtime.durable_provider_execution_ledger import record_provider_result
from backend.app.runtime.live_provider_adapters import (
    check_provider_gate,
    create_signed_asset_delivery_packet,
    normalise_provider_failure,
    provider_timeout_policy,
)

try:
    from backend.app.runtime.creative_asset_persistence_bridge import persist_creative_asset
except Exception:
    persist_creative_asset = None


def _now_ms() -> int:
    return int(time.time() * 1000)


def build_openai_request_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = payload.get("prompt") or payload.get("instructions") or ""
    model = payload.get("model") or payload.get("provider_model") or "gpt-4.1-mini"

    return {
        "provider_key": "openai",
        "provider_endpoint": "responses",
        "model": model,
        "input_present": bool(prompt),
        "request_body": {
            "model": model,
            "input": prompt,
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_replicate_request_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "provider_key": "replicate",
        "provider_endpoint": "predictions",
        "model": payload.get("model") or payload.get("provider_model") or "provider_default",
        "input_present": bool(payload.get("prompt") or payload.get("input")),
        "request_body": {
            "version": payload.get("version"),
            "input": payload.get("input") or {"prompt": payload.get("prompt", "")},
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_media_provider_request_packet(provider_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "provider_key": provider_key,
        "provider_endpoint": "generation",
        "model": payload.get("model") or payload.get("provider_model") or "provider_default",
        "input_present": bool(payload.get("prompt") or payload.get("script") or payload.get("asset_url")),
        "request_body": {
            "prompt": payload.get("prompt"),
            "script": payload.get("script"),
            "asset_url": payload.get("asset_url"),
            "voice": payload.get("voice"),
            "language": payload.get("language"),
            "duration_seconds": payload.get("duration_seconds"),
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_provider_http_request_packet(provider_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    provider_key = (provider_key or "").strip().lower()
    if provider_key == "openai":
        return build_openai_request_packet(payload)
    if provider_key == "replicate":
        return build_replicate_request_packet(payload)
    if provider_key in {"runway", "kling", "heygen", "elevenlabs"}:
        return build_media_provider_request_packet(provider_key, payload)

    return {
        "provider_key": provider_key,
        "status": "blocked",
        "reason": "unknown_provider_http_adapter",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def normalise_provider_success_response(
    *,
    provider_key: str,
    tenant_id: str,
    request_id: str,
    raw_response: Dict[str, Any],
    asset_type: str = "generated_asset",
) -> Dict[str, Any]:
    provider_job_id = (
        raw_response.get("id")
        or raw_response.get("job_id")
        or raw_response.get("prediction_id")
        or f"provider_job_{uuid.uuid4().hex[:12]}"
    )

    asset_id = f"asset_{uuid.uuid4().hex[:16]}"
    asset_packet = create_signed_asset_delivery_packet(
        tenant_id=tenant_id,
        asset_id=asset_id,
        provider_key=provider_key,
        asset_type=asset_type,
    )

    return {
        "provider_key": provider_key,
        "status": "completed",
        "provider_job_id": provider_job_id,
        "asset_id": asset_id,
        "asset_packet": asset_packet,
        "raw_response_stored": False,
        "safe_output": {
            "text": raw_response.get("output_text") or raw_response.get("text"),
            "asset_url_present": bool(raw_response.get("asset_url") or raw_response.get("output_url")),
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def execute_real_provider_http_request(
    provider_key: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = dict(payload or {})
    provider_key = (provider_key or "").strip().lower()
    started_at = _now_ms()

    live_execution_requested = bool(payload.get("live_execution_requested"))
    owner_governed_execution_confirmed = bool(payload.get("owner_governed_execution_confirmed"))

    gate = check_provider_gate(
        provider_key,
        live_execution_requested=live_execution_requested,
        owner_governed_execution_confirmed=owner_governed_execution_confirmed,
    )

    request_packet = build_provider_http_request_packet(provider_key, payload)
    tenant_id = payload.get("tenant_id") or "unknown-tenant"
    request_id = payload.get("request_id") or f"provider_request_{started_at}"
    dispatch_status = "ready_for_real_http_dispatch" if gate["execution_allowed"] else "blocked"

    if not gate["execution_allowed"]:
        latency_ms = _now_ms() - started_at
        execution_bridge = persist_provider_execution_record_bridge(
            tenant_id=tenant_id,
            request_id=request_id,
            provider_key=provider_key,
            task_type=str(payload.get("task_type") or payload.get("action_type") or "provider_http_dispatch"),
            execution_status="blocked",
        )
        execution_id = execution_bridge.get("record", {}).get("execution_id", request_id)
        persist_dispatch_attempt_bridge(
            tenant_id=tenant_id,
            request_id=request_id,
            execution_id=execution_id,
            worker_job_id=str(payload.get("worker_job_id") or execution_id),
            provider_key=provider_key,
            attempt_number=int(payload.get("attempt_number") or 1),
            allowed_by_policy=False,
            result_status="blocked",
            reason=gate["reason"],
        )
        persist_latency_metric_bridge(
            tenant_id=tenant_id,
            request_id=request_id,
            execution_id=execution_id,
            provider_key=provider_key,
            latency_ms=latency_ms,
            operation="provider_http_dispatch_blocked",
        )
        return {
            "provider_key": provider_key,
            "status": "blocked",
            "reason": gate["reason"],
            "gate": gate,
            "request_packet": request_packet,
            "live_external_call_executed": False,
            "latency_ms": latency_ms,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    latency_ms = _now_ms() - started_at
    execution_bridge = persist_provider_execution_record_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key=provider_key,
        task_type=str(payload.get("task_type") or payload.get("action_type") or "provider_http_dispatch"),
        execution_status=dispatch_status,
    )
    execution_id = execution_bridge.get("record", {}).get("execution_id", request_id)
    persist_dispatch_attempt_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        worker_job_id=str(payload.get("worker_job_id") or execution_id),
        provider_key=provider_key,
        attempt_number=int(payload.get("attempt_number") or 1),
        allowed_by_policy=True,
        result_status=dispatch_status,
        reason="dispatch_ready",
    )
    persist_latency_metric_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        provider_key=provider_key,
        latency_ms=latency_ms,
        operation="provider_http_dispatch_ready",
    )
    return {
        "provider_key": provider_key,
        "status": "ready_for_real_http_dispatch",
        "gate": gate,
        "request_packet": request_packet,
        "timeout_policy": provider_timeout_policy(provider_key),
        "live_external_call_executed": False,
        "dispatch_blocked_until_provider_credentials_and_final_policy_enablement": True,
        "latency_ms": latency_ms,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def map_provider_http_exception(
    provider_key: str,
    *,
    exception_type: str,
    status_code: Optional[int] = None,
) -> Dict[str, Any]:
    retryable = exception_type in {
        "timeout",
        "rate_limit",
        "server_error",
        "connection_error",
    }

    code_map = {
        "timeout": "provider_timeout",
        "rate_limit": "provider_rate_limited",
        "server_error": "provider_server_error",
        "connection_error": "provider_connection_error",
        "auth_error": "provider_auth_error",
        "bad_request": "provider_bad_request",
    }

    return normalise_provider_failure(
        provider_key,
        error_code=code_map.get(exception_type, "provider_unknown_error"),
        message="Provider HTTP execution failed safely.",
        retryable=retryable,
        status_code=status_code,
    )


def real_provider_http_runtime_status(provider_key: str) -> Dict[str, Any]:
    gate = check_provider_gate(
        provider_key,
        live_execution_requested=False,
        owner_governed_execution_confirmed=False,
    )

    return {
        "provider_key": provider_key,
        "known_adapter": gate["known_adapter"],
        "configured": gate["configured"],
        "ready": gate["ready"],
        "missing": gate["missing"],
        "http_request_builder_ready": gate["known_adapter"],
        "real_http_dispatch_enabled": False,
        "requires_final_policy_enablement": True,
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def controlled_openai_live_execution_status() -> Dict[str, Any]:
    return {
        "provider_key": "openai",
        "controlled_live_execution_ready": True,
        "openai_api_key_present": bool(os.getenv("OPENAI_API_KEY")),
        "real_dispatch_globally_enabled": os.getenv("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", "").lower() == "true",
        "requires_live_execution_requested": True,
        "requires_owner_governed_execution_confirmed": True,
        "actual_network_call_enabled": os.getenv("OPENAI_ACTUAL_NETWORK_CALL_ENABLED", "").lower() == "true",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def execute_controlled_openai_live_request(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = dict(payload or {})
    started_at = _now_ms()

    base = execute_real_provider_http_request("openai", payload)

    if base.get("status") != "ready_for_real_http_dispatch":
        return {
            "provider_key": "openai",
            "status": "blocked",
            "reason": base.get("reason") or base.get("status"),
            "base_result": base,
            "live_external_call_executed": False,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if os.getenv("REAL_PROVIDER_HTTP_DISPATCH_ENABLED", "").lower() != "true":
        return {
            "provider_key": "openai",
            "status": "blocked",
            "reason": "real_provider_http_dispatch_globally_disabled",
            "base_result": base,
            "live_external_call_executed": False,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    if os.getenv("OPENAI_ACTUAL_NETWORK_CALL_ENABLED", "").lower() != "true":
        return {
            "provider_key": "openai",
            "status": "ready_but_network_call_disabled",
            "reason": "OPENAI_ACTUAL_NETWORK_CALL_ENABLED_not_true",
            "base_result": base,
            "request_packet": base.get("request_packet"),
            "live_external_call_executed": False,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        request_packet = base.get("request_packet", {})
        body = request_packet.get("request_body") or {}

        response = client.responses.create(**body)
        response_id = getattr(response, "id", None) or f"openai_response_{uuid.uuid4().hex[:12]}"
        output_text = getattr(response, "output_text", None)

        normalised = normalise_provider_success_response(
            provider_key="openai",
            tenant_id=payload.get("tenant_id") or "unknown-tenant",
            request_id=payload.get("request_id") or "unknown-request",
            raw_response={
                "id": response_id,
                "output_text": output_text,
            },
            asset_type=payload.get("asset_type") or "text",
        )

        latency_ms = _now_ms() - started_at
        audit_asset = persist_openai_execution_audit_asset(
            tenant_id=payload.get("tenant_id") or "unknown-tenant",
            request_id=payload.get("request_id") or "unknown-request",
            provider_job_id=response_id,
            output_text=output_text,
            asset_type=payload.get("asset_type") or "text",
            latency_ms=latency_ms,
            agent_id=payload.get("agent_id") or payload.get("requested_agent") or payload.get("selected_agent"),
            title=payload.get("title") or payload.get("test_label") or payload.get("task") or "Creative provider output",
            campaign_context=payload.get("campaign_context") or payload.get("task"),
            target_audience=payload.get("target_audience"),
        )
        record_provider_result(
            provider_job_id=response_id,
            execution_id=audit_asset.get("execution_id") or response_id,
            provider="openai",
            result_status="completed",
            result_summary=(output_text or "")[:1000],
            asset_id=(audit_asset.get("asset") or {}).get("asset_id", ""),
            metadata={"source": "controlled_openai_live_execution"},
        )

        return {
            "provider_key": "openai",
            "status": "completed",
            "provider_job_id": response_id,
            "normalised_response": normalised,
            "audit_asset": audit_asset,
            "live_external_call_executed": True,
            "latency_ms": latency_ms,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    except Exception as exc:
        failure = map_provider_http_exception(
            "openai",
            exception_type="provider_unknown_error",
            status_code=None,
        )
        failure["safe_error"] = str(exc)[:300]
        record_provider_result(
            provider_job_id=f"openai_failed_{uuid.uuid4().hex[:12]}",
            execution_id=payload.get("request_id") or f"openai_failed_{uuid.uuid4().hex[:12]}",
            provider="openai",
            result_status="failed",
            result_summary="Controlled OpenAI execution failed safely.",
            metadata={"failure": failure},
        )
        return {
            "provider_key": "openai",
            "status": "failed",
            "failure": failure,
            "live_external_call_executed": False,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }


def persist_openai_execution_audit_asset(
    *,
    tenant_id: str,
    request_id: str,
    provider_job_id: str,
    output_text: Optional[str] = None,
    asset_type: str = "text",
    latency_ms: int = 0,
    agent_id: Optional[str] = None,
    title: Optional[str] = None,
    campaign_context: Optional[str] = None,
    target_audience: Optional[str] = None,
) -> Dict[str, Any]:
    execution_bridge = persist_provider_execution_record_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key="openai",
        task_type="controlled_openai_live_execution",
        execution_status="completed",
        worker_job_id=None,
        provider_job_id=provider_job_id,
    )
    execution_id = execution_bridge.get("record", {}).get("execution_id", f"openai_execution_{uuid.uuid4().hex[:12]}")

    asset = create_asset_record(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key="openai",
        asset_type=asset_type,
        asset_status="ready",
        source_url=None,
        metadata={
            "provider_job_id": provider_job_id,
            "output_text_present": bool(output_text),
            "source": "controlled_openai_live_execution",
            "execution_id": execution_id,
        },
    )

    update_asset_status(
        asset_id=asset["asset_id"],
        asset_status="ready",
        metadata={
            "execution_id": execution_id,
            "provider_job_id": provider_job_id,
        },
    )

    preview = create_customer_safe_asset_preview(
        tenant_id=tenant_id,
        asset_id=asset["asset_id"],
    )

    creative_registry_bridge = {
        "success": False,
        "persisted": False,
        "reason": "creative_asset_persistence_bridge_unavailable",
        "credential_values_exposed": False,
        "customer_safe": True,
    }

    if persist_creative_asset is not None:
        try:
            creative_registry_bridge = persist_creative_asset(
                {
                    "asset_id": asset.get("asset_id"),
                    "agent_id": agent_id or "marketing_specialist_agent",
                    "agent_label": agent_id or "marketing_specialist_agent",
                    "provider": "openai",
                    "asset_type": asset_type or "text",
                    "title": title or "OpenAI creative provider output",
                    "test_label": request_id,
                    "provider_asset_id": provider_job_id,
                    "provider_asset_url": None,
                    "preview_url": (preview.get("preview_packet") or {}).get("delivery_url"),
                    "download_url": (preview.get("preview_packet") or {}).get("delivery_url"),
                    "content": output_text,
                    "summary": (output_text or "")[:500],
                    "status": "ready",
                    "quality_score": None,
                    "campaign_context": campaign_context,
                    "target_audience": target_audience,
                    "usage_rights": {
                        "status": "owner_review_required",
                        "note": "Generated text creative asset. Confirm final usage rights before external publication.",
                    },
                    "owner_approval_required": True,
                    "customer_safe": True,
                    "credential_values_exposed": False,
                }
            )
        except Exception as exc:
            creative_registry_bridge = {
                "success": False,
                "persisted": False,
                "reason": "creative_asset_registry_persist_failed",
                "safe_error": str(exc)[:300],
                "credential_values_exposed": False,
                "customer_safe": True,
            }

    event_bridge = persist_worker_event_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        worker_job_id=provider_job_id,
        provider_key="openai",
        event_type="controlled_openai_execution_completed",
        status="completed",
        details={
            "asset_id": asset["asset_id"],
            "asset_type": asset_type,
            "output_text_present": bool(output_text),
            "creative_registry_bridge": creative_registry_bridge,
        },
    )

    latency_bridge = persist_latency_metric_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        provider_key="openai",
        latency_ms=int(latency_ms or 0),
        operation="controlled_openai_live_execution",
    )

    return {
        "status": "persisted",
        "execution_bridge": execution_bridge,
        "execution_id": execution_id,
        "asset": asset,
        "preview": preview,
        "creative_registry_bridge": creative_registry_bridge,
        "event_bridge": event_bridge,
        "latency_bridge": latency_bridge,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def controlled_openai_audit_asset_integration_status() -> Dict[str, Any]:
    return {
        "provider_key": "openai",
        "audit_asset_integration_ready": True,
        "execution_record_persistence_ready": True,
        "asset_record_creation_ready": True,
        "creative_registry_bridge_ready": persist_creative_asset is not None,
        "customer_safe_preview_ready": True,
        "ledger_event_ready": True,
        "latency_metric_ready": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
