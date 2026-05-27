from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

provider_file = runtime_dir / "provider_connector_registry.py"
test_file = ROOT / "test_global_provider_connector_registry.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if provider_file.exists():
    backup = BACKUP_DIR / f"provider_connector_registry_before_{timestamp}.py"
    backup.write_text(provider_file.read_text(encoding="utf-8"), encoding="utf-8")

provider_file.write_text(r'''
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

    return {
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
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "client_secret_exposure": False,
        "next_stage": "wire_real_provider_api_call_when_key_configured",
        "generated_at": utc_now_iso(),
    }


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
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.provider_connector_registry import (
    PROVIDER_CONNECTORS,
    action_requires_owner_approval,
    choose_provider_for_capability,
    execute_provider_action,
    list_provider_connectors,
    readiness,
)


def main():
    registry = list_provider_connectors(include_secret_status=True)
    ready = readiness()

    text_provider = choose_provider_for_capability("text", "openai")
    image_provider = choose_provider_for_capability("image")
    video_provider = choose_provider_for_capability("video")

    safe_action = execute_provider_action(
        provider_key="openai",
        action_type="marketing_campaign_execution",
        capability="text",
        payload={"brief": "Create governed ecommerce campaign plan."},
        actor_role="owner_admin",
        tenant_id="owner_admin_test",
    )

    blocked_spend = execute_provider_action(
        provider_key="openai",
        action_type="scale_campaign",
        capability="text",
        payload={"budget_increase": 500},
        actor_role="customer",
        tenant_id="client_test",
    )

    print("GLOBAL_PROVIDER_CONNECTOR_REGISTRY_TEST")
    print("provider_count", len(PROVIDER_CONNECTORS))
    print("registry_success", registry["success"])
    print("readiness_status", ready["status"])
    print("text_provider", text_provider)
    print("image_provider", image_provider)
    print("video_provider", video_provider)
    print("safe_action_status", safe_action["status"])
    print("safe_action_governance", safe_action["governance_preserved"])
    print("safe_action_secret_exposure", safe_action["client_secret_exposure"])
    print("blocked_spend_status", blocked_spend["status"])
    print("blocked_spend_execution", blocked_spend["execution_status"])
    print("blocked_spend_governance", blocked_spend["governance_preserved"])
    print("approval_rule_scale_campaign", action_requires_owner_approval("scale_campaign"))

    assert len(PROVIDER_CONNECTORS) >= 6
    assert registry["success"] is True
    assert ready["status"] == "global_provider_connector_registry_ready"
    assert text_provider == "openai"
    assert image_provider in {"openai", "gemini", "image_provider"}
    assert video_provider in {"gemini", "video_provider"}
    assert safe_action["success"] is True
    assert safe_action["provider_execution_attempted"] is False
    assert safe_action["governance_preserved"] is True
    assert safe_action["client_secret_exposure"] is False
    assert blocked_spend["success"] is False
    assert blocked_spend["status"] == "owner_approval_required"
    assert blocked_spend["provider_execution_attempted"] is False
    assert blocked_spend["governance_preserved"] is True

    print("GLOBAL_PROVIDER_CONNECTOR_REGISTRY_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("GLOBAL_PROVIDER_CONNECTOR_REGISTRY_INSTALLED")
print(f"Created/updated: {provider_file}")
print(f"Created/updated: {test_file}")
print("Governance preserved: spend/scaling/contracts remain owner approval gated.")