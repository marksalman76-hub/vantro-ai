from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
RUNTIME = ROOT / "backend" / "app" / "runtime"
BACKUPS = ROOT / "backups"

RUNTIME.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_file = RUNTIME / "global_real_provider_connector_layer.py"
test_file = ROOT / "test_global_real_provider_connector_layer.py"

if runtime_file.exists():
    (BACKUPS / f"global_real_provider_connector_layer_before_{stamp}.py").write_text(
        runtime_file.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

runtime_file.write_text(r'''
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from backend.app.runtime.global_provider_execution_runtime import build_global_provider_execution_packet


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


CONNECTOR_FAMILIES = {
    "llm_content": {
        "providers": ["openai", "anthropic", "gemini", "xai"],
        "output_types": ["strategy", "copy", "analysis", "support", "email", "crm", "website", "seo"],
    },
    "business_execution": {
        "providers": ["ghl", "hubspot", "shopify", "stripe", "email"],
        "output_types": ["crm_action", "email_action", "store_action", "billing_action"],
    },
    "media_generation": {
        "providers": ["runway", "kling", "heygen", "elevenlabs", "replicate"],
        "output_types": ["video", "image", "voice", "dubbing", "avatar"],
    },
    "asset_delivery": {
        "providers": ["cdn", "signed_storage", "customer_delivery"],
        "output_types": ["download", "preview", "review_packet", "delivery_packet"],
    },
}


def classify_connector_family(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = " ".join([
        str(payload.get("requested_agent", "")),
        str(payload.get("agent_id", "")),
        str(payload.get("workflow_stage", "")),
        str(payload.get("action_type", "")),
        str(payload.get("task", "")),
    ]).lower()

    if any(term in text for term in ["crm", "email", "shopify", "stripe", "billing", "integration", "follow_up"]):
        family = "business_execution"
    elif any(term in text for term in ["video", "image", "voice", "dubbing", "avatar", "media", "ugc"]):
        family = "media_generation"
    elif any(term in text for term in ["download", "preview", "delivery", "asset"]):
        family = "asset_delivery"
    else:
        family = "llm_content"

    config = CONNECTOR_FAMILIES[family]

    return {
        "success": True,
        "connector_family": family,
        "provider_candidates": config["providers"],
        "output_types": config["output_types"],
        "global_scope": True,
        "governance_preserved": True,
        "internal_config_exposed": False,
    }


def build_global_connector_execution_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    provider_packet = build_global_provider_execution_packet(payload)
    family = classify_connector_family(payload)

    connector_id = "global_connector_" + uuid.uuid4().hex[:16]

    live_allowed = bool(provider_packet.get("live_execution_allowed"))

    return {
        "success": True,
        "connector_id": connector_id,
        "runtime": "global_real_provider_connector_layer",
        "scope": "platform_wide_multi_agent",
        "tenant_id": payload.get("tenant_id", "tenant_unknown"),
        "agent_id": payload.get("requested_agent") or payload.get("agent_id") or "unknown_agent",
        "workflow_stage": payload.get("workflow_stage", ""),
        "action_type": payload.get("action_type", ""),
        "connector_family": family,
        "provider_packet": provider_packet,
        "execution_state": "ready_for_live_connector_execution" if live_allowed else "prepared_blocked_until_provider_ready",
        "live_execution_allowed": live_allowed,
        "connector_contract": {
            "input_payload_required": True,
            "tenant_isolation_required": True,
            "owner_gate_required_for_sensitive_actions": True,
            "quality_gate_required_for_client_delivery": True,
            "result_persistence_required": True,
            "customer_safe_delivery_required": True,
            "secrets_never_returned": True,
        },
        "result_packet_shape": {
            "execution_id": "required",
            "connector_family": family["connector_family"],
            "provider": "selected_by_global_provider_runtime",
            "status": "queued|processing|completed|failed|blocked",
            "customer_safe_status": "required",
            "result": "client_safe_result_only",
            "asset_packet": "optional",
            "audit": "required",
        },
        "customer_safe_status": (
            "Ready for live execution"
            if live_allowed
            else "Prepared; provider credentials or owner live-execution controls not enabled"
        ),
        "created_at": now_iso(),
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "layout_changes": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }


def global_real_provider_connector_readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "runtime": "global_real_provider_connector_layer",
        "status": "ready",
        "scope": "platform_wide_multi_agent",
        "connector_families": CONNECTOR_FAMILIES,
        "capabilities": [
            "global_connector_family_classification",
            "all_agent_connector_packet_creation",
            "llm_content_connector_contract",
            "business_execution_connector_contract",
            "media_generation_connector_contract",
            "asset_delivery_connector_contract",
            "governed_live_execution_gate_integration",
            "result_packet_standardisation",
            "customer_safe_delivery_contract",
        ],
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "layout_changes": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }
''', encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.global_real_provider_connector_layer import (
    global_real_provider_connector_readiness,
    classify_connector_family,
    build_global_connector_execution_packet,
)


def run():
    readiness = global_real_provider_connector_readiness()
    assert readiness["success"] is True
    assert readiness["status"] == "ready"
    assert readiness["scope"] == "platform_wide_multi_agent"
    assert readiness["credential_values_exposed"] is False

    cases = [
        ("marketing_specialist_agent", "marketing_campaign", "create_ad_copy_brief", "llm_content"),
        ("crm_ai_agent", "crm_optimisation", "crm_recommendation", "business_execution"),
        ("website_landing_apps_agent", "website_landing_page", "create_landing_page_brief", "llm_content"),
        ("analytics_optimisation_agent", "analytics_optimisation", "analytics_report_generation", "llm_content"),
        ("product_image_agent", "product_image_direction", "create_product_image_brief", "media_generation"),
        ("customer_support_agent", "customer_support", "support_response_generation", "llm_content"),
    ]

    for agent, stage, action, expected_family in cases:
        payload = {
            "tenant_id": "tenant_test",
            "requested_agent": agent,
            "workflow_stage": stage,
            "action_type": action,
            "task": f"Test global connector for {agent}",
        }

        family = classify_connector_family(payload)
        assert family["success"] is True
        assert family["connector_family"] == expected_family

        packet = build_global_connector_execution_packet(payload)
        assert packet["success"] is True
        assert packet["scope"] == "platform_wide_multi_agent"
        assert packet["connector_contract"]["tenant_isolation_required"] is True
        assert packet["credential_values_exposed"] is False
        assert packet["governance_preserved"] is True

    print("GLOBAL_REAL_PROVIDER_CONNECTOR_LAYER_OK")


if __name__ == "__main__":
    run()
''', encoding="utf-8")

print("GLOBAL_REAL_PROVIDER_CONNECTOR_LAYER_INSTALLED")
print(f"Created/updated: {runtime_file}")
print(f"Created/updated: {test_file}")