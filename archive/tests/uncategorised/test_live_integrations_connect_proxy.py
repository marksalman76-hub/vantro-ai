import requests

FRONTEND = "https://trance-formation.com.au"

payload = {
    "integration_key": "email",
    "provider": "Brevo",
    "credential": "test_live_key_123456",
    "connection_mode": "scoped_api_key",
}

r = requests.post(
    f"{FRONTEND}/api/client-integrations-connect",
    json=payload,
    timeout=60,
)

print("HTTP", r.status_code)
print(r.text)