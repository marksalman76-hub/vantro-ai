from pathlib import Path
from datetime import datetime

ROOT = Path(".")
BRIDGE_PATH = Path("backend/app/runtime/canonical_agent_identity_bridge.py")
PROVIDER_PATH = Path("backend/app/runtime/global_provider_execution_runtime.py")

backup_dir = Path("backups") / ("canonical_agent_identity_bridge_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

for path in [BRIDGE_PATH, PROVIDER_PATH]:
    if path.exists():
        (backup_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

BRIDGE_PATH.parent.mkdir(parents=True, exist_ok=True)

BRIDGE_PATH.write_text('''from __future__ import annotations

from typing import Any, Dict


CANONICAL_AGENT_ALIASES: Dict[str, str] = {
    # Website / app builder aliases
    "custom_websites_landing_pages_apps_agent": "website_landing_apps_agent",
    "website_app_agent": "website_landing_apps_agent",
    "custom_website_agent": "website_landing_apps_agent",
    "store_builder_agent": "website_landing_apps_agent",

    # Analytics aliases
    "analytics_intelligence_agent": "analytics_optimisation_agent",
    "analytics_agent": "analytics_optimisation_agent",
    "analytics_reporting_agent": "analytics_optimisation_agent",

    # Ads aliases
    "ad_creative_agent": "paid_ads_agent",
    "ads_optimisation_agent": "paid_ads_agent",
    "paid_ads_agent": "paid_ads_agent",

    # UGC/media aliases
    "ugc_media_agent": "ugc_creative_agent",
    "ugc_agent": "ugc_creative_agent",

    # CRM aliases
    "crm_agent": "crm_ai_agent",

    # Social aliases
    "social_media_content_agent": "social_media_manager_content_creator_agent",
    "social_media_agent": "social_media_manager_content_creator_agent",

    # Lead generator aliases
    "lead_generator_agent": "lead_generator_appointment_setter_agent",

    # Product image/copy aliases
    "product_image_generation_agent": "product_image_agent",
    "product_copywriting_agent": "product_research_agent",

    # System agent aliases
    "qa_testing_agent": "qa_testing_agent",
    "billing_optimisation_agent": "billing_optimisation_agent",
    "training_learning_agent": "training_learning_agent",
    "security_compliance_agent": "security_compliance_agent",
    "integration_automation_agent": "integration_automation_agent",
    "orchestration_agent": "orchestration_agent",

    # Already canonical agents
    "head_agent": "head_agent",
    "strategist_agent": "strategist_agent",
    "business_growth_partnerships_agent": "business_growth_partnerships_agent",
    "seo_agent": "seo_agent",
    "email_reply_agent": "email_reply_agent",
    "receptionist_agent": "receptionist_agent",
    "product_development_agent": "product_development_agent",
    "ecommerce_agent": "ecommerce_agent",
    "demo_trial_agent": "demo_trial_agent",
    "influencer_collaboration_agent": "influencer_collaboration_agent",
}


def normalise_agent_identity(agent_id: Any) -> str:
    raw = str(agent_id or "").strip().lower().replace(" ", "_").replace("-", "_")
    return CANONICAL_AGENT_ALIASES.get(raw, raw)


def normalise_agent_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    clean = dict(payload or {})

    raw_agent = (
        clean.get("requested_agent")
        or clean.get("agent_id")
        or clean.get("agent_key")
        or clean.get("agent")
        or ""
    )

    canonical = normalise_agent_identity(raw_agent)

    if canonical:
        clean["requested_agent"] = canonical
        clean["agent_id"] = canonical
        clean["agent_key"] = canonical

    clean["canonical_agent_identity_applied"] = True
    clean["original_agent_identity"] = raw_agent
    clean["canonical_agent_identity"] = canonical

    return clean


def canonical_agent_identity_status() -> Dict[str, Any]:
    return {
        "success": True,
        "canonical_agent_identity_bridge_ready": True,
        "alias_count": len(CANONICAL_AGENT_ALIASES),
        "credential_values_exposed": False,
        "client_safe": True,
    }
''', encoding="utf-8")

provider_text = PROVIDER_PATH.read_text(encoding="utf-8")

if "canonical_agent_identity_bridge" not in provider_text:
    provider_text = provider_text.replace(
        "from typing import Any, Dict, List\\n",
        "from typing import Any, Dict, List\\n\\nfrom backend.app.runtime.canonical_agent_identity_bridge import normalise_agent_identity, normalise_agent_payload\\n",
    )

provider_text = provider_text.replace(
    '''def normalise_agent_id(agent_id: str) -> str:
    return str(agent_id or "").strip().lower()
''',
    '''def normalise_agent_id(agent_id: str) -> str:
    return normalise_agent_identity(agent_id)
'''
)

provider_text = provider_text.replace(
    '''def build_global_provider_chain(agent_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    agent = get_agent_capabilities(agent_id)
''',
    '''def build_global_provider_chain(agent_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = normalise_agent_payload(payload or {})
    agent_id = normalise_agent_id(agent_id)
    agent = get_agent_capabilities(agent_id)
'''
)

provider_text = provider_text.replace(
    '''    agent_id = (
        payload.get("requested_agent")
        or payload.get("agent_id")
        or payload.get("agent")
        or "unknown_agent"
    )
''',
    '''    payload = normalise_agent_payload(payload or {})
    agent_id = (
        payload.get("requested_agent")
        or payload.get("agent_id")
        or payload.get("agent")
        or "unknown_agent"
    )
'''
)

PROVIDER_PATH.write_text(provider_text, encoding="utf-8")

print("CANONICAL_AGENT_IDENTITY_BRIDGE_INSTALLED")
print("Backup:", backup_dir)
print("Created:", BRIDGE_PATH)
print("Updated:", PROVIDER_PATH)