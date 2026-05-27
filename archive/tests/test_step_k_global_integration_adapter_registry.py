import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

r = requests.get(BASE + "/admin/integrations/live-adapter-registry", timeout=60)
print("registry", r.status_code, r.text[:1200])

payload = {
    "integration_key": "email",
    "action": "send_email",
    "payload": {
        "recipient": "leodavid2020@yahoo.com",
        "sender_email": "sksolutionsgroup@gmail.com",
        "sender_name": "Ecommerce AI Agent Platform",
        "subject": "Global adapter proof: Email Reply Agent",
        "html_content": "<p>This email was sent through the global integration live adapter registry.</p>",
    },
}

r = requests.post(BASE + "/client/integrations/action", json=payload, headers=HEADERS, timeout=60)
print("email_action", r.status_code, r.text)
