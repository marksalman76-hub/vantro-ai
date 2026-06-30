import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vantro.ai")
SES_REGION = os.getenv("AWS_REGION", "us-east-1")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://vantro.ai")


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


def send_payment_failed(to_email: str, name: str, error_msg: str = "") -> bool:
    subject = "Action required — payment failed on your Vantro account"
    detail = f" ({error_msg})" if error_msg else ""
    body_text = (
        f"Hi {name},\n\n"
        f"A recent payment attempt on your Vantro account failed{detail}. "
        f"Your agents are paused until payment is resolved.\n\n"
        f"Update your billing details at {FRONTEND_URL}/dashboard/billing\n\nThe Vantro team"
    )
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;background:#0f0f13;color:#e5e7eb;">
      <div style="margin-bottom:32px;">
        <span style="font-size:20px;font-weight:700;color:#fff;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
      </div>
      <div style="background:#7f1d1d20;border:1px solid #7f1d1d40;border-radius:12px;padding:16px 20px;margin-bottom:24px;">
        <p style="color:#fca5a5;font-weight:600;margin:0;">Payment failed{detail}</p>
      </div>
      <h2 style="color:#fff;margin-bottom:8px;">Action required</h2>
      <p style="color:#9ca3af;margin-bottom:32px;">
        A payment attempt on your Vantro subscription failed. Your agents have been paused.
        Please update your payment method to resume access.
      </p>
      <a href="{FRONTEND_URL}/dashboard/billing" style="display:inline-block;background:#7c3aed;color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;font-weight:600;">
        Update billing
      </a>
      <p style="color:#6b7280;font-size:12px;margin-top:40px;">
        If you believe this is an error, reply to this email or contact support at hello@vantro.ai.
      </p>
    </body></html>
    """
    return _send(to_email, subject, body_text, body_html)


def send_billing_reminder(to_email: str, name: str, renewal_date) -> bool:
    """2-day pre-billing reminder email. renewal_date is a datetime object."""
    from datetime import datetime
    date_str = renewal_date.strftime("%B %d, %Y") if hasattr(renewal_date, "strftime") else str(renewal_date)
    subject = f"Your Vantro subscription renews on {date_str}"
    body_text = (
        f"Hi {name},\n\n"
        f"Your Vantro subscription will renew on {date_str}. "
        f"Your card on file will be charged automatically.\n\n"
        f"To update your payment method or manage your subscription, visit "
        f"{FRONTEND_URL}/dashboard/billing\n\nThe Vantro team"
    )
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;background:#0f0f13;color:#e5e7eb;">
      <div style="margin-bottom:32px;">
        <span style="font-size:20px;font-weight:700;color:#fff;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
      </div>
      <h2 style="color:#fff;margin-bottom:8px;">Your subscription renews in 2 days</h2>
      <p style="color:#9ca3af;margin-bottom:8px;">Hi {name},</p>
      <p style="color:#9ca3af;margin-bottom:32px;">
        Your Vantro subscription will automatically renew on <strong style="color:#e5e7eb;">{date_str}</strong>.
        Your saved payment method will be charged. No action needed unless you want to make changes.
      </p>
      <a href="{FRONTEND_URL}/dashboard/billing" style="display:inline-block;background:#7c3aed;color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;font-weight:600;">
        Manage billing
      </a>
      <p style="color:#6b7280;font-size:12px;margin-top:40px;">
        Questions? Reply to this email or contact support at hello@vantro.ai.
      </p>
    </body></html>
    """
    return _send(to_email, subject, body_text, body_html)


def send_approval_needed(admin_email: str, job_id: str, agent_id: str, user_email: str) -> bool:
    """Notify admin that a HITL job is waiting for approval."""
    approve_url = f"{FRONTEND_URL}/admin/approvals"
    subject = f"[Vantro] Agent job pending approval — {agent_id}"
    body_text = (
        f"A new agent job requires your approval.\n\n"
        f"Agent: {agent_id}\nJob ID: {job_id}\nRequested by: {user_email}\n\n"
        f"Review and approve at {approve_url}"
    )
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;background:#0f0f13;color:#e5e7eb;">
      <div style="margin-bottom:32px;">
        <span style="font-size:20px;font-weight:700;color:#fff;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
      </div>
      <h2 style="color:#fff;margin-bottom:8px;">Agent job pending approval</h2>
      <table style="width:100%;margin-bottom:24px;">
        <tr><td style="color:#9ca3af;padding:4px 0;width:120px;">Agent</td><td style="color:#e5e7eb;">{agent_id}</td></tr>
        <tr><td style="color:#9ca3af;padding:4px 0;">Job ID</td><td style="color:#e5e7eb;">{job_id}</td></tr>
        <tr><td style="color:#9ca3af;padding:4px 0;">Requested by</td><td style="color:#e5e7eb;">{user_email}</td></tr>
      </table>
      <a href="{approve_url}" style="display:inline-block;background:#7c3aed;color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;font-weight:600;">
        Review &amp; approve
      </a>
    </body></html>
    """
    return _send(admin_email, subject, body_text, body_html)


def send_activation_link(
    to_email: str,
    name: str,
    activation_url: str,
    plan: str,
    agent_names: list[str],
) -> bool:
    plan_label = plan.capitalize()
    agents_html = "".join(
        f'<li style="color:#c4b5fd;padding:4px 0;">{a}</li>' for a in agent_names
    )
    agents_text = "\n".join(f"  • {a}" for a in agent_names)
    subject = "Your Vantro workspace is ready — activate now"
    body_text = (
        f"Hi {name},\n\n"
        f"Payment confirmed. Your {plan_label} plan is ready.\n\n"
        f"Click the link below to activate your workspace and unlock your agents (link expires in 7 days):\n\n"
        f"{activation_url}\n\n"
        f"Agents included with your plan:\n{agents_text}\n\n"
        f"Questions? Reply to this email or contact hello@vantro.ai\n\nThe Vantro team"
    )
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;background:#0f0f13;color:#e5e7eb;">
      <div style="margin-bottom:32px;">
        <span style="font-size:20px;font-weight:700;color:#fff;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
      </div>
      <div style="background:#4c1d9520;border:1px solid #6d28d940;border-radius:12px;padding:20px 24px;margin-bottom:28px;">
        <p style="color:#a78bfa;font-weight:600;font-size:13px;margin:0 0 4px;">Payment confirmed</p>
        <p style="color:#fff;font-size:22px;font-weight:700;margin:0;">{plan_label} plan activated</p>
      </div>
      <h2 style="color:#fff;margin-bottom:8px;">Welcome, {name}!</h2>
      <p style="color:#9ca3af;margin-bottom:24px;">
        Click the button below to activate your workspace. This is a one-time link and expires in 7 days.
      </p>
      <a href="{activation_url}" style="display:inline-block;background:#7c3aed;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:700;font-size:16px;margin-bottom:32px;">
        Activate my workspace
      </a>
      <div style="background:#1f1f2e;border-radius:10px;padding:20px 24px;margin-bottom:24px;">
        <p style="color:#9ca3af;font-size:13px;font-weight:600;margin:0 0 12px;text-transform:uppercase;letter-spacing:.05em;">Agents included</p>
        <ul style="margin:0;padding-left:20px;list-style:disc;">
          {agents_html}
        </ul>
      </div>
      <p style="color:#6b7280;font-size:12px;margin-top:32px;">
        Monthly billing starts today. Manage your subscription at any time from your billing settings.<br/>
        Questions? Contact <a href="mailto:hello@vantro.ai" style="color:#8b5cf6;">hello@vantro.ai</a>
      </p>
    </body></html>
    """
    return _send(to_email, subject, body_text, body_html)


