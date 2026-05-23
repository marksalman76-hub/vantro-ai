from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FILE = ROOT / "backend" / "app" / "core" / "admin_deployment_control_runtime.py"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_deployment_control_runtime_before_real_activation_{timestamp}.py"
shutil.copy2(FILE, backup)

text = FILE.read_text(encoding="utf-8")

if "from backend.app.core.tenant_account_runtime import create_client_activation_invite" not in text:
    text = text.replace(
        "from typing import Any, Dict, List\n",
        "from typing import Any, Dict, List\n\nfrom backend.app.core.tenant_account_runtime import create_client_activation_invite\n",
    )

old = '''    activation_token = f"act_{uuid.uuid4().hex}"

    tenant_record = {
        "tenant_id": tenant_id,
        "company_name": company_name,
        "contact_email": contact_email,
        "package": package_name,
        "active_agents": active_agents,
        "status": "deployed",
        "access_status": "active",
        "execution_status": "allowed",
        "unlimited_credits": unlimited_credits,
        "credit_state": credit_state,
        "activation_token": activation_token,
        "activation_link": f"/activate?token={activation_token}",
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "credential_values_exposed": False,
    }'''

new = '''    invite = create_client_activation_invite({
        "tenant_id": tenant_id,
        "email": contact_email,
        "company_name": company_name,
        "package": package_name,
        "active_agents": active_agents,
    })

    if not invite.get("success"):
        return {
            "success": False,
            "error": invite.get("error") or "activation_invite_failed",
            "credential_values_exposed": False,
        }

    activation_token = invite.get("activation_token")
    activation_link = invite.get("activation_path")

    tenant_record = {
        "tenant_id": tenant_id,
        "company_name": company_name,
        "contact_email": contact_email,
        "package": package_name,
        "active_agents": active_agents,
        "status": "deployed",
        "access_status": "active",
        "execution_status": "allowed",
        "unlimited_credits": unlimited_credits,
        "credit_state": credit_state,
        "activation_token": activation_token,
        "activation_link": activation_link,
        "activation_expires_at": invite.get("expires_at"),
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "credential_values_exposed": False,
    }'''

if old not in text:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

text = text.replace(old, new)

FILE.write_text(text, encoding="utf-8")

print("ADMIN_DEPLOY_REAL_ACTIVATION_INVITE_FIXED")
print(f"Backup: {backup}")