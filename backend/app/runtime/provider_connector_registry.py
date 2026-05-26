"""
Global provider connector registry.

Purpose:
- Provide one governed interface for AI/model/media providers.
- Keep provider execution behind runtime governance.
- Avoid agent-by-agent provider wiring.
- Preserve owner approval controls for spend, scaling, contracts, publishing, and high-risk actions.

This module does not expose secrets to frontend/client UI.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.app.runtime.provider_result_quality_loop import (
    apply_quality_loop_to_provider_result,
    decide_retry_from_quality,
)


OWNER_APPROVAL_ACTIONS = {
    "increase_ad_spend",
    "scale_campaign",
    "change_budget",
    "approve_contract",
    "sign_contract",
    "purchase_media",
    "publish_live_campaign",
    "commit_financial_action",
}


@dataclass(frozen=True)
class ProviderConnector:
    provider_key: str
    display_name: str
    category: str
    env_key: str
    supports_text: bool = False
    supports_image: bool = False
    supports_video: bool = False
    supports_audio: bool = False
    supports_embeddings: bool = False
    supports_tool_calling: bool = False
    owner_approval_required_for_spend: bool = True


PROVIDER_CONNECTORS: Dict[str, ProviderConnector] = {
    "openai": ProviderConnector(
        provider_key="openai",
        display_name="OpenAI",
        category="llm",
        env_key="OPENAI_API_KEY",
        supports_text=True,
        supports_image=True,
        supports_embeddings=True,
        supports_tool_calling=True,
    ),
    "anthropic": ProviderConnector(
        provider_key="anthropic",
        display_name="Anthropic",
        category="llm",
        env_key="ANTHROPIC_API_KEY",
        supports_text=True,
        supports_tool_calling=True,
    ),
    "gemini": ProviderConnector(
        provider_key="gemini",
        display_name="Google Gemini",
        category="llm",
        env_key="GOOGLE_API_KEY",
        supports_text=True,
        supports_image=True,
        supports_video=True,
        supports_tool_calling=True,
    ),
    "xai": ProviderConnector(
        provider_key="xai",
        display_name="xAI",
        category="llm",
        env_key="XAI_API_KEY",
        supports_text=True,
        supports_tool_calling=True,
    ),
    "image_provider": ProviderConnector(
        provider_key="image_provider",
        display_name="Image Generation Provider",
        category="media",
        env_key="IMAGE_PROVIDER_API_KEY",
        supports_image=True,
    ),
    "video_provider": ProviderConnector(
        provider_key="video_provider",
        display_name="Video Generation Provider",
        category="media",
        env_key="VIDEO_PROVIDER_API_KEY",
        supports_video=True,
        supports_audio=True,
    ),
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def provider_available(provider_key: str) -> bool:
    connector = PROVIDER_CONNECTORS.get(provider_key)
    if not connector:
        return False
    return bool(os.getenv(connector.env_key, "").strip())


def list_provider_connectors(include_secret_status: bool = False) -> Dict[str, Any]:
    providers = {}

    for key, connector in PROVIDER_CONNECTORS.items():
        record = {
            "provider_key": connector.provider_key,
            "display_name": connector.display_name,
            "category": connector.category,
            "configured": provider_available(key),
            "capabilities": {
                "text": connector.supports_text,
                "image": connector.supports_image,
                "video": connector.supports_video,
                "audio": connector.supports_audio,
                "embeddings": connector.supports_embeddings,
                "tool_calling": connector.supports_tool_calling,
            },
            "owner_approval_required_for_spend": connector.owner_approval_required_for_spend,
        }

        if include_secret_status:
            record["env_key"] = connector.env_key
            record["secret_value_exposed"] = False

        providers[key] = record

    return {
        "success": True,
        "registry": "global_provider_connector_registry",
        "generated_at": utc_now_iso(),
        "provider_count": len(providers),
        "providers": providers,
        "governance_preserved": True,
        "client_secret_exposure": False,
    }


def action_requires_owner_approval(action_type: Optional[str]) -> bool:
    if not action_type:
        return False
    return str(action_type).strip().lower() in OWNER_APPROVAL_ACTIONS


def choose_provider_for_capability(
    capability: str,
    preferred_provider: Optional[str] = None,
) -> Optional[str]:
    capability = str(capability or "").strip().lower()

    if preferred_provider:
        preferred_provider = preferred_provider.strip().lower()
        connector = PROVIDER_CONNECTORS.get(preferred_provider)
        if connector and _connector_supports(connector, capability):
            return preferred_provider

    for key, connector in PROVIDER_CONNECTORS.items():
        if provider_available(key) and _connector_supports(connector, capability):
            return key

    for key, connector in PROVIDER_CONNECTORS.items():
        if _connector_supports(connector, capability):
            return key

    return None


def _connector_supports(connector: ProviderConnector, capability: str) -> bool:
    return {
        "text": connector.supports_text,
        "image": connector.supports_image,
        "video": connector.supports_video,
        "audio": connector.supports_audio,
        "embeddings": connector.supports_embeddings,
        "tool_calling": connector.supports_tool_calling,
    }.get(capability, False)


def execute_provider_action(
    provider_key: Optional[str],
    action_type: str,
    payload: Optional[Dict[str, Any]] = None,
    capability: str = "text",
    actor_role: str = "system",
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Safe provider execution envelope.

    This foundation intentionally returns a governed execution packet.
    Real API calls are added behind this function per provider once keys are configured.
    """

    payload = payload or {}
    selected_provider = provider_key or choose_provider_for_capability(capability)
    connector = PROVIDER_CONNECTORS.get(str(selected_provider or "").lower())

    if action_requires_owner_approval(action_type):
        return {
            "success": False,
            "status": "owner_approval_required",
            "execution_status": "blocked_pending_owner_approval",
            "provider_execution_attempted": False,
            "provider_key": selected_provider,
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "governance_preserved": True,
            "reason": "This action may affect spend, scaling, contracts, publishing, or financial commitment.",
            "generated_at": utc_now_iso(),
        }

    if not connector:
        return {
            "success": False,
            "status": "provider_not_supported",
            "execution_status": "blocked",
            "provider_execution_attempted": False,
            "provider_key": selected_provider,
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "governance_preserved": True,
            "generated_at": utc_now_iso(),
        }

    if not _connector_supports(connector, capability):
        return {
            "success": False,
            "status": "capability_not_supported",
            "execution_status": "blocked",
            "provider_execution_attempted": False,
            "provider_key": connector.provider_key,
            "capability": capability,
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "governance_preserved": True,
            "generated_at": utc_now_iso(),
        }

    configured = provider_available(connector.provider_key)

    if connector.provider_key == "openai" and capability == "text":
        return _safe_openai_text_execution(
            action_type=action_type,
            payload=payload,
            tenant_id=tenant_id,
            actor_role=actor_role,
        )

    return _with_provider_quality_loop({
        "success": True,
        "status": "provider_action_ready",
        "execution_status": "provider_connector_ready",
        "provider_execution_attempted": False,
        "real_provider_configured": configured,
        "provider_key": connector.provider_key,
        "display_name": connector.display_name,
        "category": connector.category,
        "capability": capability,
        "action_type": action_type,
        "tenant_id": tenant_id,
        "actor_role": actor_role,
        "payload_received": bool(payload),
        "payload_keys": sorted(list(payload.keys())),
        "output_text": "Provider connector is ready. Configure the provider API key for live premium output generation.",
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "client_secret_exposure": False,
        "next_stage": "wire_real_provider_api_call_when_key_configured",
        "generated_at": utc_now_iso(),
    }, task_type=action_type)


