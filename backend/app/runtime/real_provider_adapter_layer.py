"""
Real Provider Adapter Layer

Unified provider adapter scaffold for real external execution.

This layer:
- Normalises provider request shape.
- Selects provider adapters safely.
- Checks provider activation readiness.
- Does not expose credentials.
- Does not perform live external calls until provider credentials and live execution gates are enabled.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from backend.app.runtime.real_provider_activation_registry import (
    get_provider_activation_status,
    select_ready_provider_for_capability,
)


SUPPORTED_ADAPTERS = {
    "openai": {
        "adapter": "openai_live_execution_adapter_v1",
        "capabilities": ["text", "vision", "image_generation", "agent_reasoning"],
        "default_timeout_seconds": 90,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "replicate": {
        "adapter": "replicate_live_execution_adapter_v1",
        "capabilities": ["image_generation", "video_generation", "model_inference"],
        "default_timeout_seconds": 180,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "runway": {
        "adapter": "runway_live_execution_adapter_v1",
        "capabilities": ["video_generation", "image_to_video", "text_to_video"],
        "default_timeout_seconds": 300,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "kling": {
        "adapter": "kling_live_execution_adapter_v1",
        "capabilities": ["video_generation", "image_to_video", "text_to_video"],
        "default_timeout_seconds": 300,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "heygen": {
        "adapter": "heygen_live_execution_adapter_v1",
        "capabilities": ["avatar_video", "ugc_video", "voice_avatar"],
        "default_timeout_seconds": 300,
        "supports_polling": True,
        "supports_asset_output": True,
    },
    "elevenlabs": {
        "adapter": "elevenlabs_live_execution_adapter_v1",
        "capabilities": ["voice_generation", "dubbing", "speech"],
        "default_timeout_seconds": 180,
        "supports_polling": True,
        "supports_asset_output": True,
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalise_provider_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    provider_key = str(payload.get("provider_key") or "").strip().lower()
    capability = str(payload.get("capability") or "").strip()
    tenant_id = str(payload.get("tenant_id") or "unknown-tenant").strip()
    actor_role = str(payload.get("actor_role") or "owner").strip()

    request_id = str(payload.get("request_id") or f"provider_req_{uuid4().hex}")

    return {
        "request_id": request_id,
        "tenant_id": tenant_id,
        "actor_role": actor_role,
        "provider_key": provider_key,
        "capability": capability,
        "input": dict(payload.get("input", {})),
        "metadata": dict(payload.get("metadata", {})),
        "owner_approval_required": bool(payload.get("owner_approval_required", True)),
        "live_execution_requested": bool(payload.get("live_execution_requested", False)),
        "credential_values_exposed": False,
        "customer_safe": True,
        "normalised_at": _now_iso(),
    }


def get_provider_adapter_status(provider_key: str) -> Dict[str, Any]:
    provider_key = str(provider_key or "").strip().lower()
    activation = get_provider_activation_status(provider_key)
    adapter = SUPPORTED_ADAPTERS.get(provider_key)

    return {
        "provider_key": provider_key,
        "known_adapter": adapter is not None,
        "adapter": adapter.get("adapter") if adapter else None,
        "activation": activation,
        "configured": bool(activation.get("configured")),
        "ready": bool(activation.get("ready")) and adapter is not None,
        "credential_values_exposed": False,
        "owner_governed_execution_required": True,
        "checked_at": _now_iso(),
    }


def route_provider_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = normalise_provider_request(payload)

    if not request["capability"]:
        return {
            "routed": False,
            "error": "missing_capability",
            "request": request,
            "credential_values_exposed": False,
            "customer_safe": True,
            "checked_at": _now_iso(),
        }

    provider_key = request["provider_key"]

    if not provider_key:
        selected = select_ready_provider_for_capability(request["capability"])
        if not selected.get("selected"):
            return {
                "routed": False,
                "error": "no_ready_provider_for_capability",
                "selection": selected,
                "request": request,
                "credential_values_exposed": False,
                "customer_safe": True,
                "checked_at": _now_iso(),
            }
        provider_key = selected["provider_key"]
        request["provider_key"] = provider_key

    adapter_status = get_provider_adapter_status(provider_key)

    if not adapter_status["known_adapter"]:
        return {
            "routed": False,
            "error": "unknown_provider_adapter",
            "provider_key": provider_key,
            "request": request,
            "credential_values_exposed": False,
            "customer_safe": True,
            "checked_at": _now_iso(),
        }

    adapter = SUPPORTED_ADAPTERS[provider_key]

    if request["capability"] not in adapter["capabilities"]:
        return {
            "routed": False,
            "error": "capability_not_supported_by_provider",
            "provider_key": provider_key,
            "capability": request["capability"],
            "supported_capabilities": adapter["capabilities"],
            "request": request,
            "credential_values_exposed": False,
            "customer_safe": True,
            "checked_at": _now_iso(),
        }

    if not adapter_status["ready"]:
        return {
            "routed": False,
            "error": "provider_not_configured",
            "provider_key": provider_key,
            "adapter_status": adapter_status,
            "request": request,
            "credential_values_exposed": False,
            "customer_safe": True,
            "checked_at": _now_iso(),
        }

    return {
        "routed": True,
        "execution_mode": "ready_for_live_adapter",
        "provider_key": provider_key,
        "adapter": adapter["adapter"],
        "capability": request["capability"],
        "timeout_seconds": adapter["default_timeout_seconds"],
        "supports_polling": adapter["supports_polling"],
        "supports_asset_output": adapter["supports_asset_output"],
        "request": request,
        "credential_values_exposed": False,
        "customer_safe": True,
        "owner_governed_execution_required": True,
        "checked_at": _now_iso(),
    }


def execute_provider_request_scaffold(payload: Dict[str, Any]) -> Dict[str, Any]:
    route = route_provider_request(payload)

    if not route.get("routed"):
        return {
            "submitted": False,
            "route": route,
            "provider_job_id": None,
            "status": "not_submitted",
            "credential_values_exposed": False,
            "customer_safe": True,
            "checked_at": _now_iso(),
        }

    if not route["request"].get("live_execution_requested"):
        return {
            "submitted": False,
            "status": "live_execution_not_requested",
            "route": route,
            "provider_job_id": None,
            "message": "Adapter route is ready, but live execution was not requested.",
            "credential_values_exposed": False,
            "customer_safe": True,
            "checked_at": _now_iso(),
        }

    return {
        "submitted": False,
        "status": "live_execution_blocked_until_adapter_implementation",
        "route": route,
        "provider_job_id": None,
        "message": "Provider adapter scaffold is installed. Live network calls will be enabled provider-by-provider after credential configuration and execution gate verification.",
        "credential_values_exposed": False,
        "customer_safe": True,
        "owner_governed_execution_required": True,
        "checked_at": _now_iso(),
    }
