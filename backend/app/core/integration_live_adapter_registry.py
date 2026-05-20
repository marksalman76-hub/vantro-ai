from __future__ import annotations

import json
import urllib.error
import urllib.request
import urllib.parse
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

    if integration_key == "store" and action in {"read_products", "create_product_draft", "update_product_draft"}:
        return _execute_shopify_action(tenant_id, connection, action, payload)

    if integration_key == "crm" and action in {"create_contact", "add_note", "create_deal", "update_contact"}:
        return _execute_crm_action(tenant_id, connection, action, payload)

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



def _shopify_store_base_url(store_domain: str) -> str:
    store_domain = str(store_domain or "").strip()
    store_domain = store_domain.replace("https://", "").replace("http://", "").strip("/")
    if not store_domain:
        raise ValueError("store_domain_required")
    return f"https://{store_domain}"


def _execute_shopify_action(tenant_id: str, connection: Dict[str, Any], action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    provider = str(connection.get("provider") or "")
    if provider.lower() != "shopify":
        return {
            "success": False,
            "error": "provider_not_supported_for_store_live_execution",
            "provider": provider,
            "supported_provider": "Shopify",
        }

    api_token = connection.get("credential_value")
    if not api_token:
        return {
            "success": False,
            "error": "credential_not_available",
            "credential_exposed": False,
        }

    store_domain = str(payload.get("store_domain") or payload.get("shop_domain") or "").strip()
    try:
        base_url = _shopify_store_base_url(store_domain)
    except ValueError:
        return {
            "success": False,
            "error": "store_domain_required",
            "message": "Provide Shopify store domain, for example your-store.myshopify.com.",
        }

    if action == "read_products":
        return _shopify_read_products(base_url, api_token)

    if action == "create_product_draft":
        return _shopify_create_product_draft(base_url, api_token, payload)

    if action == "update_product_draft":
        return {
            "success": True,
            "mode": "shopify_update_product_draft_scaffold",
            "provider": "Shopify",
            "action": action,
            "live_execution_ready": False,
            "credential_exposed": False,
            "message": "Update product draft adapter scaffold registered. Product ID targeting is next.",
        }

    return {"success": False, "error": "unsupported_shopify_action", "action": action}


def _shopify_request(url: str, api_token: str, method: str = "GET", payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    data = None
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": api_token,
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return {
                "success": True,
                "status_code": response.status,
                "provider_response": body,
                "credential_exposed": False,
            }
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        return {
            "success": False,
            "error": "shopify_api_error",
            "status_code": error.code,
            "provider_response": body,
            "credential_exposed": False,
        }
    except Exception as error:
        return {
            "success": False,
            "error": "shopify_exception",
            "message": str(error),
            "credential_exposed": False,
        }


def _shopify_read_products(base_url: str, api_token: str) -> Dict[str, Any]:
    url = f"{base_url}/admin/api/2025-01/products.json?limit=5"
    result = _shopify_request(url, api_token, method="GET")
    result.update({
        "mode": "live_shopify_read_products",
        "provider": "Shopify",
        "action": "read_products",
    })
    return result


def _shopify_create_product_draft(base_url: str, api_token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    title = str(payload.get("title") or "AI Generated Product Draft").strip()
    body_html = str(payload.get("body_html") or payload.get("description") or "<p>Product draft created by Ecommerce AI Agent Platform.</p>").strip()
    vendor = str(payload.get("vendor") or "AI Generated").strip()
    product_type = str(payload.get("product_type") or "General").strip()
    price = str(payload.get("price") or "0.00").strip()
    sku = str(payload.get("sku") or "AI-DRAFT").strip()

    shopify_payload = {
        "product": {
            "title": title,
            "body_html": body_html,
            "vendor": vendor,
            "product_type": product_type,
            "status": "draft",
            "variants": [
                {
                    "price": price,
                    "sku": sku,
                }
            ],
        }
    }

    url = f"{base_url}/admin/api/2025-01/products.json"
    result = _shopify_request(url, api_token, method="POST", payload=shopify_payload)
    result.update({
        "mode": "live_shopify_create_product_draft",
        "provider": "Shopify",
        "action": "create_product_draft",
        "title": title,
        "status": "draft",
    })
    return result



def _execute_crm_action(tenant_id: str, connection: Dict[str, Any], action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    provider = str(connection.get("provider") or "").strip()
    token = connection.get("credential_value")

    if not token:
        return {"success": False, "error": "credential_not_available", "credential_exposed": False}

    if provider.lower() in {"hubspot", "hub spot"}:
        return _execute_hubspot_action(token, action, payload)

    if provider.lower() in {"gohighlevel", "go high level", "ghl"}:
        return _execute_gohighlevel_action(token, action, payload)

    return {
        "success": False,
        "error": "provider_not_supported_for_live_crm",
        "provider": provider,
        "supported_providers": ["HubSpot", "GoHighLevel"],
    }


def _crm_json_request(url: str, token: str, method: str, payload: Dict[str, Any] | None = None, provider: str = "crm") -> Dict[str, Any]:
    data = None
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    if provider == "GoHighLevel":
        headers["Version"] = "2021-07-28"
        headers["Accept"] = "application/json"
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return {
                "success": True,
                "status_code": response.status,
                "provider": provider,
                "provider_response": body,
                "credential_exposed": False,
            }
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        return {
            "success": False,
            "error": f"{provider}_api_error",
            "status_code": error.code,
            "provider_response": body,
            "credential_exposed": False,
        }
    except Exception as error:
        return {
            "success": False,
            "error": f"{provider}_exception",
            "message": str(error),
            "credential_exposed": False,
        }


def _execute_hubspot_action(token: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if action == "create_contact":
        email = str(payload.get("email") or "").strip()
        first_name = str(payload.get("first_name") or "").strip()
        last_name = str(payload.get("last_name") or "").strip()
        phone = str(payload.get("phone") or "").strip()
        company = str(payload.get("company") or "").strip()

        if not email:
            return {"success": False, "error": "email_required"}

        hs_payload = {
            "properties": {
                "email": email,
                "firstname": first_name,
                "lastname": last_name,
                "phone": phone,
                "company": company,
            }
        }

        result = _crm_json_request(
            "https://api.hubapi.com/crm/v3/objects/contacts",
            token,
            "POST",
            hs_payload,
            provider="HubSpot",
        )
        result.update({"mode": "live_hubspot_create_contact", "action": action})
        return result

    if action == "add_note":
        return {
            "success": True,
            "mode": "hubspot_add_note_scaffold",
            "provider": "HubSpot",
            "action": action,
            "live_execution_ready": False,
            "credential_exposed": False,
            "message": "HubSpot note scaffold registered. Association targeting is next.",
        }

    return {
        "success": True,
        "mode": "hubspot_action_scaffold",
        "provider": "HubSpot",
        "action": action,
        "live_execution_ready": False,
        "credential_exposed": False,
    }


def _execute_gohighlevel_action(token: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    location_id = str(payload.get("location_id") or "").strip()

    if not location_id:
        return {
            "success": False,
            "error": "location_id_required",
            "message": "GoHighLevel requires a location_id for contact actions.",
        }

    if action == "create_contact":
        email = str(payload.get("email") or "").strip()
        first_name = str(payload.get("first_name") or "").strip()
        last_name = str(payload.get("last_name") or "").strip()
        phone = str(payload.get("phone") or "").strip()

        if not email and not phone:
            return {"success": False, "error": "email_or_phone_required"}

        ghl_payload = {
            "locationId": location_id,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "phone": phone,
            "source": payload.get("source") or "Ecommerce AI Agent Platform",
        }

        result = _crm_json_request(
            "https://services.leadconnectorhq.com/contacts/",
            token,
            "POST",
            ghl_payload,
            provider="GoHighLevel",
        )
        result.update({"mode": "live_gohighlevel_create_contact", "action": action})
        return result

    if action == "update_contact":
        contact_id = str(payload.get("contact_id") or "").strip()
        if not contact_id:
            return {"success": False, "error": "contact_id_required"}

        update_payload = {
            "email": payload.get("email"),
            "firstName": payload.get("first_name"),
            "lastName": payload.get("last_name"),
            "phone": payload.get("phone"),
        }
        update_payload = {k: v for k, v in update_payload.items() if v not in [None, ""]}

        result = _crm_json_request(
            f"https://services.leadconnectorhq.com/contacts/{contact_id}",
            token,
            "PUT",
            update_payload,
            provider="GoHighLevel",
        )
        result.update({"mode": "live_gohighlevel_update_contact", "action": action, "contact_id": contact_id})
        return result

    if action == "add_note":
        contact_id = str(payload.get("contact_id") or "").strip()
        body = str(payload.get("body") or payload.get("note") or "").strip()

        if not contact_id:
            return {"success": False, "error": "contact_id_required"}
        if not body:
            return {"success": False, "error": "note_body_required"}

        note_payload = {
            "body": body,
        }

        result = _crm_json_request(
            f"https://services.leadconnectorhq.com/contacts/{contact_id}/notes",
            token,
            "POST",
            note_payload,
            provider="GoHighLevel",
        )
        result.update({"mode": "live_gohighlevel_add_note", "action": action, "contact_id": contact_id})
        return result

    if action == "create_deal":
        return {
            "success": False,
            "error": "owner_approval_required",
            "mode": "gohighlevel_create_deal_guarded",
            "provider": "GoHighLevel",
            "action": action,
            "message": "Creating opportunities/deals remains approval-gated before live execution.",
            "credential_exposed": False,
        }

    return {
        "success": False,
        "error": "unsupported_gohighlevel_action",
        "provider": "GoHighLevel",
        "action": action,
        "credential_exposed": False,
    }
