import requests

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
