import json
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
