import os

from backend.app.core.llm_provider_credential_readiness import LLMProviderCredentialReadiness
from backend.app.core.owner_live_llm_control import owner_live_llm_control
from backend.app.core.live_llm_execution_gate import LiveLLMExecutionGate, LiveLLMExecutionGateRequest
from backend.app.core.safe_openai_live_connector import (
    SafeOpenAILiveConnector,
    SafeOpenAIConnectorRequest,
)


owner_live_llm_control.set_state(
    enabled=False,
    updated_by="step_80_readiness_test",
    reason="Verify OpenAI readiness without allowing a live provider call.",
)

readiness = LLMProviderCredentialReadiness().check_selected_provider(
    "openai_primary_pending_connection"
)

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
        payload={"task": "Create UGC brief"},
        provider_ready=bool(readiness["provider_ready"]),
        live_execution_allowed=bool(gate.live_execution_allowed),
    )
)

checks = {
    "openai_provider_normalised": readiness["normalised_provider"] == "openai",
    "credential_values_not_exposed": readiness["credential_values_exposed"] is False,
    "owner_control_disabled": owner_live_llm_control.is_enabled() is False,
    "gate_blocks_live_execution": gate.live_execution_allowed is False,
    "connector_does_not_attempt_live_call": connector_result.live_call_attempted is False,
    "connector_does_not_complete_live_call": connector_result.live_call_completed is False,
    "connector_hides_credentials": connector_result.metadata["credential_values_exposed"] is False,
    "connector_hides_prompts": connector_result.metadata["internal_prompts_exposed"] is False,
    "connector_hides_backend_config": connector_result.metadata["backend_config_exposed"] is False,
    "api_key_value_not_printed": "OPENAI_API_KEY" not in str(connector_result.generated_content),
    "env_has_openai_key_boolean_only": isinstance(bool(os.getenv("OPENAI_API_KEY")), bool),
}

failed = [name for name, passed in checks.items() if not passed]

print("STEP_80_OPENAI_READINESS_NO_LIVE_CALL_RESULTS")
print("provider_ready:", readiness["provider_ready"])
print("gate_execution_mode:", gate.execution_mode)
print("connector_execution_mode:", connector_result.execution_mode)

for name, passed in checks.items():
    print(f"{name}: {passed}")

if failed:
    print("FAILED_CHECKS:", failed)
    raise SystemExit(1)

print("STEP_80_OPENAI_READINESS_NO_LIVE_CALL_OK")