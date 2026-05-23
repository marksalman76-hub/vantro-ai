from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/admin/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"admin_page_before_deployment_agent_helpers_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old = "setSelectedDeploymentAgents(ADMIN_AGENT_OPTIONS.map((agent) => agent.id));"
new = "setSelectedDeploymentAgents(ADMIN_AGENT_OPTIONS.map(([agentId]) => agentId));"

if old not in text:
    raise RuntimeError("Could not find incorrect agent.id mapping.")

text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

print("ADMIN_DEPLOYMENT_AGENT_HELPERS_V3_FIXED")
print(f"Backup: {backup}")