def send_approval_needed_owner(
    owner_email: str,
    owner_name: str,
    agent_name: str,
    job_id: str,
) -> bool:
    """Notify the workspace owner that their HITL-3 agent job needs admin approval.

    Distinct from send_approval_needed (which notifies the platform admin).
    This notifies the *requester* that their job is held pending approval.
    """
    job_url = f"{FRONTEND_URL}/admin/jobs/{job_id}"
    subject = f"[Vantro] Your agent job is pending approval"
    body_text = (
        f"Hi {owner_name},\n\n"
        f"Your agent job ({agent_name}) has been submitted and is awaiting admin approval "
        f"before execution.\n\n"
        f"Job ID: {job_id}\n"
        f"View status: {job_url}\n\n"
        f"You will receive another email once an administrator reviews your request.\n\n"
        f"The Vantro team"
    )
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;background:#0f0f13;color:#e5e7eb;">
      <div style="margin-bottom:32px;">
        <span style="font-size:20px;font-weight:700;color:#fff;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
      </div>
      <h2 style="color:#fff;margin-bottom:8px;">Job pending approval</h2>
      <p style="color:#9ca3af;margin-bottom:24px;">Hi {owner_name},</p>
      <p style="color:#9ca3af;margin-bottom:24px;">
        Your <strong style="color:#e5e7eb;">{agent_name}</strong> job has been submitted and is
        awaiting administrator approval before it can run.
      </p>
      <table style="width:100%;margin-bottom:24px;">
        <tr><td style="color:#9ca3af;padding:4px 0;width:100px;">Agent</td><td style="color:#e5e7eb;">{agent_name}</td></tr>
        <tr><td style="color:#9ca3af;padding:4px 0;">Job ID</td><td style="color:#a78bfa;font-family:monospace;">{job_id}</td></tr>
      </table>
      <a href="{job_url}" style="display:inline-block;background:#7c3aed;color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;font-weight:600;">
        View job status
      </a>
      <p style="color:#6b7280;font-size:12px;margin-top:40px;">
        You will be notified once an administrator reviews your request.
      </p>
    </body></html>
    """
    return _send(owner_email, subject, body_text, body_html)


def send_approval_result(user_email: str, agent_id: str, approved: bool, reason: str = "") -> bool:
    """Notify user of admin approval/rejection decision."""
    status_label = "approved" if approved else "rejected"
    subject = f"[Vantro] Your agent job has been {status_label}"
    detail = f"\n\nAdmin note: {reason}" if reason else ""
    body_text = (
        f"Your agent job ({agent_id}) has been {status_label} by an administrator.{detail}\n\n"
        f"View your jobs at {FRONTEND_URL}/dashboard"
    )
    action_color = "#7c3aed" if approved else "#dc2626"
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;background:#0f0f13;color:#e5e7eb;">
      <div style="margin-bottom:32px;">
        <span style="font-size:20px;font-weight:700;color:#fff;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
      </div>
      <h2 style="color:#fff;margin-bottom:8px;">Job {status_label}</h2>
      <p style="color:#9ca3af;margin-bottom:{'16px' if reason else '32px'};">
        Your agent job (<code style="color:#a78bfa;">{agent_id}</code>) has been {status_label} by an administrator.
      </p>
      {f'<p style="color:#9ca3af;margin-bottom:32px;">Admin note: {reason}</p>' if reason else ''}
      <a href="{FRONTEND_URL}/dashboard" style="display:inline-block;background:{action_color};color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;font-weight:600;">
        View dashboard
      </a>
    </body></html>
    """
    return _send(user_email, subject, body_text, body_html)


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
