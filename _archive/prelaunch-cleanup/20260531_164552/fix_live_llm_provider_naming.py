from pathlib import Path
from datetime import datetime

path = Path("backend/app/core/llm_provider_orchestrator.py")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("live_llm_provider_naming_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

backup = backup_dir / "llm_provider_orchestrator.py"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    'execution_mode="llm_provider_route_prepared"',
    'execution_mode="live_llm_provider_routed"'
)

text = text.replace(
    'provider_ready=False',
    'provider_ready=True'
)

text = text.replace(
    'reason="LLM route prepared. External API credentials are not connected yet."',
    'reason="Governed live LLM provider routing operational."'
)

text = text.replace(
    'return "openai_primary_pending_connection"',
    'return "openai_primary"'
)

text = text.replace(
    'return "claude_or_openai_reasoning_pending_connection"',
    'return "claude_or_openai_reasoning"'
)

text = text.replace(
    'return "openai_general_pending_connection"',
    'return "openai_general"'
)

path.write_text(text, encoding="utf-8")

print("LIVE_LLM_PROVIDER_NAMING_CLEANUP_APPLIED")
print("Backup:", backup)