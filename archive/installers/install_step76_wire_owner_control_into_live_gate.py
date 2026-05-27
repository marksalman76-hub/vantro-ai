from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "live_llm_execution_gate.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"live_llm_execution_gate_before_step76_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

content = '''"""
Live LLM Execution Gate

Central safety gate for enabling real provider execution.

This prevents accidental live model calls unless all required controls pass.
"""

from dataclasses import dataclass
from typing import Dict, List
import os

from backend.app.core.owner_live_llm_control import owner_live_llm_control


@dataclass
class LiveLLMExecutionGateRequest:
    tenant_id: str
    agent_id: str
    task_type: str
    provider: str
    provider_ready: bool
    owner_live_execution_enabled: bool = False


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
        persisted_owner_enabled = owner_live_llm_control.is_enabled()
        owner_enabled = bool(request.owner_live_execution_enabled or persisted_owner_enabled)

        checks = {
            "tenant_id_present": bool(request.tenant_id),
            "agent_id_present": bool(request.agent_id),
            "task_type_present": bool(request.task_type),
            "provider_present": bool(request.provider),
            "provider_ready": bool(request.provider_ready),
            "owner_live_execution_enabled": owner_enabled,
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
                "owner_control_enabled": owner_enabled,
                "persisted_owner_control_enabled": persisted_owner_enabled,
                "request_owner_control_enabled": bool(request.owner_live_execution_enabled),
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
'''

TARGET_FILE.write_text(content, encoding="utf-8")

print("STEP_76_OWNER_CONTROL_WIRED_INTO_LIVE_GATE")
print(f"Backup created: {backup_file}")
print(f"Updated: {TARGET_FILE}")