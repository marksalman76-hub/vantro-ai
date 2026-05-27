import urllib.request
import json

from backend.app.core.ai_generation_service import AIGenerationService, GenerationRequest
from backend.app.core.owner_live_llm_control import owner_live_llm_control
from backend.app.core.openai_sdk_dependency_guard import openai_sdk_dependency_guard
from backend.app.core.llm_provider_credential_readiness import LLMProviderCredentialReadiness


BASE_URL = "http://127.0.0.1:8000"

owner_live_llm_control.set_state(
    enabled=False,
    updated_by="step_100_final_release_readiness",
    reason="Final local release readiness regression keeps live LLM execution blocked.",
)

routes = [
    "/admin/provider-readiness",
    "/admin/provider-execution-audit?limit=5",
    "/admin/openai-sdk-readiness",
    "/admin/live-llm-readiness-dashboard",
    "/admin/live-llm-environment-setup",
    "/admin/llm-provider-stack-summary",
    "/admin/output-quality-summary",
    "/admin/platform-progress-matrix",
    "/admin/operational-dashboard",
]

agent_cases = [
    ("product_copywriting_agent", "store_creation", "Create product page for Glow Serum targeting women 25 to 40 in Dubai."),
    ("ugc_creative_agent", "content_generation", "Create UGC video brief for Glow Serum targeting women 25 to 40 in Dubai."),
    ("product_image_agent", "creative_generation", "Create premium product images for Glow Serum targeting women 25 to 40 in Dubai."),
    ("influencer_collaboration_agent", "creator_strategy", "Create influencer strategy for Glow Serum targeting women 25 to 40 in Dubai."),
    ("analytics_optimisation_agent", "growth_analysis", "Analyse ecommerce performance for Glow Serum targeting women 25 to 40 in Dubai."),
    ("general_ecommerce_agent", "general_strategy", "Create ecommerce growth recommendations for Glow Serum targeting women 25 to 40 in Dubai."),
]

failed = []

print("STEP_100_FINAL_LOCAL_RELEASE_READINESS_RESULTS")

for route in routes:
    try:
        with urllib.request.urlopen(BASE_URL + route, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
            ok = body.get("success") is True
            print(route, ok)
            if not ok:
                failed.append({route: body})
    except Exception as exc:
        print(route, False, exc.__class__.__name__)
        failed.append({route: exc.__class__.__name__})

service = AIGenerationService()

for agent, stage, task in agent_cases:
    result = service.generate(
        GenerationRequest(
            tenant_id="client_demo_001",
            requested_agent=agent,
            workflow_stage=stage,
            task=task,
            region="United Arab Emirates",
            language="Arabic",
            currency="AED",
        )
    )

    provider_execution = result["provider_execution"]
    governed_live_call = provider_execution["metadata"]["governed_live_call"]
    connector = governed_live_call["provider_connector"]

    checks = {
        "client_safe": result.get("client_safe") is True,
        "content_present": bool(result.get("content")),
        "sections_present": isinstance(result.get("sections"), dict),
        "llm_routing_present": "llm_routing" in result,
        "provider_execution_present": "provider_execution" in result,
        "governance_protection_present": "governance_protection" in result,
        "live_call_not_attempted": connector.get("live_call_attempted") is False,
        "credentials_not_exposed": connector["metadata"]["credential_values_exposed"] is False,
        "prompts_not_exposed": connector["metadata"]["internal_prompts_exposed"] is False,
        "backend_config_not_exposed": connector["metadata"]["backend_config_exposed"] is False,
    }

    case_failed = [name for name, passed in checks.items() if not passed]
    print(agent, "failed:", case_failed)

    if case_failed:
        failed.append({agent: case_failed})

sdk = openai_sdk_dependency_guard.check()
readiness = LLMProviderCredentialReadiness().check_selected_provider("openai_primary_pending_connection")

final_checks = {
    "owner_live_control_disabled": owner_live_llm_control.is_enabled() is False,
    "openai_sdk_installed": sdk["installed"] is True,
    "sdk_no_live_call_attempted": sdk["live_call_attempted"] is False,
    "provider_credentials_not_exposed": readiness["credential_values_exposed"] is False,
}

for name, passed in final_checks.items():
    print(name, passed)
    if not passed:
        failed.append({name: passed})

if failed:
    print("FAILED_RELEASE_CHECKS:", failed)
    raise SystemExit(1)

print("STEP_100_FINAL_LOCAL_RELEASE_READINESS_OK")