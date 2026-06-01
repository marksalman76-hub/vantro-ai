from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
ADMIN = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"

BACKUP = ROOT / "backups" / f"wire_website_agent_react_runtime_admin_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(ADMIN, BACKUP / "page.tsx")

s = ADMIN.read_text(encoding="utf-8")

# Make admin website runs include the internal task store connector so the route executes instead of review/pending.
s = s.replace(
    "connected_integrations: uniqueValues(selectedAgents.flatMap(integrationsForAutonomousAgent)),",
    'connected_integrations: uniqueValues([...selectedAgents.flatMap(integrationsForAutonomousAgent), "task_store"]),'
)

# Make admin website runs owner-admin approved by default.
s = s.replace(
    "owner_approved: false,",
    "owner_approved: true,"
)

# Upgrade default admin website task wording if present.
s = s.replace(
    "Create a premium ecommerce launch campaign deliverable for a luxury skincare brand targeting women aged 30–50 in Australia.",
    "Create a custom premium React/Next.js landing page for a luxury Australian skincare brand targeting women aged 30–50. Use advanced glassmorphism, 3D motion visuals, premium animation, cinematic layout, proof sections, offer section, FAQ, sticky CTA, and generate a real previewable React route. Do not return generic copy. Generate the website project."
)

ADMIN.write_text(s, encoding="utf-8")

print("WEBSITE_AGENT_REACT_RUNTIME_WIRED_TO_ADMIN")
print("Backup:", BACKUP)
print("Updated:", ADMIN)