import json
import getpass
import requests

BASE_URL = "https://app.trance-formation.com.au/api"

admin_token = getpass.getpass("Paste ADMIN_PLATFORM_TOKEN: ").strip()
tenant_id = "client_manual_8c187cfb7f"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {admin_token}",
    "x-admin-token": admin_token,
    "x-actor-role": "admin",
    "x-tenant-id": tenant_id,
    "origin": "https://app.trance-formation.com.au",
    "referer": "https://app.trance-formation.com.au/admin",
}

payload = {
    "tenant_id": tenant_id,
    "monthly_credits": 25,
    "credits_used": 0,
    "credits_remaining": 25,
    "reason": "live_client_portal_ai_media_execution_test",
}

response = requests.post(
    f"{BASE_URL}/admin-client-credits-assign",
    headers=headers,
    json=payload,
    timeout=60,
)

print("STATUS", response.status_code)
print("CONTENT_TYPE", response.headers.get("content-type"))

try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)