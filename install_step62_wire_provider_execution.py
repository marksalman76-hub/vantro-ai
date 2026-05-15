from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "ai_generation_service.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"ai_generation_service_before_step62_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

updated = original

import_block = """from backend.app.core.llm_provider_execution_adapter import (
    LLMProviderExecutionAdapter,
    LLMProviderExecutionRequest,
    provider_execution_summary,
)
"""

if "llm_provider_execution_adapter" not in updated:
    updated = updated.replace(
        "from backend.app.core.llm_provider_orchestrator import (\n"
        "    LLMProviderOrchestrator,\n"
        "    LLMRouteRequest,\n"
        "    llm_route_summary,\n"
        ")\n",
        "from backend.app.core.llm_provider_orchestrator import (\n"
        "    LLMProviderOrchestrator,\n"
        "    LLMRouteRequest,\n"
        "    llm_route_summary,\n"
        ")\n\n"
        + import_block,
    )

if "self.provider_execution_adapter = LLMProviderExecutionAdapter()" not in updated:
    updated = updated.replace(
        "        self.llm_orchestrator = LLMProviderOrchestrator()\n",
        "        self.llm_orchestrator = LLMProviderOrchestrator()\n"
        "        self.provider_execution_adapter = LLMProviderExecutionAdapter()\n",
    )

old_block = '''        result["provider_execution"] = {
            "provider_selected": route_result.selected_provider,
            "model_class": route_result.selected_model_class,
            "provider_ready": route_result.provider_ready,
            "execution_mode": route_result.execution_mode,
            "future_provider_execution_supported": True,
            "future_multi_provider_failover_supported": True,
            "future_local_model_support": True,
            "future_governed_learning_support": True,
        }
'''

new_block = '''        provider_execution_result = self.provider_execution_adapter.execute(
            LLMProviderExecutionRequest(
                tenant_id=request.tenant_id,
                agent_id=request.requested_agent,
                task_type=result.get("output_type", self._resolve_task_type(request)),
                selected_provider=route_result.selected_provider,
                selected_model_class=route_result.selected_model_class,
                region=request.region,
                language=request.language,
                payload={
                    "task": request.task,
                    "workflow_stage": request.workflow_stage,
                    "generated_output_type": result.get("output_type"),
                    "client_safe": result.get("client_safe", True),
                },
            )
        )

        result["provider_execution"] = provider_execution_summary(provider_execution_result)
'''

if old_block not in updated:
    raise SystemExit("Expected provider_execution block not found. Stop and send me the current ai_generation_service.py file.")

updated = updated.replace(old_block, new_block)

TARGET_FILE.write_text(updated, encoding="utf-8")

print("STEP_62_PROVIDER_EXECUTION_WIRED_INTO_AI_GENERATION_SERVICE")
print(f"Backup created: {backup_file}")
print(f"Updated: {TARGET_FILE}")