from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/admin/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"admin_page_before_deployment_agent_helper_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

if "function selectAllDeploymentAgents()" in text or "function clearDeploymentAgents()" in text:
    print("HELPERS_ALREADY_PRESENT")
    print(f"Backup: {backup}")
    raise SystemExit(0)

anchor = """  function toggleAdminAgent(agentId: string) {
    setSelectedAdminAgents((current) =>
      current.includes(agentId)
        ? current.filter((item) => item !== agentId)
        : [...current, agentId]
    );
  }
"""

insert = anchor + """

  function selectAllDeploymentAgents() {
    setSelectedDeploymentAgents(ADMIN_AGENT_OPTIONS.map((agent) => agent.id));
  }

  function clearDeploymentAgents() {
    setSelectedDeploymentAgents([]);
  }
"""

if anchor not in text:
    raise RuntimeError("Could not find toggleAdminAgent anchor.")

text = text.replace(anchor, insert, 1)
path.write_text(text, encoding="utf-8")

print("ADMIN_DEPLOYMENT_AGENT_HELPERS_FIXED")
print(f"Backup: {backup}")