from backend.app.core.owner_live_llm_control import owner_live_llm_control
from backend.app.core.llm_provider_credential_readiness import LLMProviderCredentialReadiness
from backend.app.core.openai_sdk_dependency_guard import openai_sdk_dependency_guard
from backend.app.core.live_llm_execution_gate import LiveLLMExecutionGate, LiveLLMExecutionGateRequest
from backend.app.core.safe_openai_live_connector import (
    SafeOpenAILiveConnector,
    SafeOpenAIConnectorRequest,
)


owner_live_llm_control.set_state(
    enabled=True,
    updated_by="step_85_controlled_live_activation_test",
    reason="Controlled local test to verify live LLM activation gates without exposing secrets.",
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

connector_result = SafeOpenAILiveConnector().execute(
    SafeOpenAIConnectorRequest(
        tenant_id="client_demo_001",
        agent_id="ugc_creative_agent",
        task_type="premium_ugc_video_execution_brief",
        model_class="premium_reasoning_and_generation",
        region="United Arab Emirates",
        language="Arabic",
        payload={
            "task": "Create a short premium ecommerce UGC hook for Glow Serum. Keep it client-safe.",
            "workflow_stage": "controlled_live_activation_test",
            "generated_output_type": "premium_ugc_video_execution_brief",
        },
        provider_ready=bool(readiness["provider_ready"]),
        live_execution_allowed=bool(gate.live_execution_allowed),
    )
)

checks = {
    "sdk_installed": sdk["installed"] is True,
    "owner_control_enabled": owner_live_llm_control.is_enabled() is True,
    "credential_values_not_exposed": readiness["credential_values_exposed"] is False,
    "connector_credentials_not_exposed": connector_result.metadata["credential_values_exposed"] is False,
    "connector_prompts_not_exposed": connector_result.metadata["internal_prompts_exposed"] is False,
    "connector_backend_config_not_exposed": connector_result.metadata["backend_config_exposed"] is False,
}

print("STEP_85_CONTROLLED_LIVE_LLM_ACTIVATION_RESULTS")
print("provider_ready:", readiness["provider_ready"])
print("sdk_installed:", sdk["installed"])
print("gate_execution_mode:", gate.execution_mode)
print("gate_live_execution_allowed:", gate.live_execution_allowed)
print("connector_execution_mode:", connector_result.execution_mode)
print("connector_live_call_attempted:", connector_result.live_call_attempted)
print("connector_live_call_completed:", connector_result.live_call_completed)

for name, passed in checks.items():
    print(f"{name}: {passed}")

if connector_result.generated_content:
    print("generated_content_preview:")
    print(connector_result.generated_content[:500])

if not readiness["provider_ready"]:
    print("NOTE: OPENAI_API_KEY is not configured, so this test correctly stops before any live call.")

if not gate.live_execution_allowed:
    print("NOTE: Live execution gate did not allow the call. Check OPENAI_API_KEY and ENABLE_LIVE_LLM_CALLS if you intend to run a live test.")

print("STEP_85_CONTROLLED_LIVE_LLM_ACTIVATION_TEST_COMPLETED")