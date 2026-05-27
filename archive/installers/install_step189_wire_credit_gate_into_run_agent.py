from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"

text = MAIN.read_text(encoding="utf-8")

if "client_credit_gate as pg_client_credit_gate" not in text:
    text = text.replace(
        "    lookup_client_account as pg_lookup_client_account,\n)",
        "    lookup_client_account as pg_lookup_client_account,\n"
        "    client_credit_gate as pg_client_credit_gate,\n)",
    )

text = text.replace(
    '''class RunAgentRequest(BaseModel):
    tenant_id: str
    requested_agent: str
    workflow_stage: str
    task: str
    action_type: str
    region: str = "Global"
    language: str = "English"
    currency: str = "USD"
    owner_approved: bool = False
    execute_real_world_action: bool = True
    project_id: str = "default_project"''',
    '''class RunAgentRequest(BaseModel):
    tenant_id: str
    requested_agent: str
    workflow_stage: str
    task: str
    action_type: str
    region: str = "Global"
    language: str = "English"
    currency: str = "USD"
    owner_approved: bool = False
    execute_real_world_action: bool = True
    project_id: str = "default_project"
    actor_role: str = "client"
    requested_credits: int = 1''',
)

gate = '''    credit_gate = pg_client_credit_gate({
        "actor_role": request.actor_role,
        "tenant_id": request.tenant_id,
        "requested_credits": request.requested_credits,
    })

    if not credit_gate.get("credit_gate_passed"):
        return {
            "success": False,
            "status": "credit_gate_blocked",
            "message": "Client execution is blocked until credit top-up or next billing cycle.",
            "credit_gate": credit_gate,
        }

'''

anchor = '''    if request.tenant_id not in DEMO_TENANTS:
        return {
            "success": False,
            "error": "tenant_not_found_or_not_active",
            "tenant_id": request.tenant_id,
        }
'''

if "status\": \"credit_gate_blocked\"" not in text:
    text = text.replace(anchor, gate + anchor)

MAIN.write_text(text, encoding="utf-8")

print("STEP_189_CREDIT_GATE_WIRED_INTO_RUN_AGENT")
print("STEP_189_OK")