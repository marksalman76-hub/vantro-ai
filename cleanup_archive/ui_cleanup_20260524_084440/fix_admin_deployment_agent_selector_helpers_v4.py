from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/admin/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"admin_page_before_deployment_agent_helpers_v4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

if "function toggleDeploymentAgent(" not in text:
    marker = "  function selectAllDeploymentAgents()"
    helper = """  function toggleDeploymentAgent(agentId: string) {
    setSelectedDeploymentAgents((current) =>
      current.includes(agentId)
        ? current.filter((item) => item !== agentId)
        : [...current, agentId]
    );
  }

"""
    if marker not in text:
        raise RuntimeError("Could not find selectAllDeploymentAgents marker.")

    text = text.replace(marker, helper + marker, 1)

path.write_text(text, encoding="utf-8")

print("ADMIN_DEPLOYMENT_AGENT_HELPERS_V4_FIXED")
print(f"Backup: {backup}")