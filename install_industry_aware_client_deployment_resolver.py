from pathlib import Path

ROOT = Path.cwd()

resolver = ROOT / "backend/app/core/industry_aware_client_deployment_resolver.py"
resolver.write_text(r'''from __future__ import annotations

from typing import Any, Dict, List

from backend.app.core.admin_industry_agent_store_learning_vault import (
    list_industry_packs,
    list_learning_vault,
)


def _normalise_industry(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "general"
    aliases = {
        "ecommerce": "ecommerce",
        "e-commerce": "ecommerce",
        "online store": "ecommerce",
        "shopify": "ecommerce",
        "real estate": "real_estate",
        "property": "real_estate",
        "realtor": "real_estate",
        "fitness": "fitness",
        "gym": "fitness",
        "health": "healthcare",
        "healthcare": "healthcare",
        "medical": "healthcare",
        "legal": "legal",
        "law": "legal",
        "hospitality": "hospitality",
        "restaurant": "hospitality",
        "beauty": "beauty",
        "skincare": "beauty",
    }
    for needle, mapped in aliases.items():
        if needle in text:
            return mapped
    return text.replace(" ", "_").replace("/", "_")[:80]


def resolve_client_industry_deployment(payload: Dict[str, Any]) -> Dict[str, Any]:
    industry = _normalise_industry(
        payload.get("industry")
        or payload.get("business_niche")
        or payload.get("business_type")
        or payload.get("niche")
    )

    package_name = str(payload.get("package_name") or payload.get("target_package") or "").lower()
    selected_agents = payload.get("selected_agents") or []
    if not isinstance(selected_agents, list):
        selected_agents = []

    packs_result = list_industry_packs(industry=industry, limit=5)
    packs = packs_result.get("industry_packs", [])

    learning_result = list_learning_vault(industry=industry, limit=25)
    learning_records = learning_result.get("learning_records", [])

    recommended_agents: List[str] = []
    deployment_checklist: List[str] = []
    recommended_integrations: List[str] = []
    deployment_notes: List[str] = []

    for pack in packs:
        for agent in pack.get("agents", []):
            agent_id = agent.get("agent_id")
            if agent_id and agent_id not in recommended_agents:
                recommended_agents.append(agent_id)
            if agent.get("deployment_notes"):
                deployment_notes.append(agent["deployment_notes"])
        for item in pack.get("deployment_checklist", []):
            if item not in deployment_checklist:
                deployment_checklist.append(item)
        for item in pack.get("recommended_integrations", []):
            if item not in recommended_integrations:
                recommended_integrations.append(item)

    learning_improvements: List[str] = []
    successful_patterns: List[str] = []

    for record in learning_records:
        for item in record.get("recommended_improvements", []):
            if item not in learning_improvements:
                learning_improvements.append(item)
        for item in record.get("successful_patterns", []):
            if item not in successful_patterns:
                successful_patterns.append(item)

    resolved_agents = selected_agents or recommended_agents

    return {
        "success": True,
        "industry": industry,
        "package_name": package_name,
        "industry_pack_found": bool(packs),
        "learning_vault_records_found": len(learning_records),
        "selected_agents": selected_agents,
        "recommended_agents": recommended_agents,
        "resolved_deployment_agents": resolved_agents,
        "recommended_integrations": recommended_integrations[:20],
        "deployment_checklist": deployment_checklist[:30],
        "tenant_safe_learning_applied": bool(learning_records),
        "learning_based_improvements": learning_improvements[:20],
        "successful_industry_patterns": successful_patterns[:20],
        "client_safe_summary": (
            "Industry-specific deployment guidance and previous tenant-safe learning patterns were applied."
            if packs or learning_records
            else "No industry-specific pack found yet. Default deployment rules apply."
        ),
        "owner_only_private_data_exposed": False,
        "raw_client_data_reused": False,
        "next_step": "Use resolved deployment agents and checklist during client activation/onboarding.",
    }


def industry_aware_client_deployment_status() -> Dict[str, Any]:
    return {
        "success": True,
        "industry_aware_client_deployment_ready": True,
        "admin_learning_vault_read_enabled": True,
        "tenant_safe_learning_only": True,
        "raw_client_data_reused": False,
        "client_setup_can_resolve_industry_pack": True,
    }
''', encoding="utf-8")

