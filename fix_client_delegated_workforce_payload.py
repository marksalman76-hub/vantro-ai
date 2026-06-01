from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
CLIENT = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP = ROOT / "backups" / f"client_delegated_workforce_payload_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(CLIENT, BACKUP / "page.tsx")

text = CLIENT.read_text(encoding="utf-8")

old = '''body: JSON.stringify({
                          selected_agents: selectedAgents,
                          task: "Create a client-specific client deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements.",
                          business_profile: {
                            niche: businessProfile.business_niche || "Saved client business profile",
                            target_audience: businessProfile.target_audience || "Saved target audience and customer context",
                            positioning: businessProfile.notes || "Client-specific commercial positioning and execution requirements",
                          },
                        }),'''

new = '''body: JSON.stringify({
                          implementation_plan: buildAutonomousImplementationPlan(
                            buildStrictTaskExecutionContract(
                              `Create a client-specific deliverable using the saved business profile. Business niche: ${businessProfile.business_niche || "saved business profile"}. Target audience: ${businessProfile.target_audience || "saved target audience"}. Positioning: ${businessProfile.notes || "client-specific positioning"}. Fulfil the selected agent task only and provide completion evidence.`,
                              selectedAgents[0] || "marketing_specialist_agent"
                            ),
                            selectedAgents[0] || "marketing_specialist_agent"
                          ),
                          owner_approved: false,
                          client_owned_agents: selectedAgents,
                          package_tier: packageTier || "starter",
                          connected_integrations: ["email", "crm", "calendar"],
                          tenant_id: tenantId || "client_demo_001",
                        }),'''

if old not in text:
    raise SystemExit("Could not find old client delegated workforce payload.")

text = text.replace(old, new)

CLIENT.write_text(text, encoding="utf-8")

print("CLIENT_DELEGATED_WORKFORCE_PAYLOAD_FIXED")
print("Backup:", BACKUP)
print("Updated:", CLIENT)