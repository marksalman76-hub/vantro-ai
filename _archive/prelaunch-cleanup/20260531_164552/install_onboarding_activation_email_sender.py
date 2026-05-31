from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

ADMIN_RUNTIME = ROOT / "backend" / "app" / "core" / "admin_deployment_control_runtime.py"
EMAIL_RUNTIME = ROOT / "backend" / "app" / "core" / "onboarding_email_runtime.py"

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_deployment_control_runtime_before_onboarding_email_{stamp}.py"
shutil.copy2(ADMIN_RUNTIME, backup)

EMAIL_RUNTIME.write_text(r'''from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Any, Dict


def _frontend_url() -> str:
    return (
        os.getenv("FRONTEND_PUBLIC_URL")
        or os.getenv("NEXT_PUBLIC_APP_URL")
        or os.getenv("FRONTEND_URL")
        or "https://ecommerce-ai-agent-platform.vercel.app"
    ).rstrip("/")


def build_activation_url(activation_path: str) -> str:
    path = str(activation_path or "").strip()
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return f"{_frontend_url()}{path}"


def email_config_status() -> Dict[str, Any]:
    required = {
        "SMTP_HOST": os.getenv("SMTP_HOST"),
        "SMTP_PORT": os.getenv("SMTP_PORT"),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
        "SMTP_FROM_EMAIL": os.getenv("SMTP_FROM_EMAIL"),
    }

    missing = [key for key, value in required.items() if not value]

    return {
        "success": len(missing) == 0,
        "configured": len(missing) == 0,
        "missing": missing,
        "secret_values_exposed": False,
    }


def send_client_activation_email(payload: Dict[str, Any]) -> Dict[str, Any]:
    contact_email = str(payload.get("contact_email") or payload.get("email") or "").strip()
    company_name = str(payload.get("company_name") or "Client").strip()
    activation_path = str(payload.get("activation_link") or payload.get("activation_path") or "").strip()
    package_name = str(payload.get("package") or "Business").strip()

    if not contact_email or "@" not in contact_email:
        return {
            "success": False,
            "email_sent": False,
            "reason": "valid_contact_email_required",
            "secret_values_exposed": False,
        }

    activation_url = build_activation_url(activation_path)
    config = email_config_status()

    if not config["configured"]:
        return {
            "success": False,
            "email_sent": False,
            "reason": "smtp_not_configured",
            "missing_env": config["missing"],
            "activation_url": activation_url,
            "secret_values_exposed": False,
        }

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM_EMAIL", "")
    smtp_from_name = os.getenv("SMTP_FROM_NAME", "Ecommerce AI Agent Platform")

    subject = "Activate your Ecommerce AI Agent workspace"

    text_body = f"""Hi,

Your Ecommerce AI Agent workspace for {company_name} is ready.

Package: {package_name}

Click this secure link to activate your account and create your password:

{activation_url}

This link is single-use. If it has already been used or expires, please request a new activation link.

Thank you.
"""

    html_body = f"""
    <div style="font-family:Arial,sans-serif;line-height:1.6;color:#111827">
      <h2>Your Ecommerce AI Agent workspace is ready</h2>
      <p>Your workspace for <strong>{company_name}</strong> has been deployed.</p>
      <p><strong>Package:</strong> {package_name}</p>
      <p>
        <a href="{activation_url}" style="display:inline-block;background:#2563eb;color:#ffffff;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:700">
          Activate your account
        </a>
      </p>
      <p>This link is single-use. If it has already been used or expires, please request a new activation link.</p>
    </div>
    """

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{smtp_from_name} <{smtp_from}>"
    message["To"] = contact_email
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        return {
            "success": True,
            "email_sent": True,
            "recipient": contact_email,
            "activation_url": activation_url,
            "secret_values_exposed": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "email_sent": False,
            "reason": "smtp_send_failed",
            "error": str(exc),
            "activation_url": activation_url,
            "secret_values_exposed": False,
        }
''', encoding="utf-8")

text = ADMIN_RUNTIME.read_text(encoding="utf-8")

if "from backend.app.core.onboarding_email_runtime import send_client_activation_email" not in text:
    text = text.replace(
        "from backend.app.core.postgres_account_runtime import create_activation_invite as pg_create_activation_invite\n",
        "from backend.app.core.postgres_account_runtime import create_activation_invite as pg_create_activation_invite\nfrom backend.app.core.onboarding_email_runtime import send_client_activation_email\n",
    )

old = '''    data["tenants"][tenant_id] = tenant_record
    data["events"].append(_event("manual_client_system_deployed", tenant_id, {
        "company_name": company_name,
        "package": package_name,
        "active_agent_count": len(active_agents),
        "unlimited_credits": unlimited_credits,
    }))

    _save_state(data)

    return {
        "success": True,
        "status": "manual_client_system_deployed",
        "tenant": tenant_record,
        "credential_values_exposed": False,
    }'''

new = '''    email_result = send_client_activation_email({
        "contact_email": contact_email,
        "company_name": company_name,
        "package": package_name,
        "activation_link": activation_link,
    })

    tenant_record["activation_email"] = {
        "attempted": True,
        "sent": bool(email_result.get("email_sent")),
        "reason": email_result.get("reason"),
        "recipient": contact_email,
        "secret_values_exposed": False,
    }

    data["tenants"][tenant_id] = tenant_record
    data["events"].append(_event("manual_client_system_deployed", tenant_id, {
        "company_name": company_name,
        "package": package_name,
        "active_agent_count": len(active_agents),
        "unlimited_credits": unlimited_credits,
        "activation_email_sent": bool(email_result.get("email_sent")),
    }))

    _save_state(data)

    return {
        "success": True,
        "status": "manual_client_system_deployed",
        "tenant": tenant_record,
        "activation_email": email_result,
        "credential_values_exposed": False,
    }'''

if old not in text:
    raise SystemExit("TARGET_ADMIN_DEPLOY_RETURN_BLOCK_NOT_FOUND")

text = text.replace(old, new)

ADMIN_RUNTIME.write_text(text, encoding="utf-8")

print("ONBOARDING_ACTIVATION_EMAIL_SENDER_INSTALLED")
print(f"Backup: {backup}")
print("Created: backend\\app\\core\\onboarding_email_runtime.py")
print("Updated: backend\\app\\core\\admin_deployment_control_runtime.py")