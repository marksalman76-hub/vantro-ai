from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/admin/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"admin_page_before_deployment_agent_helpers_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

if "function selectAllDeploymentAgents()" not in text:
    marker = "  async function runAdminAgent()"
    helpers = """  function selectAllDeploymentAgents() {
    setSelectedDeploymentAgents(ADMIN_AGENT_OPTIONS.map((agent) => agent.id));
  }

  function clearDeploymentAgents() {
    setSelectedDeploymentAgents([]);
  }

"""
    if marker not in text:
        raise RuntimeError("Could not find runAdminAgent marker.")

    text = text.replace(marker, helpers + marker, 1)

path.write_text(text, encoding="utf-8")

print("ADMIN_DEPLOYMENT_AGENT_HELPERS_V2_FIXED")
print(f"Backup: {backup}")