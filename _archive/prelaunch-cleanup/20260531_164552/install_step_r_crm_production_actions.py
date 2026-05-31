from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

path = ROOT / "backend" / "app" / "core" / "integration_live_adapter_registry.py"
backup = BACKUPS / f"integration_live_adapter_registry_before_step_r_crm_actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

s = path.read_text(encoding="utf-8", errors="ignore")

old = '''    if action == "create_contact":
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

new = '''    if action == "create_contact":
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
'''

if old not in s:
    raise SystemExit("TARGET_GHL_ACTION_BLOCK_NOT_FOUND")

s = s.replace(old, new, 1)

path.write_text(s, encoding="utf-8")

test = ROOT / "test_step_r_crm_production_actions.py"
test.write_text(r'''import json
import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

LOCATION_ID = "mlWJi2CdN2cXHRe06d5b"

create_payload = {
    "integration_key": "crm",
    "action": "create_contact",
    "payload": {
        "location_id": LOCATION_ID,
        "email": "test.crm.production.actions@example.com",
        "first_name": "CRM",
        "last_name": "Production",
        "phone": "+61400000001",
        "source": "Ecommerce AI Agent Platform production action test"
    },
}

r = requests.post(BASE + "/client/integrations/action", json=create_payload, headers=HEADERS, timeout=60)
print("create_contact", r.status_code, r.text[:2500])

contact_id = None
try:
    data = r.json()
    provider_response = json.loads(data.get("provider_response", "{}"))
    contact_id = provider_response.get("contact", {}).get("id")
except Exception:
    pass

if contact_id:
    update_payload = {
        "integration_key": "crm",
        "action": "update_contact",
        "payload": {
            "location_id": LOCATION_ID,
            "contact_id": contact_id,
            "first_name": "CRM Updated",
        },
    }
    r = requests.post(BASE + "/client/integrations/action", json=update_payload, headers=HEADERS, timeout=60)
    print("update_contact", r.status_code, r.text[:2500])

    note_payload = {
        "integration_key": "crm",
        "action": "add_note",
        "payload": {
            "location_id": LOCATION_ID,
            "contact_id": contact_id,
            "body": "AI Agent proof note: CRM live adapter created and updated this contact safely.",
        },
    }
    r = requests.post(BASE + "/client/integrations/action", json=note_payload, headers=HEADERS, timeout=60)
    print("add_note", r.status_code, r.text[:2500])
else:
    print("SKIPPED update/note because contact_id was not returned")
''', encoding="utf-8")

print("STEP_R_CRM_PRODUCTION_ACTIONS_INSTALLED")
print(f"Backup: {backup}")