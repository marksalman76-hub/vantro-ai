from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("backend/app/agents/agent_registry.py")
content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup_file = backup_dir / f"agent_registry_before_operations_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(TARGET, backup_file)

if '"operations_manager_agent"' not in content:
    marker = '''    "influencer_collaboration_agent": {
        "name": "Influencer Collaboration Agent",
        "category": "collaboration",
        "visibility": "purchasable",
        "role": "Identifies creator-fit opportunities, prepares outreach, follow-ups, collaboration briefs, and influencer campaign tracking support.",
    },
'''

    insert = marker + '''    "operations_manager_agent": {
        "name": "Operations Manager Agent",
        "category": "operations",
        "visibility": "purchasable",
        "role": "Coordinates operational workflows, process improvements, task planning, execution readiness, team handoffs, and day-to-day business efficiency recommendations.",
    },
'''

    if marker not in content:
        raise RuntimeError("Could not find insertion marker.")

    content = content.replace(marker, insert)

TARGET.write_text(content, encoding="utf-8")

print("OPERATIONS_MANAGER_AGENT_REGISTERED")
print("Backup:", backup_file)