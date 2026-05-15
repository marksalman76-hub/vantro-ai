"""
LLM Provider Execution Adapter

Governed adapter layer for future live LLM provider execution.

This file does not expose prompts, internal configuration, learning rules,
provider credentials, backend architecture, or security logic to clients.

Current mode:
- route-only execution preparation
- no external API calls yet
- provider credentials intentionally not required yet
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


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
    def execute(self, request: LLMProviderExecutionRequest) -> LLMProviderExecutionResult:
        return LLMProviderExecutionResult(
            success=True,
            execution_mode="provider_execution_prepared_no_external_call",
            provider=request.selected_provider,
            model_class=request.selected_model_class,
            provider_ready=False,
            generated_content=None,
            safe_client_message=(
                "Premium AI generation route prepared. Live provider execution is ready "
                "to be connected once approved provider credentials are configured."
            ),
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
        "safe_client_message": result.safe_client_message,
        "blocked_exposure_categories": result.blocked_exposure_categories,
        "governance_limits": result.governance_limits,
        "metadata": result.metadata,
    }