def readiness() -> Dict[str, Any]:
    registry = list_provider_connectors(include_secret_status=True)
    configured = [
        key for key, record in registry["providers"].items()
        if record["configured"]
    ]

    return {
        "success": True,
        "status": "global_provider_connector_registry_ready",
        "provider_count": registry["provider_count"],
        "configured_provider_count": len(configured),
        "configured_providers": configured,
        "required_env_keys": {
            key: record["env_key"]
            for key, record in registry["providers"].items()
        },
        "governance_preserved": True,
        "owner_approval_required_for_spend_scaling_contracts": True,
        "client_secret_exposure": False,
        "generated_at": utc_now_iso(),
    }

# --- Real OpenAI provider execution path ---
# Safe-by-default. No API call is attempted unless OPENAI_API_KEY is configured.

def _safe_openai_text_execution(action_type, payload, tenant_id=None, actor_role="system"):
    import json
    import os
    import urllib.request
    import urllib.error

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _with_provider_quality_loop({
            "success": True,
            "status": "provider_action_ready",
            "execution_status": "provider_connector_ready",
            "provider_execution_attempted": False,
            "real_provider_configured": False,
            "provider_key": "openai",
            "display_name": "OpenAI",
            "category": "llm",
            "capability": "text",
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "payload_received": bool(payload),
            "payload_keys": sorted(list((payload or {}).keys())),
            "output_text": "Provider connector is ready. Configure OPENAI_API_KEY for live premium output generation.",
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "next_stage": "configure_OPENAI_API_KEY_for_live_provider_execution",
            "generated_at": utc_now_iso(),
        }, task_type=action_type)

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"

    business = payload.get("business") or payload.get("brand") or payload.get("company") or "the client business"
    goal = payload.get("goal") or payload.get("task") or payload.get("brief") or "produce a premium ecommerce execution output"

    prompt = (
        "You are operating inside a governed ecommerce AI workforce platform. "
        "Produce a concise, premium, commercially useful output. "
        "Do not claim to spend money, publish, scale campaigns, sign contracts, or perform external actions. "
        f"Business/context: {business}. "
        f"Goal/task: {goal}. "
        f"Input payload: {json.dumps(payload, ensure_ascii=False)[:4000]}"
    )

    request_payload = {
        "model": model,
        "input": prompt,
        "max_output_tokens": 900,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)

        output_text = ""
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output_text += content.get("text", "")

        return _with_provider_quality_loop({
            "success": True,
            "status": "provider_execution_completed",
            "execution_status": "completed",
            "provider_execution_attempted": True,
            "real_provider_configured": True,
            "provider_key": "openai",
            "display_name": "OpenAI",
            "category": "llm",
            "capability": "text",
            "model": model,
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "output_text": output_text.strip(),
            "raw_provider_id": data.get("id"),
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "generated_at": utc_now_iso(),
        }, task_type=action_type)

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")[:1200]
        return {
            "success": False,
            "status": "provider_execution_failed",
            "execution_status": "failed",
            "provider_execution_attempted": True,
            "real_provider_configured": True,
            "provider_key": "openai",
            "display_name": "OpenAI",
            "category": "llm",
            "capability": "text",
            "model": model,
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "http_status": exc.code,
            "error": error_body,
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "generated_at": utc_now_iso(),
        }

    except Exception as exc:
        return {
            "success": False,
            "status": "provider_execution_failed",
            "execution_status": "failed",
            "provider_execution_attempted": True,
            "real_provider_configured": True,
            "provider_key": "openai",
            "display_name": "OpenAI",
            "category": "llm",
            "capability": "text",
            "model": model,
            "action_type": action_type,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "error": str(exc)[:1200],
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "client_secret_exposure": False,
            "generated_at": utc_now_iso(),
        }

