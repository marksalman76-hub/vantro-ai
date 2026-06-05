import os
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
