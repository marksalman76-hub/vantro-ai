from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
runtime_path = ROOT / "backend" / "app" / "core" / "client_integrations_runtime.py"

for path in [main_path, runtime_path]:
    backup = BACKUPS / f"{path.stem}_before_step_i_brevo_email_proof_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}"
    backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

runtime = runtime_path.read_text(encoding="utf-8", errors="ignore")

if "def get_client_integration_secret" not in runtime:
    runtime += r'''

def get_client_integration_secret(tenant_id: str, integration_key: str) -> Dict[str, Any]:
    data = _load()
    connection = data.get("tenants", {}).get(tenant_id, {}).get("connections", {}).get(integration_key)
    if not connection or not connection.get("connected"):
        return {"success": False, "error": "integration_not_connected"}

    # Current prototype stores proof-test state only. Production must use encrypted vault storage.
    return {
        "success": True,
        "integration_key": integration_key,
        "provider": connection.get("provider"),
        "status": connection.get("status"),
        "credential_hint": connection.get("credential_hint"),
    }


def log_email_proof_send(tenant_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _load()
    data.setdefault("audit", []).append({
        "event": "email_proof_send",
        "tenant_id": tenant_id,
        **payload,
        "created_at": _now(),
    })
    _save(data)
    return {"success": True}
'''
runtime_path.write_text(runtime, encoding="utf-8")

main = main_path.read_text(encoding="utf-8", errors="ignore")

if "get_client_integration_secret" not in main:
    main = main.replace(
        "from backend.app.core.client_integrations_runtime import (",
        "from backend.app.core.client_integrations_runtime import (",
        1,
    )
    main = main.replace(
        "test_client_integration,\n)",
        "test_client_integration,\n    get_client_integration_secret,\n    log_email_proof_send,\n)",
        1,
    )

route = r'''

@app.post("/client/integrations/email/send-proof")
async def client_email_send_proof(payload: dict, x_tenant_id: str = Header(default="client_demo_001")):
    recipient = str(payload.get("recipient") or "").strip()
    if recipient.lower() != "leodavid2020@yahoo.com":
        return {
            "success": False,
            "error": "recipient_not_allowed",
            "message": "Controlled proof send is restricted to the approved test recipient.",
        }

    connection = get_client_integration_secret(x_tenant_id, "email")
    if not connection.get("success"):
        return connection

    subject = "Email Reply Agent proof: live automation test"
    body = (
        "Hi Leo,\n\n"
        "This is a controlled proof email from the Ecommerce AI Agent Platform.\n\n"
        "What this proves:\n"
        "- The client connected an email provider.\n"
        "- The Email Reply Agent can prepare a client-ready message.\n"
        "- The system can route the action through the connected email integration.\n"
        "- The action is logged without exposing the provider credential.\n\n"
        "Next production step: replace this proof mode with real provider send execution "
        "using encrypted credential storage and approval-gated sending.\n\n"
        "Regards,\n"
        "Ecommerce AI Agent Platform"
    )

    log_email_proof_send(
        x_tenant_id,
        {
            "recipient": recipient,
            "subject": subject,
            "provider": connection.get("provider"),
            "status": "proof_prepared",
            "credential_exposed": False,
        },
    )

    return {
        "success": True,
        "mode": "proof_prepared",
        "provider": connection.get("provider"),
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "credential_exposed": False,
        "approval_required_before_live_send": True,
        "message": "Proof email prepared and logged. Live send requires final Brevo send adapter wiring.",
    }
'''
if "/client/integrations/email/send-proof" not in main:
    main = main.rstrip() + "\n" + route + "\n"

main_path.write_text(main, encoding="utf-8")

test_path = ROOT / "test_step_i_email_proof_send.py"
test_path.write_text(r'''import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

payload = {"recipient": "leodavid2020@yahoo.com"}

r = requests.post(
    BASE + "/client/integrations/email/send-proof",
    json=payload,
    headers=HEADERS,
    timeout=60,
)

print("HTTP", r.status_code)
print(r.text)
''', encoding="utf-8")

print("STEP_I_BREVO_EMAIL_PROOF_SEND_INSTALLED")