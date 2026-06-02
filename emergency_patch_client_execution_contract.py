from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

target = 'implementation_plan: buildAutonomousImplementationPlan('

if target not in text:
    raise SystemExit("TARGET_NOT_FOUND")

insert = '''
                          requested_agent: selectedAgents[0] || "paid_ads_agent",
                          workflow_stage: "client_live_execution",
                          task:
                            taskValue ||
                            "Create premium client deliverable",
                          action_type: "creative_generation",
'''

text = text.replace(target, insert + '\n                          ' + target, 1)

p.write_text(text, encoding="utf-8")

print("CLIENT_EXECUTION_CONTRACT_DIRECT_PATCHED")