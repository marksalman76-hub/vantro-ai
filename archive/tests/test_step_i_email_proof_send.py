import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

payload = {"recipient": "leodavid2020@yahoo.com"}

r = requests.post(
    BASE + "/client/integrations/email/send-proof",
    json=payload,
    headers=HEADERS,
    timeout=60,
)

print("HTTP", r.status_code)
print(r.text)
