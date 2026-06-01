from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
ADMIN = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"
CLIENT = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP = ROOT / "backups" / f"task_execution_contract_layer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

for p in [ADMIN, CLIENT]:
    shutil.copy2(p, BACKUP / p.name)

admin = ADMIN.read_text(encoding="utf-8")
client = CLIENT.read_text(encoding="utf-8")

contract = r'''
function buildStrictTaskExecutionContract(task: string, agentName?: string): string {
  return `${task}

STRICT TASK EXECUTION CONTRACT:
You are acting as a task executor, not a consultant.
Fulfil the user's exact requested task only.
Do not expand the task into a campaign, strategy, report, audit, plan, or multi-channel bundle unless the user explicitly asks for that.

OUTPUT REQUIREMENTS:
- Return only the finished deliverable.
- Do not include executive summary, assumptions, diagnosis, execution plan, KPIs, risks, admin review points, next steps, metadata, JSON, or internal reasoning.
- If the user asks for a product description, return only: Headline, Description, Call-to-action.
- If the user asks for an email, return only: Subject and Email body.
- If the user asks for ad copy, return only the requested ad copy variations.
- If the user asks for social captions, return only captions.
- If the task requires a real external action and the integration is not connected or approval is required, clearly state the exact blocker and the required next action.
- Do not invent completed external actions.

QUALITY BAR:
Make the deliverable commercially usable, specific, premium, concise, and ready to copy into the relevant business tool.`;
}
'''

if "function buildStrictTaskExecutionContract" not in admin:
    admin = admin.replace("export default function AdminLiveExecutionPage()", contract + "\nexport default function AdminLiveExecutionPage()")

admin = admin.replace(
    "task: buildPortalDeliverableTask(task)",
    "task: buildStrictTaskExecutionContract(task, agentName(agent))"
)

if "function buildStrictTaskExecutionContract" not in client:
    idx = client.find("export default function")
    if idx == -1:
        raise SystemExit("Could not find client export default function.")
    client = client[:idx] + contract + "\n" + client[idx:]

client = re.sub(
    r'''body:\s*JSON\.stringify\(\{\s*requested_agent:\s*selectedAgent[^}]*task:\s*taskInput[^}]*\}\)''',
    '''body: JSON.stringify({
                          requested_agent: selectedAgent,
                          task: buildStrictTaskExecutionContract(taskInput, selectedAgent),
                        })''',
    client,
    count=1,
    flags=re.S,
)

client = re.sub(
    r'''body:\s*JSON\.stringify\(\{\s*requested_agent:\s*activeAgent[^}]*task:\s*[^}]+?\}\)''',
    lambda m: m.group(0).replace("task:", "task: buildStrictTaskExecutionContract(").replace("\n                        })", ", activeAgent)\n                        })"),
    client,
    count=1,
    flags=re.S,
)

ADMIN.write_text(admin, encoding="utf-8")
CLIENT.write_text(client, encoding="utf-8")

print("TASK_EXECUTION_CONTRACT_LAYER_INSTALLED")
print("Backup:", BACKUP)
print("Updated:", ADMIN)
print("Updated:", CLIENT)