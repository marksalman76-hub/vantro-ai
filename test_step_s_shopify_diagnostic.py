import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

payload = {
    "integration_key": "store",
    "action": "diagnose_connection",
    "payload": {
        "store_domain": "ncn1m2-ch.myshopify.com"
    },
}

r = requests.post(BASE + "/client/integrations/action", json=payload, headers=HEADERS, timeout=60)
print("shopify_diagnostic", r.status_code, r.text[:3000])
