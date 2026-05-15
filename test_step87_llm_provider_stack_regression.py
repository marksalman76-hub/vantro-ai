from backend.app.core.ai_generation_service import AIGenerationService, GenerationRequest
from backend.app.core.llm_provider_credential_readiness import LLMProviderCredentialReadiness
from backend.app.core.openai_sdk_dependency_guard import openai_sdk_dependency_guard
from backend.app.core.owner_live_llm_control import owner_live_llm_control
from backend.app.core.live_llm_execution_gate import LiveLLMExecutionGate, LiveLLMExecutionGateRequest
from backend.app.core.provider_execution_audit_log import provider_execution_audit_log


owner_live_llm_control.set_state(
    enabled=False,
    updated_by="step_87_regression_test",
    reason="Final LLM provider stack regression test must keep live execution blocked.",
)

generation = AIGenerationService().generate(
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

readiness = LLMProviderCredentialReadiness().check_selected_provider(
    "openai_primary_pending_connection"
)

sdk = openai_sdk_dependency_guard.check()

gate = LiveLLMExecutionGate().evaluate(
    LiveLLMExecutionGateRequest(
        tenant_id="client_demo_001",
        agent_id="ugc_creative_agent",
        task_type="premium_ugc_video_execution_brief",
        provider="openai",
        provider_ready=bool(readiness["provider_ready"]),
    )
)

provider_execution = generation["provider_execution"]
governed_live_call = provider_execution["metadata"]["governed_live_call"]
provider_connector = governed_live_call["provider_connector"]
live_execution_gate = governed_live_call["live_execution_gate"]
audit = provider_execution["metadata"]["provider_execution_audit"]
latest_audit = provider_execution_audit_log.latest(3)

checks = {
    "generation_client_safe": generation["client_safe"] is True,
    "llm_routing_present": "llm_routing" in generation,
    "provider_execution_present": "provider_execution" in generation,
    "governance_protection_present": "governance_protection" in generation,
    "openai_provider_normalised": readiness["normalised_provider"] == "openai",
    "credential_values_not_exposed": readiness["credential_values_exposed"] is False,
    "sdk_installed": sdk["installed"] is True,
    "sdk_no_live_call_attempted": sdk["live_call_attempted"] is False,
    "owner_control_disabled": owner_live_llm_control.is_enabled() is False,
    "standalone_gate_blocks_live": gate.live_execution_allowed is False,
    "embedded_gate_blocks_live": live_execution_gate["live_execution_allowed"] is False,
    "provider_connector_no_live_attempt": provider_connector["live_call_attempted"] is False,
    "provider_connector_no_live_completion": provider_connector["live_call_completed"] is False,
    "provider_connector_credentials_hidden": provider_connector["metadata"]["credential_values_exposed"] is False,
    "provider_connector_prompts_hidden": provider_connector["metadata"]["internal_prompts_exposed"] is False,
    "provider_connector_backend_config_hidden": provider_connector["metadata"]["backend_config_exposed"] is False,
    "audit_stored": audit["stored"] is True,
    "audit_credentials_not_stored": audit["credential_values_stored"] is False,
    "audit_prompts_not_stored": audit["internal_prompts_stored"] is False,
    "latest_audit_available": latest_audit["count"] >= 1,
}

failed = [name for name, passed in checks.items() if not passed]

print("STEP_87_LLM_PROVIDER_STACK_REGRESSION_RESULTS")
print("generation_output_type:", generation["output_type"])
print("selected_provider:", generation["llm_routing"]["selected_provider"])
print("provider_ready:", readiness["provider_ready"])
print("sdk_installed:", sdk["installed"])
print("owner_control_enabled:", owner_live_llm_control.is_enabled())
print("standalone_gate_mode:", gate.execution_mode)
print("embedded_gate_mode:", live_execution_gate["execution_mode"])
print("connector_mode:", provider_connector["execution_mode"])
print("latest_audit_count:", latest_audit["count"])

for name, passed in checks.items():
    print(f"{name}: {passed}")

if failed:
    print("FAILED_CHECKS:", failed)
    raise SystemExit(1)

print("STEP_87_LLM_PROVIDER_STACK_REGRESSION_OK")