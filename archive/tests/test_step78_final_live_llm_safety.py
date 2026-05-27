from backend.app.core.ai_generation_service import AIGenerationService, GenerationRequest
from backend.app.core.owner_live_llm_control import owner_live_llm_control
from backend.app.core.provider_execution_audit_log import provider_execution_audit_log


owner_live_llm_control.set_state(
    enabled=False,
    updated_by="step_78_safety_test",
    reason="Verify live LLM execution stays blocked when owner control is disabled.",
)

result = AIGenerationService().generate(
    GenerationRequest(
        tenant_id="client_demo_001",
        requested_agent="ugc_creative_agent",
        workflow_stage="content_generation",
        task="Create UGC video brief for Glow Serum targeting women 25 to 40 in Dubai.",
        region="United Arab Emirates",
        language="Arabic",
        currency="AED",
    )
)

provider_execution = result["provider_execution"]
governed_live_call = provider_execution["metadata"]["governed_live_call"]
live_gate = governed_live_call["live_execution_gate"]
provider_connector = governed_live_call["provider_connector"]
audit = provider_execution["metadata"]["provider_execution_audit"]
latest_audit = provider_execution_audit_log.latest(1)

checks = {
    "client_safe": result["client_safe"] is True,
    "llm_routing_present": "llm_routing" in result,
    "provider_execution_present": "provider_execution" in result,
    "governance_protection_present": "governance_protection" in result,
    "live_execution_blocked": live_gate["live_execution_allowed"] is False,
    "live_call_not_attempted": provider_connector["live_call_attempted"] is False,
    "credential_values_not_exposed": provider_connector["metadata"]["credential_values_exposed"] is False,
    "internal_prompts_not_exposed": provider_connector["metadata"]["internal_prompts_exposed"] is False,
    "backend_config_not_exposed": provider_connector["metadata"]["backend_config_exposed"] is False,
    "audit_stored": audit["stored"] is True,
    "audit_credentials_not_stored": audit["credential_values_stored"] is False,
    "audit_prompts_not_stored": audit["internal_prompts_stored"] is False,
    "latest_audit_available": latest_audit["count"] >= 1,
}

failed = [name for name, passed in checks.items() if not passed]

print("STEP_78_FINAL_LIVE_LLM_SAFETY_RESULTS")
for name, passed in checks.items():
    print(f"{name}: {passed}")

if failed:
    print("FAILED_CHECKS:", failed)
    raise SystemExit(1)

print("STEP_78_FINAL_LIVE_LLM_SAFETY_TEST_OK")