"""
Gate-safe live provider adapter layer for the unique multi-agent, multi-industry platform.

This module prepares live-capable external provider execution while preserving:
- credential-safe readiness checks
- owner-governed live execution gates
- blocked execution when credentials are absent
- normalised provider failures
- timeout/polling abstractions
- latency and health scoring foundations
- signed asset delivery packet scaffolding without exposing secrets
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


SUPPORTED_PROVIDER_KEYS = {
    "openai",
    "replicate",
    "runway",
    "kling",
    "heygen",
    "elevenlabs",
}


PROVIDER_CREDENTIAL_ENV = {
    "openai": ["OPENAI_API_KEY"],
    "replicate": ["REPLICATE_API_TOKEN"],
    "runway": ["RUNWAY_API_KEY"],
    "kling": ["KLING_API_KEY"],
    "heygen": ["HEYGEN_API_KEY"],
    "elevenlabs": ["ELEVENLABS_API_KEY"],
}


@dataclass(frozen=True)
class ProviderRouteDecision:
    provider_key: str
    known_adapter: bool
    configured: bool
    ready: bool
    missing: List[str]
    credential_values_exposed: bool
    live_execution_requested: bool
    owner_governed_execution_required: bool
    execution_allowed: bool
    reason: str


def _now_ms() -> int:
    return int(time.time() * 1000)


def _missing_credentials(provider_key: str) -> List[str]:
    required = PROVIDER_CREDENTIAL_ENV.get(provider_key, [])
    return [name for name in required if not os.getenv(name)]


def check_provider_gate(
    provider_key: str,
    *,
    live_execution_requested: bool = False,
    owner_governed_execution_confirmed: bool = False,
) -> Dict[str, Any]:
    provider_key = (provider_key or "").strip().lower()
    known = provider_key in SUPPORTED_PROVIDER_KEYS
    missing = [] if not known else _missing_credentials(provider_key)
    configured = known and not missing
    ready = bool(known and configured)
    execution_allowed = bool(
        ready and live_execution_requested and owner_governed_execution_confirmed
    )

    if not known:
        reason = "unknown_provider_adapter"
    elif missing:
        reason = "provider_credentials_missing"
    elif not live_execution_requested:
        reason = "live_execution_not_requested"
    elif not owner_governed_execution_confirmed:
        reason = "owner_governed_execution_not_confirmed"
    else:
        reason = "execution_allowed"

    decision = ProviderRouteDecision(
        provider_key=provider_key,
        known_adapter=known,
        configured=configured,
        ready=ready,
        missing=missing,
        credential_values_exposed=False,
        live_execution_requested=live_execution_requested,
        owner_governed_execution_required=True,
        execution_allowed=execution_allowed,
        reason=reason,
    )
    return decision.__dict__


def normalise_provider_failure(
    provider_key: str,
    *,
    error_code: str,
    message: str,
    retryable: bool = True,
    status_code: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "provider_key": provider_key,
        "status": "failed",
        "failure_code": error_code,
        "safe_message": message,
        "retryable": retryable,
        "status_code": status_code,
        "credential_values_exposed": False,
        "owner_review_required": not retryable,
    }


def provider_timeout_policy(provider_key: str) -> Dict[str, Any]:
    provider_key = (provider_key or "").strip().lower()
    defaults = {
        "connect_timeout_seconds": 15,
        "read_timeout_seconds": 90,
        "job_timeout_seconds": 900,
        "poll_interval_seconds": 8,
        "max_poll_attempts": 120,
    }
    if provider_key in {"runway", "kling", "heygen"}:
        defaults["job_timeout_seconds"] = 1800
        defaults["poll_interval_seconds"] = 10
        defaults["max_poll_attempts"] = 180
    if provider_key == "elevenlabs":
        defaults["job_timeout_seconds"] = 600
        defaults["poll_interval_seconds"] = 5
        defaults["max_poll_attempts"] = 120
    return defaults


def build_polling_packet(provider_key: str, provider_job_id: str) -> Dict[str, Any]:
    return {
        "provider_key": provider_key,
        "provider_job_id": provider_job_id,
        "polling_policy": provider_timeout_policy(provider_key),
        "status_map": {
            "queued": ["queued", "pending", "starting"],
            "running": ["running", "processing", "generating"],
            "completed": ["completed", "succeeded", "success"],
            "failed": ["failed", "error", "cancelled", "timeout"],
        },
        "credential_values_exposed": False,
    }


def calculate_provider_health_score(
    *,
    success_count: int = 0,
    failure_count: int = 0,
    timeout_count: int = 0,
    average_latency_ms: Optional[int] = None,
) -> Dict[str, Any]:
    total = max(success_count + failure_count + timeout_count, 1)
    success_ratio = success_count / total
    penalty = (failure_count * 8) + (timeout_count * 12)

    latency_penalty = 0
    if average_latency_ms is not None:
        if average_latency_ms > 120000:
            latency_penalty = 20
        elif average_latency_ms > 60000:
            latency_penalty = 10
        elif average_latency_ms > 30000:
            latency_penalty = 5

    score = max(0, min(100, round((success_ratio * 100) - penalty - latency_penalty)))
    return {
        "health_score": score,
        "success_ratio": round(success_ratio, 4),
        "failure_count": failure_count,
        "timeout_count": timeout_count,
        "average_latency_ms": average_latency_ms,
        "failover_recommended": score < 60,
    }


def build_failover_routing_packet(
    requested_provider: str,
    available_providers: Optional[List[str]] = None,
) -> Dict[str, Any]:
    available = [
        p for p in (available_providers or [])
        if p in SUPPORTED_PROVIDER_KEYS and not _missing_credentials(p)
    ]
    return {
        "requested_provider": requested_provider,
        "available_configured_providers": available,
        "failover_ready": bool(available),
        "fallback_order": available,
        "owner_governed_execution_required": True,
        "credential_values_exposed": False,
    }


def create_signed_asset_delivery_packet(
    *,
    tenant_id: str,
    asset_id: str,
    provider_key: str,
    asset_type: str,
    expires_in_seconds: int = 3600,
) -> Dict[str, Any]:
    secret = os.getenv("ASSET_PACKET_SIGNING_SECRET") or os.getenv("ADMIN_AUTH_SECRET") or "dev-signing-secret"
    expires_at_ms = _now_ms() + (expires_in_seconds * 1000)
    nonce = str(uuid.uuid4())
    payload = f"{tenant_id}:{asset_id}:{provider_key}:{asset_type}:{expires_at_ms}:{nonce}"
    signature = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

    return {
        "tenant_id": tenant_id,
        "asset_id": asset_id,
        "provider_key": provider_key,
        "asset_type": asset_type,
        "expires_at_ms": expires_at_ms,
        "nonce": nonce,
        "signature": signature,
        "download_allowed": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def create_execution_audit_linkage(
    *,
    tenant_id: str,
    request_id: str,
    provider_key: str,
    provider_job_id: Optional[str] = None,
    execution_status: str = "queued",
    started_at_ms: Optional[int] = None,
) -> Dict[str, Any]:
    now = _now_ms()
    started = started_at_ms or now
    return {
        "tenant_id": tenant_id,
        "request_id": request_id,
        "provider_key": provider_key,
        "provider_job_id": provider_job_id,
        "execution_status": execution_status,
        "started_at_ms": started,
        "updated_at_ms": now,
        "latency_ms": max(0, now - started),
        "audit_event_type": "provider_execution_linkage",
        "credential_values_exposed": False,
    }


class GateSafeProviderAdapter:
    provider_key = "base"

    def route(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        return check_provider_gate(
            self.provider_key,
            live_execution_requested=bool(payload.get("live_execution_requested")),
            owner_governed_execution_confirmed=bool(payload.get("owner_governed_execution_confirmed")),
        )

    def execute(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        gate = self.route(payload)
        started = _now_ms()

        if not gate["execution_allowed"]:
            return {
                "provider_key": self.provider_key,
                "status": "blocked",
                "reason": gate["reason"],
                "gate": gate,
                "latency_ms": _now_ms() - started,
                "credential_values_exposed": False,
            }

        return {
            "provider_key": self.provider_key,
            "status": "ready_for_live_provider_call",
            "adapter_mode": "gate_safe_live_capable",
            "request_normalised": True,
            "provider_job_id": None,
            "polling_packet": None,
            "latency_ms": _now_ms() - started,
            "credential_values_exposed": False,
        }


class OpenAIGateSafeAdapter(GateSafeProviderAdapter):
    provider_key = "openai"

    def normalise_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "provider_key": self.provider_key,
            "task_type": payload.get("task_type", "text_or_media_generation"),
            "model": payload.get("model") or payload.get("provider_model") or "provider_default",
            "prompt_present": bool(payload.get("prompt") or payload.get("instructions")),
            "tenant_id": payload.get("tenant_id"),
            "request_id": payload.get("request_id"),
            "credential_values_exposed": False,
        }

    def execute(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        base = super().execute(payload)
        base["adapter_name"] = "openai_live_execution_adapter_v1"
        base["normalised_request"] = self.normalise_request(payload)
        return base


class ReplicateGateSafeAdapter(GateSafeProviderAdapter):
    provider_key = "replicate"


class RunwayGateSafeAdapter(GateSafeProviderAdapter):
    provider_key = "runway"


class KlingGateSafeAdapter(GateSafeProviderAdapter):
    provider_key = "kling"


class HeyGenGateSafeAdapter(GateSafeProviderAdapter):
    provider_key = "heygen"


class ElevenLabsGateSafeAdapter(GateSafeProviderAdapter):
    provider_key = "elevenlabs"


ADAPTERS = {
    "openai": OpenAIGateSafeAdapter(),
    "replicate": ReplicateGateSafeAdapter(),
    "runway": RunwayGateSafeAdapter(),
    "kling": KlingGateSafeAdapter(),
    "heygen": HeyGenGateSafeAdapter(),
    "elevenlabs": ElevenLabsGateSafeAdapter(),
}


def get_live_provider_adapter(provider_key: str) -> Optional[GateSafeProviderAdapter]:
    return ADAPTERS.get((provider_key or "").strip().lower())


def execute_gate_safe_provider_request(provider_key: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    adapter = get_live_provider_adapter(provider_key)
    if not adapter:
        return {
            "provider_key": provider_key,
            "status": "blocked",
            "reason": "unknown_provider_adapter",
            "known_adapter": False,
            "credential_values_exposed": False,
        }
    return adapter.execute(payload or {})


def live_provider_adapter_runtime_status(provider_key: str) -> Dict[str, Any]:
    adapter = get_live_provider_adapter(provider_key)
    if not adapter:
        return {
            "provider_key": provider_key,
            "known_adapter": False,
            "configured": False,
            "ready": False,
            "credential_values_exposed": False,
            "owner_governed_execution_required": True,
        }

    gate = adapter.route({})
    return {
        **gate,
        "adapter_class": adapter.__class__.__name__,
        "timeout_policy": provider_timeout_policy(provider_key),
        "health_scoring_enabled": True,
        "failover_routing_prepared": True,
        "signed_asset_packets_enabled": True,
        "execution_audit_linkage_enabled": True,
    }
