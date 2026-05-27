import json
import getpass
import requests

BASE_URL = "https://app.trance-formation.com.au/api"

admin_token = getpass.getpass("Paste ADMIN_PLATFORM_TOKEN: ").strip()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {admin_token}",
    "x-admin-token": admin_token,
    "x-actor-role": "admin",
    "x-tenant-id": "admin_global_provider_readiness",
    "origin": "https://app.trance-formation.com.au",
    "referer": "https://app.trance-formation.com.au/admin",
}

response = requests.get(
    f"{BASE_URL}/admin-global-provider-readiness",
    headers=headers,
    timeout=60,
)

print("STATUS", response.status_code)
print("CONTENT_TYPE", response.headers.get("content-type"))

try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)