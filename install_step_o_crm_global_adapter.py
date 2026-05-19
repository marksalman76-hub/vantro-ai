from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

adapter_path = ROOT / "backend" / "app" / "core" / "integration_live_adapter_registry.py"
backup = BACKUPS / f"integration_live_adapter_registry_before_step_o_crm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(adapter_path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

text = adapter_path.read_text(encoding="utf-8", errors="ignore")

text = text.replace(
    '''    if integration_key == "store" and action in {"read_products", "create_product_draft", "update_product_draft"}:
        return _execute_shopify_action(tenant_id, connection, action, payload)''',
    '''    if integration_key == "store" and action in {"read_products", "create_product_draft", "update_product_draft"}:
        return _execute_shopify_action(tenant_id, connection, action, payload)

    if integration_key == "crm" and action in {"create_contact", "add_note", "create_deal", "update_contact"}:
        return _execute_crm_action(tenant_id, connection, action, payload)''',
)

if "def _execute_crm_action" not in text:
    text += r'''


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

    return {
        "success": True,
        "mode": "gohighlevel_action_scaffold",
        "provider": "GoHighLevel",
        "action": action,
        "live_execution_ready": False,
        "credential_exposed": False,
    }
'''

adapter_path.write_text(text, encoding="utf-8")

test_path = ROOT / "test_step_o_crm_global_adapter.py"
test_path.write_text(r'''import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

payload = {
    "integration_key": "crm",
    "action": "create_contact",
    "payload": {
        "email": "test.crm.proof@example.com",
        "first_name": "CRM",
        "last_name": "Proof",
        "phone": "+61400000000",
        "company": "Ecommerce AI Agent Platform"
    },
}

r = requests.post(BASE + "/client/integrations/action", json=payload, headers=HEADERS, timeout=60)
print("crm_create_contact", r.status_code, r.text[:2500])
''', encoding="utf-8")

print("STEP_O_CRM_GLOBAL_ADAPTER_INSTALLED")
print(f"Backup: {backup}")