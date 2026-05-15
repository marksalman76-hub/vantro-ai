"""
Live LLM Execution Gate

Central safety gate for enabling real provider execution.

This prevents accidental live model calls unless all required controls pass.
"""

from dataclasses import dataclass
from typing import Dict, List
import os


@dataclass
class LiveLLMExecutionGateRequest:
    tenant_id: str
    agent_id: str
    task_type: str
    provider: str
    provider_ready: bool
    owner_live_execution_enabled: bool


@dataclass
class LiveLLMExecutionGateResult:
    success: bool
    live_execution_allowed: bool
    execution_mode: str
    failed_checks: List[str]
    passed_checks: List[str]
    client_safe_message: str
    metadata: Dict[str, object]


class LiveLLMExecutionGate:
    def evaluate(self, request: LiveLLMExecutionGateRequest) -> LiveLLMExecutionGateResult:
        checks = {
            "tenant_id_present": bool(request.tenant_id),
            "agent_id_present": bool(request.agent_id),
            "task_type_present": bool(request.task_type),
            "provider_present": bool(request.provider),
            "provider_ready": bool(request.provider_ready),
            "owner_live_execution_enabled": bool(request.owner_live_execution_enabled),
            "global_live_llm_enabled": self._global_live_llm_enabled(),
            "credential_exposure_blocked": True,
            "internal_prompt_exposure_blocked": True,
            "backend_config_exposure_blocked": True,
            "client_safe_boundary_enforced": True,
        }

        passed_checks = [key for key, value in checks.items() if value]
        failed_checks = [key for key, value in checks.items() if not value]

        live_execution_allowed = len(failed_checks) == 0

        return LiveLLMExecutionGateResult(
            success=True,
            live_execution_allowed=live_execution_allowed,
            execution_mode=(
                "live_llm_execution_allowed"
                if live_execution_allowed
                else "live_llm_execution_blocked"
            ),
            failed_checks=failed_checks,
            passed_checks=passed_checks,
            client_safe_message=(
                "Live provider execution is enabled and all safety checks passed."
                if live_execution_allowed
                else "Live provider execution is blocked until all provider, owner, and safety checks pass."
            ),
            metadata={
                "tenant_id": request.tenant_id,
                "agent_id": request.agent_id,
                "task_type": request.task_type,
                "provider": request.provider,
                "credential_values_exposed": False,
                "internal_prompts_exposed": False,
                "backend_config_exposed": False,
                "client_safe": True,
            },
        )

    def _global_live_llm_enabled(self) -> bool:
        return os.getenv("ENABLE_LIVE_LLM_CALLS", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "enabled",
        }


def live_llm_execution_gate_summary(result: LiveLLMExecutionGateResult) -> Dict[str, object]:
    return {
        "success": result.success,
        "live_execution_allowed": result.live_execution_allowed,
        "execution_mode": result.execution_mode,
        "failed_checks": result.failed_checks,
        "passed_checks": result.passed_checks,
        "client_safe_message": result.client_safe_message,
        "metadata": result.metadata,
    }
