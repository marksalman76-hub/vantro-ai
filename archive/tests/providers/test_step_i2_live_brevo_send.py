import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

payload = {
    "recipient": "leodavid2020@yahoo.com",
    "sender_email": "REPLACE_WITH_YOUR_VERIFIED_BREVO_SENDER_EMAIL",
    "sender_name": "Ecommerce AI Agent Platform",
}

r = requests.post(
    BASE + "/client/integrations/email/send-live-proof",
    json=payload,
    headers=HEADERS,
    timeout=60,
)

print("HTTP", r.status_code)
print(r.text)
