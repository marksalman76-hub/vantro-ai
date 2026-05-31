from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

runtime_path = ROOT / "backend" / "app" / "core" / "client_integrations_runtime.py"
main_path = ROOT / "backend" / "app" / "main.py"

for path in [runtime_path, main_path]:
    backup = BACKUPS / f"{path.stem}_before_step_k_global_adapter_registry_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}"
    backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

adapter_path = ROOT / "backend" / "app" / "core" / "integration_live_adapter_registry.py"
adapter_path.write_text(r'''from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict

from backend.app.core.client_integrations_runtime import (
    get_client_integration_secret,
    log_email_proof_send,
)

LIVE_ADAPTER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "email": {
        "status": "live_supported",
        "live_providers": ["Brevo"],
        "supported_actions": ["send_email"],
        "approval_required_actions": ["bulk_send", "campaign_send"],
    },
    "crm": {
        "status": "adapter_scaffold",
        "live_providers": ["GoHighLevel", "HubSpot", "Salesforce", "Pipedrive", "Zoho"],
        "supported_actions": ["create_contact", "update_contact", "add_note", "create_deal"],
        "approval_required_actions": ["bulk_import", "delete_contact", "pipeline_mass_update"],
    },
    "store": {
        "status": "adapter_scaffold",
        "live_providers": ["Shopify", "WooCommerce", "BigCommerce"],
        "supported_actions": ["create_product_draft", "update_product_draft", "read_products"],
        "approval_required_actions": ["publish_product", "change_price", "delete_product"],
    },
    "website": {
        "status": "adapter_scaffold",
        "live_providers": ["WordPress", "Webflow", "Shopify CMS", "Wix", "Squarespace"],
        "supported_actions": ["create_page_draft", "update_page_draft", "read_pages"],
        "approval_required_actions": ["publish_page", "deploy_site", "update_dns"],
    },
    "calendar": {
        "status": "adapter_scaffold",
        "live_providers": ["Google Calendar", "Outlook Calendar"],
        "supported_actions": ["create_event", "update_event", "read_availability"],
        "approval_required_actions": ["cancel_event", "bulk_reschedule"],
    },
    "sms": {
        "status": "adapter_scaffold",
        "live_providers": ["ClickSend", "Twilio"],
        "supported_actions": ["send_sms"],
        "approval_required_actions": ["bulk_sms", "marketing_sms"],
    },
    "social": {
        "status": "adapter_scaffold",
        "live_providers": ["Meta", "Instagram", "TikTok", "LinkedIn", "Pinterest"],
        "supported_actions": ["create_post_draft", "read_insights"],
        "approval_required_actions": ["publish_post", "send_dm", "boost_post"],
    },
    "ads": {
        "status": "adapter_scaffold",
        "live_providers": ["Meta Ads", "Google Ads", "TikTok Ads"],
        "supported_actions": ["create_campaign_draft", "read_campaigns", "read_performance"],
        "approval_required_actions": ["launch_campaign", "increase_budget", "change_bid_strategy"],
    },
    "analytics": {
        "status": "adapter_scaffold",
        "live_providers": ["GA4", "Search Console", "Meta Pixel", "Shopify Analytics"],
        "supported_actions": ["read_metrics", "read_traffic", "read_conversions"],
        "approval_required_actions": [],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def adapter_registry_summary() -> Dict[str, Any]:
    return {
        "success": True,
        "registry": LIVE_ADAPTER_REGISTRY,
        "global_adapter_path_ready": True,
        "live_supported_count": sum(1 for item in LIVE_ADAPTER_REGISTRY.values() if item["status"] == "live_supported"),
        "scaffold_count": sum(1 for item in LIVE_ADAPTER_REGISTRY.values() if item["status"] == "adapter_scaffold"),
        "governance": {
            "credential_exposure_allowed": False,
            "owner_approval_required_for_high_risk_actions": True,
            "tenant_isolation_required": True,
            "audit_required": True,
        },
    }


def execute_integration_action(
    tenant_id: str,
    integration_key: str,
    action: str,
    payload: Dict[str, Any],
    actor_role: str = "customer",
) -> Dict[str, Any]:
    integration_key = str(integration_key or "").strip()
    action = str(action or "").strip()

    adapter = LIVE_ADAPTER_REGISTRY.get(integration_key)
    if not adapter:
        return {"success": False, "error": "unsupported_integration"}

    if action not in adapter.get("supported_actions", []) and action not in adapter.get("approval_required_actions", []):
        return {
            "success": False,
            "error": "unsupported_action",
            "integration_key": integration_key,
            "action": action,
            "supported_actions": adapter.get("supported_actions", []),
            "approval_required_actions": adapter.get("approval_required_actions", []),
        }

    if action in adapter.get("approval_required_actions", []) and actor_role not in {"owner", "admin"}:
        return {
            "success": False,
            "error": "owner_approval_required",
            "integration_key": integration_key,
            "action": action,
            "message": "This action requires owner/admin approval before live execution.",
        }

    connection = get_client_integration_secret(tenant_id, integration_key)
    if not connection.get("success"):
        return connection

    if integration_key == "email" and action == "send_email":
        return _send_email_via_brevo(tenant_id, connection, payload)

    return {
        "success": True,
        "mode": "adapter_scaffold_ready",
        "integration_key": integration_key,
        "provider": connection.get("provider"),
        "action": action,
        "live_execution_ready": False,
        "credential_exposed": False,
        "message": "Adapter scaffold is registered. Provider-specific execution adapter is the next step.",
    }


def _send_email_via_brevo(tenant_id: str, connection: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    provider = str(connection.get("provider") or "")
    if provider.lower() != "brevo":
        return {
            "success": False,
            "error": "provider_not_supported_for_live_email",
            "provider": provider,
            "supported_provider": "Brevo",
        }

    api_key = connection.get("credential_value")
    if not api_key:
        return {
            "success": False,
            "error": "credential_not_available",
            "credential_exposed": False,
        }

    recipient = str(payload.get("recipient") or "").strip()
    sender_email = str(payload.get("sender_email") or "").strip()
    sender_name = str(payload.get("sender_name") or "Ecommerce AI Agent Platform").strip()
    subject = str(payload.get("subject") or "Email Reply Agent proof: live Brevo send").strip()
    html_content = str(payload.get("html_content") or payload.get("body") or "").strip()

    if not recipient:
        return {"success": False, "error": "recipient_required"}
    if not sender_email:
        return {"success": False, "error": "sender_email_required"}
    if not html_content:
        html_content = "<p>This is a live email sent by the Ecommerce AI Agent Platform.</p>"

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
            tenant_id,
            {
                "recipient": recipient,
                "subject": subject,
                "provider": provider,
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
            tenant_id,
            {
                "recipient": recipient,
                "subject": subject,
                "provider": provider,
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
        tenant_id,
        {
            "recipient": recipient,
            "subject": subject,
            "provider": provider,
            "status": "sent",
            "brevo_status": status_code,
            "credential_exposed": False,
        },
    )

    return {
        "success": True,
        "mode": "live_adapter_execution",
        "integration_key": "email",
        "provider": provider,
        "action": "send_email",
        "recipient": recipient,
        "sender_email": sender_email,
        "subject": subject,
        "brevo_status": status_code,
        "provider_response": response_body,
        "credential_exposed": False,
        "executed_at": _now(),
    }
''', encoding="utf-8")

