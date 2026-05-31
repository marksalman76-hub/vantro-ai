from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
runtime_path = ROOT / "backend" / "app" / "core" / "client_integrations_runtime.py"

for path in [main_path, runtime_path]:
    backup = BACKUPS / f"{path.stem}_before_step_i2_real_brevo_send_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}"
    backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

runtime = runtime_path.read_text(encoding="utf-8", errors="ignore")

runtime = runtime.replace(
    '"credential_stored": True,\n        "credential_hint": _credential_hint(credential),',
    '"credential_stored": True,\n        "credential_value": credential,\n        "credential_hint": _credential_hint(credential),',
)

runtime = runtime.replace(
    '"credential_hint": connection.get("credential_hint"),\n    }',
    '"credential_hint": connection.get("credential_hint"),\n        "credential_value": connection.get("credential_value"),\n    }',
)

runtime_path.write_text(runtime, encoding="utf-8")

main = main_path.read_text(encoding="utf-8", errors="ignore")

if "import urllib.request" not in main:
    main = "import urllib.request\nimport urllib.error\nimport json\n" + main

route = r'''

@app.post("/client/integrations/email/send-live-proof")
async def client_email_send_live_proof(payload: dict, x_tenant_id: str = Header(default="client_demo_001")):
    recipient = str(payload.get("recipient") or "").strip()
    sender_email = str(payload.get("sender_email") or "").strip()
    sender_name = str(payload.get("sender_name") or "Ecommerce AI Agent Platform").strip()

    if recipient.lower() not in {"leodavid2020@gmail.com", "leodavid2020@yahoo.com"}:
        return {
            "success": False,
            "error": "recipient_not_allowed",
            "message": "Controlled live proof send is restricted to the approved test recipient.",
        }

    if not sender_email:
        return {
            "success": False,
            "error": "sender_email_required",
            "message": "Brevo requires a verified sender email address.",
        }

    connection = get_client_integration_secret(x_tenant_id, "email")
    if not connection.get("success"):
        return connection

    api_key = connection.get("credential_value")
    if not api_key:
        return {
            "success": False,
            "error": "credential_not_available",
            "message": "Reconnect Brevo so the server can store the credential for live sending.",
        }

    subject = "Email Reply Agent proof: live Brevo send"
    html_content = """
    <p>Hi Leo,</p>
    <p>This is a <strong>live Brevo send proof</strong> from the Ecommerce AI Agent Platform.</p>
    <p>This proves:</p>
    <ul>
      <li>The client connected Brevo.</li>
      <li>The platform stored the provider credential server-side.</li>
      <li>The Email Reply Agent can prepare a client-ready message.</li>
      <li>The backend can send through the connected provider without exposing the credential.</li>
      <li>The action is logged for audit and review.</li>
    </ul>
    <p>Regards,<br/>Ecommerce AI Agent Platform</p>
    """

    brevo_payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": recipient}],
        "subject": subject,
        "htmlContent": html_content,
    }

    request = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(brevo_payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_body = response.read().decode("utf-8")
            status_code = response.status
    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8")
        log_email_proof_send(
            x_tenant_id,
            {
                "recipient": recipient,
                "subject": subject,
                "provider": connection.get("provider"),
                "status": "brevo_send_failed",
                "brevo_status": error.code,
                "credential_exposed": False,
            },
        )
        return {
            "success": False,
            "error": "brevo_send_failed",
            "status_code": error.code,
            "provider_response": error_body,
            "credential_exposed": False,
        }
    except Exception as error:
        log_email_proof_send(
            x_tenant_id,
            {
                "recipient": recipient,
                "subject": subject,
                "provider": connection.get("provider"),
                "status": "send_exception",
                "credential_exposed": False,
            },
        )
        return {
            "success": False,
            "error": "send_exception",
            "message": str(error),
            "credential_exposed": False,
        }

    log_email_proof_send(
        x_tenant_id,
        {
            "recipient": recipient,
            "subject": subject,
            "provider": connection.get("provider"),
            "status": "sent",
            "brevo_status": status_code,
            "credential_exposed": False,
        },
    )

    return {
        "success": True,
        "mode": "live_brevo_send",
        "provider": connection.get("provider"),
        "recipient": recipient,
        "sender_email": sender_email,
        "subject": subject,
        "brevo_status": status_code,
        "provider_response": response_body,
        "credential_exposed": False,
        "message": "Live Brevo email sent and logged.",
    }
'''
if "/client/integrations/email/send-live-proof" not in main:
    main = main.rstrip() + "\n" + route + "\n"

main_path.write_text(main, encoding="utf-8")

test_path = ROOT / "test_step_i2_live_brevo_send.py"
test_path.write_text(r'''import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

payload = {
    "recipient": "leodavid2020@yahoo.com",
    "sender_email": "REPLACE_WITH_YOUR_VERIFIED_BREVO_SENDER_EMAIL",
    "sender_name": "Ecommerce AI Agent Platform",
}

r = requests.post(
    BASE + "/client/integrations/email/send-live-proof",
    json=payload,
    headers=HEADERS,
    timeout=60,
)

print("HTTP", r.status_code)
print(r.text)
''', encoding="utf-8")

print("STEP_I2_REAL_BREVO_SEND_ADAPTER_INSTALLED")