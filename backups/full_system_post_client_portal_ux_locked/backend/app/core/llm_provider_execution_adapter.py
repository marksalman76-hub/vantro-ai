"""
LLM Provider Execution Adapter

Governed adapter layer for future live LLM provider execution.

Current mode:
- route-only execution preparation
- live readiness check included
- governed live call boundary included
- provider execution audit logging included
- no external API calls yet
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from backend.app.core.llm_provider_credential_readiness import (
    LLMProviderCredentialReadiness,
)

from backend.app.core.governed_live_llm_call import (
    GovernedLiveLLMCall,
    GovernedLLMCallRequest,
    governed_live_llm_call_summary,
)

from backend.app.core.provider_execution_audit_log import provider_execution_audit_log


@dataclass
class LLMProviderExecutionRequest:
    tenant_id: str
    agent_id: str
    task_type: str
    selected_provider: str
    selected_model_class: str
    region: str
    language: str
    payload: Dict[str, object]


@dataclass
class LLMProviderExecutionResult:
    success: bool
    execution_mode: str
    provider: str
    model_class: str
    provider_ready: bool
    generated_content: Optional[str]
    safe_client_message: str
    blocked_exposure_categories: List[str]
    governance_limits: List[str]
    metadata: Dict[str, object]


class LLMProviderExecutionAdapter:
    def __init__(self) -> None:
        self.credential_readiness = LLMProviderCredentialReadiness()
        self.governed_live_call = GovernedLiveLLMCall()

    def execute(self, request: LLMProviderExecutionRequest) -> LLMProviderExecutionResult:
        readiness = self.credential_readiness.check_selected_provider(request.selected_provider)
        provider_ready = bool(readiness.get("provider_ready"))

        governed_result = self.governed_live_call.execute(
            GovernedLLMCallRequest(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                task_type=request.task_type,
                provider=request.selected_provider,
                model_class=request.selected_model_class,
                region=request.region,
                language=request.language,
                payload=request.payload,
                provider_ready=provider_ready,
            )
        )

        governed_summary = governed_live_llm_call_summary(governed_result)

        audit_result = provider_execution_audit_log.record(
            {
                "event_type": "provider_execution_decision",
                "tenant_id": request.tenant_id,
                "agent_id": request.agent_id,
                "task_type": request.task_type,
                "provider": request.selected_provider,
                "model_class": request.selected_model_class,
                "normalised_provider": readiness.get("normalised_provider"),
                "provider_ready": provider_ready,
                "execution_mode": governed_result.execution_mode,
                "live_execution_allowed": governed_result.live_call_allowed,
                "live_call_attempted": governed_result.live_call_attempted,
                "credential_values_exposed": readiness.get("credential_values_exposed", False),
                "client_safe": True,
            }
        )

        return LLMProviderExecutionResult(
            success=True,
            execution_mode=governed_result.execution_mode,
            provider=request.selected_provider,
            model_class=request.selected_model_class,
            provider_ready=provider_ready,
            generated_content=governed_result.generated_content,
            safe_client_message=governed_result.safe_client_message,
            blocked_exposure_categories=[
                "internal_prompts",
                "behaviour_rules",
                "learning_architecture",
                "backend_configuration",
                "provider_credentials",
                "security_controls",
                "tenant_memory_logic",
                "governance_policy_logic",
            ],
            governance_limits=[
                "No client access to internal prompts.",
                "No client access to backend learning configuration.",
                "No client access to provider credentials.",
                "No autonomous spend changes.",
                "No autonomous campaign scaling.",
                "No autonomous contract approval.",
                "Owner approval remains required for authority-sensitive actions.",
            ],
            metadata={
                "tenant_id": request.tenant_id,
                "agent_id": request.agent_id,
                "task_type": request.task_type,
                "region": request.region,
                "language": request.language,
                "normalised_provider": readiness.get("normalised_provider"),
                "credential_values_exposed": readiness.get("credential_values_exposed", False),
                "live_execution_allowed": governed_result.live_call_allowed,
                "live_call_attempted": governed_result.live_call_attempted,
                "credential_safe_status": readiness.get("safe_status"),
                "governed_live_call": governed_summary,
                "provider_execution_audit": audit_result,
                "future_live_provider_call_supported": True,
                "future_failover_supported": True,
                "future_private_model_supported": True,
                "client_safe": True,
            },
        )


def provider_execution_summary(result: LLMProviderExecutionResult) -> Dict[str, object]:
    return {
        "success": result.success,
        "execution_mode": result.execution_mode,
        "provider": result.provider,
        "model_class": result.model_class,
        "provider_ready": result.provider_ready,
        "generated_content": result.generated_content,
        "safe_client_message": result.safe_client_message,
        "blocked_exposure_categories": result.blocked_exposure_categories,
        "governance_limits": result.governance_limits,
        "metadata": result.metadata,
    }