main = main_path.read_text(encoding="utf-8", errors="ignore")

if "integration_live_adapter_registry" not in main:
    main = '''from backend.app.core.integration_live_adapter_registry import (
    adapter_registry_summary,
    execute_integration_action,
)
''' + main

routes = r'''

@app.get("/admin/integrations/live-adapter-registry")
async def admin_live_adapter_registry():
    return adapter_registry_summary()


@app.post("/client/integrations/action")
async def client_integration_action(payload: dict, x_tenant_id: str = Header(default="client_demo_001"), x_actor_role: str = Header(default="customer")):
    return execute_integration_action(
        tenant_id=x_tenant_id,
        integration_key=str(payload.get("integration_key") or ""),
        action=str(payload.get("action") or ""),
        payload=dict(payload.get("payload") or {}),
        actor_role=x_actor_role,
    )
'''
if "/client/integrations/action" not in main:
    main = main.rstrip() + "\n" + routes + "\n"

main_path.write_text(main, encoding="utf-8")

test_path = ROOT / "test_step_k_global_integration_adapter_registry.py"
test_path.write_text(r'''import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

r = requests.get(BASE + "/admin/integrations/live-adapter-registry", timeout=60)
print("registry", r.status_code, r.text[:1200])

payload = {
    "integration_key": "email",
    "action": "send_email",
    "payload": {
        "recipient": "leodavid2020@yahoo.com",
        "sender_email": "sksolutionsgroup@gmail.com",
        "sender_name": "Ecommerce AI Agent Platform",
        "subject": "Global adapter proof: Email Reply Agent",
        "html_content": "<p>This email was sent through the global integration live adapter registry.</p>",
    },
}

r = requests.post(BASE + "/client/integrations/action", json=payload, headers=HEADERS, timeout=60)
print("email_action", r.status_code, r.text)
''', encoding="utf-8")

print("STEP_K_GLOBAL_INTEGRATION_ADAPTER_REGISTRY_INSTALLED")