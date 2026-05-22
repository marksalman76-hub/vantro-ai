from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
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
    message["From"] = Address(display_name=smtp_from_name, addr_spec=smtp_from)
    message["To"] = contact_email
    message.set_content(text_body, charset="utf-8")
    message.add_alternative(html_body, subtype="html", charset="utf-8")

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
