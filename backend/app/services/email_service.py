import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vantro.ai")
SES_REGION = os.getenv("AWS_REGION", "us-east-1")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://www.vantro.ai")


def _ses_client():
    return boto3.client("ses", region_name=SES_REGION)


def send_password_reset(to_email: str, reset_token: str) -> bool:
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    subject = "Reset your Vantro password"
    body_text = f"Click the link below to reset your password (expires in 1 hour):\n\n{reset_url}\n\nIf you didn't request this, ignore this email."
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;background:#0f0f13;color:#e5e7eb;">
      <div style="margin-bottom:32px;">
        <span style="font-size:20px;font-weight:700;color:#fff;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
      </div>
      <h2 style="color:#fff;margin-bottom:8px;">Reset your password</h2>
      <p style="color:#9ca3af;margin-bottom:32px;">Click the button below to set a new password. This link expires in 1 hour.</p>
      <a href="{reset_url}" style="display:inline-block;background:#7c3aed;color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;font-weight:600;">
        Reset password
      </a>
      <p style="color:#6b7280;font-size:12px;margin-top:40px;">If you didn't request a password reset, you can safely ignore this email.</p>
    </body></html>
    """
    return _send(to_email, subject, body_text, body_html)


def send_welcome(to_email: str, name: str) -> bool:
    subject = "Welcome to Vantro — let's create your first video"
    body_text = f"Hi {name},\n\nYour Vantro account is ready. Head to {FRONTEND_URL}/create to generate your first AI video.\n\nThe Vantro team"
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;background:#0f0f13;color:#e5e7eb;">
      <div style="margin-bottom:32px;">
        <span style="font-size:20px;font-weight:700;color:#fff;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
      </div>
      <h2 style="color:#fff;margin-bottom:8px;">Welcome, {name}!</h2>
      <p style="color:#9ca3af;margin-bottom:32px;">Your account is ready. Create your first AI video in under 2 minutes.</p>
      <a href="{FRONTEND_URL}/create" style="display:inline-block;background:#7c3aed;color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;font-weight:600;">
        Create your first video
      </a>
    </body></html>
    """
    return _send(to_email, subject, body_text, body_html)


def send_enterprise_enquiry(name: str, company: str, email: str, phone: str, volume: str, message: str) -> bool:
    subject = f"Enterprise enquiry from {company}"
    body_text = (
        f"Name: {name}\nCompany: {company}\nEmail: {email}\n"
        f"Phone: {phone or '—'}\nMonthly volume: {volume or '—'}\n\n{message or '(no message)'}"
    )
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px 20px;">
      <h2>Enterprise enquiry — {company}</h2>
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:8px 0;color:#6b7280;width:140px;">Name</td><td style="padding:8px 0;">{name}</td></tr>
        <tr><td style="padding:8px 0;color:#6b7280;">Company</td><td style="padding:8px 0;">{company}</td></tr>
        <tr><td style="padding:8px 0;color:#6b7280;">Email</td><td style="padding:8px 0;">{email}</td></tr>
        <tr><td style="padding:8px 0;color:#6b7280;">Phone</td><td style="padding:8px 0;">{phone or '—'}</td></tr>
        <tr><td style="padding:8px 0;color:#6b7280;">Volume/mo</td><td style="padding:8px 0;">{volume or '—'}</td></tr>
      </table>
      <hr style="margin:16px 0;border-color:#e5e7eb;"/>
      <p>{message or '(no message)'}</p>
    </body></html>
    """
    return _send("hello@vantro.ai", subject, body_text, body_html, reply_to=email)


def _send(to: str, subject: str, body_text: str, body_html: str, reply_to: str = "") -> bool:
    try:
        client = _ses_client()
        kwargs: dict = {
            "Source": FROM_EMAIL,
            "Destination": {"ToAddresses": [to]},
            "Message": {
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        }
        if reply_to:
            kwargs["ReplyToAddresses"] = [reply_to]
        client.send_email(**kwargs)
        logger.info("Email sent to %s: %s", to, subject)
        return True
    except ClientError as e:
        logger.error("SES error sending to %s: %s", to, e.response["Error"]["Message"])
        return False
    except Exception as e:
        logger.error("Email send failed: %s", e)
        return False