# --- Provider result quality loop bridge ---

def _with_provider_quality_loop(result, task_type=None, minimum_score=72):
    try:
        quality_result = apply_quality_loop_to_provider_result(
            result,
            task_type=task_type or result.get("action_type"),
            minimum_score=minimum_score,
        )
        retry_decision = decide_retry_from_quality(
            quality_result,
            retry_count=int(result.get("retry_count", 0) or 0),
            max_retries=int(result.get("max_retries", 3) or 3),
        )
        quality_result["quality_retry_decision"] = retry_decision
        return quality_result
    except Exception as exc:
        safe_result = dict(result)
        safe_result.update(
            {
                "quality_loop_applied": False,
                "quality_loop_error": str(exc)[:500],
                "quality_gate_passed": False,
                "finalisation_status": "requires_manual_review",
                "governance_preserved": True,
                "owner_approval_controls_preserved": True,
            }
        )
        return safe_result


def extract_ai_media_provider_ready_packet(payload):
    if not isinstance(payload, dict):
        return None

    if isinstance(payload.get("provider_ready_execution_packet"), dict):
        return payload.get("provider_ready_execution_packet")

    orchestration_packet = payload.get("orchestration_packet")
    if isinstance(orchestration_packet, dict):
        packet = orchestration_packet.get("provider_ready_execution_packet")
        if isinstance(packet, dict):
            return packet

    creative_direction = payload.get("creative_direction")
    if isinstance(creative_direction, dict):
        nested_orchestration = creative_direction.get("orchestration_packet")
        if isinstance(nested_orchestration, dict):
            packet = nested_orchestration.get("provider_ready_execution_packet")
            if isinstance(packet, dict):
                return packet

    return None


def enrich_provider_payload_with_ai_media_packet(payload):
    if not isinstance(payload, dict):
        return payload

    provider_ready_packet = extract_ai_media_provider_ready_packet(payload)

    if not provider_ready_packet:
        return payload

    enriched = dict(payload)
    enriched["ai_media_provider_ready_packet"] = provider_ready_packet
    enriched["provider_payload_enriched"] = True
    enriched["provider_packet_type"] = provider_ready_packet.get("packet_type")
    enriched["provider_execution_allowed"] = provider_ready_packet.get("execution_allowed", True)
    enriched["provider_manual_review_required"] = provider_ready_packet.get("manual_review_required", False)
    enriched["provider_primary_slot"] = provider_ready_packet.get("primary_provider_slot")
    enriched["provider_fallback_slots"] = provider_ready_packet.get("fallback_provider_slots", [])
    enriched["provider_parameters"] = provider_ready_packet.get("provider_parameters", {})
    enriched["provider_continuity_controls"] = provider_ready_packet.get("continuity_controls", {})
    enriched["provider_multilingual_controls"] = provider_ready_packet.get("multilingual_controls", {})
    enriched["provider_fallback_controls"] = provider_ready_packet.get("fallback_controls", {})
    enriched["provider_governance_controls"] = provider_ready_packet.get("governance_controls", {})
    enriched["provider_quality_controls"] = provider_ready_packet.get("quality_controls", {})

    return enriched

