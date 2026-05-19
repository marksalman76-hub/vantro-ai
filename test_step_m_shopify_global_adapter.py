import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

registry = requests.get(BASE + "/admin/integrations/live-adapter-registry", timeout=60)
print("registry", registry.status_code, registry.text[:1000])

payload = {
    "integration_key": "store",
    "action": "read_products",
    "payload": {
        "store_domain": "REPLACE_WITH_SHOPIFY_STORE_DOMAIN"
    },
}

r = requests.post(BASE + "/client/integrations/action", json=payload, headers=HEADERS, timeout=60)
print("shopify_read_products", r.status_code, r.text[:2000])
