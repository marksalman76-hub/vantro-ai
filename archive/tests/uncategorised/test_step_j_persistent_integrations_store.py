import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

payload = {
    "integration_key": "email",
    "provider": "Brevo",
    "credential": "test_persistent_key_123456",
    "connection_mode": "scoped_api_key",
}

r = requests.post(BASE + "/client/integrations/connect", json=payload, headers=HEADERS, timeout=60)
print("connect", r.status_code, r.text)

r = requests.post(BASE + "/client/integrations/test", json={"integration_key": "email"}, headers=HEADERS, timeout=60)
print("test", r.status_code, r.text)

r = requests.get(BASE + "/client/integrations", headers=HEADERS, timeout=60)
print("list", r.status_code, r.text[:1200])
