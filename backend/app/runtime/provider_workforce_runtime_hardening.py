from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from backend.app.runtime.real_provider_activation_registry import get_all_provider_activation_statuses
from backend.app.runtime.provider_dispatch_policy_worker_foundation import provider_dispatch_policy_status, provider_worker_foundation_status
from backend.app.runtime.real_provider_http_execution_layer import controlled_openai_live_execution_status, real_provider_http_runtime_status


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_provider_score(status: Dict[str, Any]) -> int:
    score = 0
    if status.get("known_adapter"):
        score += 20
    if status.get("configured"):
        score += 25
    if status.get("ready"):
        score += 25
    if status.get("http_request_builder_ready"):
        score += 15
    if status.get("owner_governed_execution_required"):
        score += 10
    if status.get("credential_values_exposed") is False:
        score += 5
    return min(score, 100)


def provider_runtime_health_summary() -> Dict[str, Any]:
    providers = ["openai", "runway", "kling", "heygen", "elevenlabs", "replicate"]
    registry = get_all_provider_activation_statuses()
    dispatch_policy = provider_dispatch_policy_status()
    worker = provider_worker_foundation_status()

    provider_statuses: Dict[str, Dict[str, Any]] = {}
    for provider in providers:
        status = real_provider_http_runtime_status(provider)
        score = _safe_provider_score(status)
        provider_statuses[provider] = {
            **status,
            "health_score": score,
            "health_state": "ready" if score >= 80 else "configured_not_dispatching" if score >= 60 else "not_configured",
            "safe_to_show_admin": True,
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    ready = [p for p, s in provider_statuses.items() if s["health_state"] == "ready"]
    configured = [p for p, s in provider_statuses.items() if s.get("configured")]
    unconfigured = [p for p, s in provider_statuses.items() if not s.get("configured")]

    return {
        "success": True,
        "profile": "provider_runtime_health_summary_v1",
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "provider_count": len(providers),
        "configured_provider_count": len(configured),
        "unconfigured_provider_count": len(unconfigured),
        "ready_provider_count": len(ready),
        "ready_providers": ready,
        "configured_providers": configured,
        "unconfigured_providers": unconfigured,
        "provider_statuses": provider_statuses,
        "registry": registry,
        "dispatch_policy": dispatch_policy,
        "worker_foundation": worker,
        "controlled_openai": controlled_openai_live_execution_status(),
        "checked_at_ms": _now_ms(),
    }


def provider_recovery_readiness_summary() -> Dict[str, Any]:
    worker = provider_worker_foundation_status()
    dispatch = provider_dispatch_policy_status()

    return {
        "success": True,
        "profile": "provider_recovery_readiness_v1",
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "retry_escalation_linked": bool(worker.get("retry_escalation_linked")),
        "timeline_events_linked": bool(worker.get("timeline_events_linked")),
        "safe_queue_preparation_enabled": bool(worker.get("safe_queue_preparation_enabled")),
        "dispatch_policy_layer_enabled": bool(worker.get("dispatch_policy_layer_enabled")),
        "real_background_dispatch_enabled": bool(worker.get("real_background_dispatch_enabled")),
        "requires_final_policy_enablement": bool(dispatch.get("requires_final_policy_enablement")),
        "owner_governed_execution_required": True,
        "recovery_modes": [
            "retry_after_timeout",
            "manual_review_after_retry_exhaustion",
            "provider_degraded_mode",
            "owner_review_required",
            "safe_customer_status_packet",
        ],
        "next_safe_step": "Connect durable queue replay after admin UI exposes provider health and recovery state.",
        "checked_at_ms": _now_ms(),
    }


def provider_workforce_runtime_hardening_status() -> Dict[str, Any]:
    health = provider_runtime_health_summary()
    recovery = provider_recovery_readiness_summary()

    return {
        "success": True,
        "profile": "provider_workforce_runtime_hardening_v1",
        "visibility_only": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "health_summary": health,
        "recovery_readiness": recovery,
        "hardening_layers": {
            "provider_health_scoring": True,
            "provider_registry_visibility": True,
            "dispatch_policy_visibility": True,
            "worker_foundation_visibility": True,
            "retry_recovery_readiness": True,
            "admin_safe_status_packets": True,
            "credential_safe_visibility": True,
            "external_execution_not_triggered_by_status_routes": True,
        },
        "checked_at_ms": _now_ms(),
    }
