"""
Governed Live LLM Call

Prepared execution boundary for future live LLM calls.

This layer intentionally does not call external providers yet.
It enforces:
- owner-governed execution readiness
- live execution enablement gate
- no prompt/config exposure
- no credential exposure
- no autonomous high-risk actions
- client-safe output boundaries
- provider-specific connector routing
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from backend.app.core.safe_openai_live_connector import (
    SafeOpenAILiveConnector,
    SafeOpenAIConnectorRequest,
    safe_openai_connector_summary,
)

from backend.app.core.live_llm_execution_gate import (
    LiveLLMExecutionGate,
    LiveLLMExecutionGateRequest,
    live_llm_execution_gate_summary,
)


@dataclass
class GovernedLLMCallRequest:
    tenant_id: str
    agent_id: str
    task_type: str
    provider: str
    model_class: str
    region: str
    language: str
    payload: Dict[str, object]
    provider_ready: bool
    owner_live_execution_enabled: bool = False


@dataclass
class GovernedLLMCallResult:
    success: bool
    live_call_attempted: bool
    live_call_allowed: bool
    execution_mode: str
    generated_content: Optional[str]
    safe_client_message: str
    governance_checks: Dict[str, object]
    blocked_categories: List[str]
    provider_connector: Dict[str, object]
    live_execution_gate: Dict[str, object]


class GovernedLiveLLMCall:
    def __init__(self) -> None:
        self.openai_connector = SafeOpenAILiveConnector()
        self.live_execution_gate = LiveLLMExecutionGate()

    def execute(self, request: GovernedLLMCallRequest) -> GovernedLLMCallResult:
        governance_checks = {
            "provider_ready": request.provider_ready,
            "tenant_id_present": bool(request.tenant_id),
            "agent_id_present": bool(request.agent_id),
            "task_type_present": bool(request.task_type),
            "client_safe_boundary_enforced": True,
            "credential_exposure_blocked": True,
            "internal_prompt_exposure_blocked": True,
            "backend_config_exposure_blocked": True,
            "owner_approval_required_for_sensitive_actions": True,
        }

        gate_result = self.live_execution_gate.evaluate(
            LiveLLMExecutionGateRequest(
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                task_type=request.task_type,
                provider=request.provider,
                provider_ready=request.provider_ready,
                owner_live_execution_enabled=request.owner_live_execution_enabled,
            )
        )

        gate_summary = live_llm_execution_gate_summary(gate_result)
        live_call_allowed = bool(gate_result.live_execution_allowed)

        provider_connector = self._route_to_connector(request, live_call_allowed)

        return GovernedLLMCallResult(
            success=True,
            live_call_attempted=bool(provider_connector.get("live_call_attempted", False)),
            live_call_allowed=live_call_allowed,
            execution_mode=(
                provider_connector.get("execution_mode")
                or (
                    "governed_live_call_ready_not_executed"
                    if live_call_allowed
                    else "governed_live_call_blocked_until_ready"
                )
            ),
            generated_content=provider_connector.get("generated_content"),
            safe_client_message=str(
                provider_connector.get(
                    "safe_client_message",
                    gate_result.client_safe_message,
                )
            ),
            governance_checks=governance_checks,
            blocked_categories=[
                "provider_credentials",
                "internal_prompts",
                "system_messages",
                "learning_memory_internals",
                "governance_policy_internals",
                "backend_configuration",
                "tenant_security_rules",
            ],
            provider_connector=provider_connector,
            live_execution_gate=gate_summary,
        )

    def _route_to_connector(
        self,
        request: GovernedLLMCallRequest,
        live_call_allowed: bool,
    ) -> Dict[str, object]:
        normalised_provider = self._normalise_provider(request.provider)

        if normalised_provider == "openai":
            result = self.openai_connector.execute(
                SafeOpenAIConnectorRequest(
                    tenant_id=request.tenant_id,
                    agent_id=request.agent_id,
                    task_type=request.task_type,
                    model_class=request.model_class,
                    region=request.region,
                    language=request.language,
                    payload=request.payload,
                    provider_ready=request.provider_ready,
                    live_execution_allowed=live_call_allowed,
                )
            )
            return safe_openai_connector_summary(result)

        return {
            "success": True,
            "provider": normalised_provider,
            "live_call_attempted": False,
            "live_call_completed": False,
            "generated_content": None,
            "execution_mode": (
                f"{normalised_provider}_connector_pending"
                if live_call_allowed
                else f"{normalised_provider}_connector_blocked_until_ready"
            ),
            "safe_client_message": (
                f"{normalised_provider} connector is prepared but not implemented in this step."
            ),
            "metadata": {
                "credential_values_exposed": False,
                "internal_prompts_exposed": False,
                "backend_config_exposed": False,
                "client_safe": True,
            },
        }

    def _normalise_provider(self, provider: str) -> str:
        lowered = provider.lower()

        if "openai" in lowered:
            return "openai"

        if "claude" in lowered or "anthropic" in lowered:
            return "anthropic_claude"

        if "gemini" in lowered or "google" in lowered:
            return "google_gemini"

        if "grok" in lowered or "xai" in lowered:
            return "xai_grok"

        if "local" in lowered or "private" in lowered:
            return "local_or_private_model"

        return provider


def governed_live_llm_call_summary(result: GovernedLLMCallResult) -> Dict[str, object]:
    return {
        "success": result.success,
        "live_call_attempted": result.live_call_attempted,
        "live_call_allowed": result.live_call_allowed,
        "execution_mode": result.execution_mode,
        "generated_content": result.generated_content,
        "safe_client_message": result.safe_client_message,
        "governance_checks": result.governance_checks,
        "blocked_categories": result.blocked_categories,
        "provider_connector": result.provider_connector,
        "live_execution_gate": result.live_execution_gate,
    }
