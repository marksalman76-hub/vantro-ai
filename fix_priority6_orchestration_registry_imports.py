from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
ORCH = ROOT / "backend" / "app" / "core" / "multi_agent_orchestration_runtime.py"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if not ORCH.exists():
    raise FileNotFoundError(f"Missing orchestration runtime: {ORCH}")

text = ORCH.read_text(encoding="utf-8")
backup = BACKUPS / f"multi_agent_orchestration_runtime_before_registry_import_fix_{timestamp}.py"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    "from backend.app.agents.agent_registry import AGENT_REGISTRY, agent_exists, normalize_agent_id",
    "from backend.app.agents.agent_registry import AGENT_CATALOGUE, agent_exists, normalize_agent_id, get_agent_role, get_agent_display_name",
)

text = text.replace(
    "    agent = AGENT_REGISTRY.get(agent_id, {})\n    return str(agent.get(\"role\") or \"\")",
    "    return str(get_agent_role(agent_id) or \"\")",
)

text = text.replace(
    "    agent = AGENT_REGISTRY.get(agent_id, {})\n    return str(agent.get(\"name\") or agent_id)",
    "    return str(get_agent_display_name(agent_id) or agent_id)",
)

text = text.replace(
    "    total_agents = len(AGENT_REGISTRY)",
    "    total_agents = len(AGENT_CATALOGUE)",
)

ORCH.write_text(text, encoding="utf-8")

print("PRIORITY6_ORCHESTRATION_REGISTRY_IMPORTS_FIXED")
print(f"Backup: {backup}")