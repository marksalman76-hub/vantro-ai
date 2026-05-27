from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, Optional

from backend.app.runtime.live_provider_adapters import (
    check_provider_gate,
    create_signed_asset_delivery_packet,
    normalise_provider_failure,
    provider_timeout_policy,
)


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

    if not gate["execution_allowed"]:
        return {
            "provider_key": provider_key,
            "status": "blocked",
            "reason": gate["reason"],
            "gate": gate,
            "request_packet": request_packet,
            "live_external_call_executed": False,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    # Live execution is intentionally isolated here.
    # This foundation confirms readiness but does not make external calls yet.
    # Real HTTP dispatch should be enabled only after production credentials,
    # owner policy gates, durable storage, and monitoring are configured.
    return {
        "provider_key": provider_key,
        "status": "ready_for_real_http_dispatch",
        "gate": gate,
        "request_packet": request_packet,
        "timeout_policy": provider_timeout_policy(provider_key),
        "live_external_call_executed": False,
        "dispatch_blocked_until_provider_credentials_and_final_policy_enablement": True,
        "latency_ms": _now_ms() - started_at,
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
