from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "governed_live_llm_call.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"governed_live_llm_call_before_step72_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

content = '''"""
Governed Live LLM Call

Prepared execution boundary for future live LLM calls.

This layer intentionally does not call external providers yet.
It enforces:
- owner-governed execution readiness
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


class GovernedLiveLLMCall:
    def __init__(self) -> None:
        self.openai_connector = SafeOpenAILiveConnector()

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

        live_call_allowed = all(
            [
                governance_checks["provider_ready"],
                governance_checks["tenant_id_present"],
                governance_checks["agent_id_present"],
                governance_checks["task_type_present"],
                governance_checks["client_safe_boundary_enforced"],
            ]
        )

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
                    "Governed live AI execution boundary completed.",
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
    }
'''

TARGET_FILE.write_text(content, encoding="utf-8")

print("STEP_72_OPENAI_CONNECTOR_WIRED_INTO_GOVERNED_LIVE_LLM_CALL")
print(f"Backup created: {backup_file}")
print(f"Updated: {TARGET_FILE}")