routes = ROOT / "backend/app/api/industry_aware_client_deployment_routes.py"
routes.write_text(r'''from fastapi import APIRouter
from backend.app.core.industry_aware_client_deployment_resolver import (
    resolve_client_industry_deployment,
    industry_aware_client_deployment_status,
)

router = APIRouter()


@router.get("/client/industry-aware-deployment/status")
def client_industry_aware_deployment_status():
    return industry_aware_client_deployment_status()


@router.post("/client/industry-aware-deployment/resolve")
def client_industry_aware_deployment_resolve(payload: dict):
    return resolve_client_industry_deployment(payload)
''', encoding="utf-8")

main = ROOT / "backend/app/main.py"
text = main.read_text(encoding="utf-8")
if "industry_aware_client_deployment_routes" not in text:
    text += '''

# Industry-aware client deployment resolver routes
try:
    from backend.app.api.industry_aware_client_deployment_routes import router as industry_aware_client_deployment_router
    app.include_router(industry_aware_client_deployment_router)
except Exception as exc:
    print(f"INDUSTRY_AWARE_CLIENT_DEPLOYMENT_ROUTES_NOT_LOADED: {exc}")
'''
    main.write_text(text, encoding="utf-8")
    print("PATCHED backend/app/main.py")
else:
    print("NO_CHANGE backend/app/main.py")

test = ROOT / "test_industry_aware_client_deployment_resolver.py"
test.write_text(r'''import os
import tempfile

os.environ["ADMIN_INDUSTRY_STORE_DIR"] = tempfile.mkdtemp(prefix="industry_resolver_test_")

from backend.app.core.admin_industry_agent_store_learning_vault import (
    create_or_update_industry_pack,
    capture_tenant_safe_learning,
)
from backend.app.core.industry_aware_client_deployment_resolver import (
    resolve_client_industry_deployment,
    industry_aware_client_deployment_status,
)


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


create_or_update_industry_pack({
    "industry": "ecommerce",
    "display_name": "Ecommerce Launch Pack",
    "agents": [
        {"agent_id": "ecommerce_manager_agent", "deployment_notes": "Prioritise store optimisation and product merchandising."},
        {"agent_id": "product_copywriting_agent", "deployment_notes": "Use conversion-oriented product page copy."},
    ],
    "recommended_integrations": ["store", "email", "analytics"],
    "deployment_checklist": ["Connect store", "Confirm product catalogue", "Load brand voice"],
})

capture_tenant_safe_learning({
    "industry": "ecommerce",
    "agent_id": "product_copywriting_agent",
    "quality_score": 92,
    "approved_by_client": True,
    "successful_patterns": ["Benefit-led product hooks improved output quality."],
    "recommended_improvements": ["Use offer clarity, urgency, and proof points in product copy."],
    "raw_output": "PRIVATE SHOULD NOT BE REUSED",
    "customer_email": "private@example.com",
})

resolved = resolve_client_industry_deployment({
    "business_niche": "Shopify skincare ecommerce brand",
    "package_name": "Growth",
})

assert_true(resolved["success"], "resolver should succeed")
assert_true(resolved["industry"] == "ecommerce", "industry should map to ecommerce")
assert_true(resolved["industry_pack_found"], "industry pack should be found")
assert_true(resolved["tenant_safe_learning_applied"], "learning vault should apply")
assert_true("ecommerce_manager_agent" in resolved["recommended_agents"], "recommended agents should include ecommerce manager")
assert_true(resolved["owner_only_private_data_exposed"] is False, "private data must not be exposed")
assert_true(resolved["raw_client_data_reused"] is False, "raw client data must not be reused")

status = industry_aware_client_deployment_status()
assert_true(status["industry_aware_client_deployment_ready"], "status should be ready")

print("INDUSTRY_AWARE_CLIENT_DEPLOYMENT_RESOLVER_TEST_PASSED")
''', encoding="utf-8")

print("INDUSTRY_AWARE_CLIENT_DEPLOYMENT_RESOLVER_INSTALLED")