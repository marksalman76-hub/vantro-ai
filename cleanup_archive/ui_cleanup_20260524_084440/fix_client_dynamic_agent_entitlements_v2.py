from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_dynamic_agent_entitlements_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    "{AGENTS.map((agent) => {",
    "{(account?.active_agents || DEFAULT_AGENTS).map((agent) => {",
    1,
)

path.write_text(text, encoding="utf-8")

print("CLIENT_DYNAMIC_AGENT_ENTITLEMENTS_V2_FIXED")
print(f"Backup: {backup}")