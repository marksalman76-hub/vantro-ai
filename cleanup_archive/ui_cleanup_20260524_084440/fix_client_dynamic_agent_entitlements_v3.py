from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_dynamic_agent_entitlements_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old_agents = '''const AGENTS = [
  "Product Copywriting Agent",
  "UGC Creative Agent",
  "Product Image Agent",
  "Influencer Collaboration Agent",
  "Analytics Optimisation Agent",
  "General Ecommerce Agent",
  "Competitor Intelligence Agent",
];
'''

if old_agents in text:
    text = text.replace(old_agents, "const DEFAULT_AGENTS: string[] = [];\n", 1)

old_state = '''  const [selectedAgents, setSelectedAgents] = useState<string[]>([
    "Product Copywriting Agent",
  ]);
'''

if old_state in text:
    text = text.replace(old_state, "  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);\n", 1)

old_fetch = '''      .then((data) => setAccount(data?.account || data))
'''

new_fetch = '''      .then((data) => {
        const accountData = data?.account || data;
        setAccount(accountData);

        const deployedAgents =
          accountData?.active_agents && Array.isArray(accountData.active_agents)
            ? accountData.active_agents
            : [];

        if (deployedAgents.length > 0) {
          setSelectedAgents(deployedAgents);
        }
      })
'''

if old_fetch in text:
    text = text.replace(old_fetch, new_fetch, 1)

path.write_text(text, encoding="utf-8")

print("CLIENT_DYNAMIC_AGENT_ENTITLEMENTS_V3_FIXED")
print(f"Backup: {backup}")