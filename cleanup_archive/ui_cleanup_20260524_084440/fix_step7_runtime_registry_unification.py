from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
main_path = root / "backend" / "app" / "main.py"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = backup_dir / f"main_before_step7_runtime_registry_unification_{timestamp}.py"

text = main_path.read_text(encoding="utf-8")
backup_path.write_text(text, encoding="utf-8")

text = text.replace(
    "from backend.app.agents.agent_registry import agent_exists",
    "from backend.app.agents.agent_registry import agent_exists, normalize_agent_id",
)

start = text.find("AGENT_ALIAS_MAP: Dict[str, str] = {")
if start != -1:
    end = text.find("\nACTION_TO_EXECUTION_MAP:", start)
    if end == -1:
        raise RuntimeError("Could not find ACTION_TO_EXECUTION_MAP after AGENT_ALIAS_MAP.")
    text = text[:start] + text[end + 1:]

text = text.replace(
    "requested_agent = AGENT_ALIAS_MAP.get(request.requested_agent, request.requested_agent)",
    "requested_agent = normalize_agent_id(request.requested_agent)",
)

text = text.replace(
    "normalised_active_agents = [\n            AGENT_ALIAS_MAP.get(agent, agent) for agent in active_agents\n        ]",
    "normalised_active_agents = [\n            normalize_agent_id(agent) for agent in active_agents\n        ]",
)

if "AGENT_ALIAS_MAP" in text:
    raise RuntimeError("AGENT_ALIAS_MAP still exists in main.py")

if "normalize_agent_id" not in text:
    raise RuntimeError("normalize_agent_id was not added to main.py")

main_path.write_text(text, encoding="utf-8")

print("STEP_7_RUNTIME_REGISTRY_UNIFICATION_FIXED")
print(f"Backup: {backup_path}")