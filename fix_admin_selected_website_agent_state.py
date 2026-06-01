from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"

BACKUP = ROOT / "backups" / f"admin_selected_website_agent_state_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "page.tsx")

s = TARGET.read_text(encoding="utf-8")

s = s.replace(
    'const [selectedAgents, setSelectedAgents] = useState<string[]>(["marketing_specialist_agent"]);',
    'const [selectedAgents, setSelectedAgents] = useState<string[]>(["website_landing_apps_agent"]);'
)

s = s.replace(
    'const [agent, setAgent] = useState<string>("marketing_specialist_agent");',
    'const [agent, setAgent] = useState<string>("website_landing_apps_agent");'
)

TARGET.write_text(s, encoding="utf-8")

print("ADMIN_SELECTED_WEBSITE_AGENT_STATE_FIXED")
print("Backup:", BACKUP)