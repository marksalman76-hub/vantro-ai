import json
import os
import urllib.request
import urllib.error

BASE_URL = os.getenv("API_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")
TOKEN = os.getenv("ADMIN_PLATFORM_TOKEN", "").strip()

if not TOKEN:
    raise RuntimeError("Set ADMIN_PLATFORM_TOKEN first.")

req = urllib.request.Request(
    f"{BASE_URL}/admin/global-commercial-launch/status",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "x-admin-token": TOKEN,
        "x-actor-role": "owner_admin",
        "x-tenant-id": "owner_admin",
    },
    method="GET",
)

try:
    with urllib.request.urlopen(req, timeout=60) as response:
        raw = response.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        print(json.dumps(data, indent=2))

        required = [
            data.get("success") is True,
            data.get("global_commercial_launch_enabled") is True,
            data.get("global_first_architecture") is True,
            data.get("multi_region_ready") is True,
            data.get("multi_currency_ready") is True,
            data.get("multi_language_ready") is True,
            data.get("enterprise_ready") is True,
            data.get("customer_safe") is True,
            data.get("credential_values_exposed") is False,
            isinstance(data.get("commercial_sections"), dict),
            "global_onboarding" in data.get("commercial_sections", {}),
            "customer_success" in data.get("commercial_sections", {}),
        ]

        if all(required):
            print("GLOBAL_COMMERCIAL_LAUNCH_STATUS_VERIFIED")
        else:
            raise RuntimeError("GLOBAL_COMMERCIAL_LAUNCH_STATUS_INCOMPLETE")
except urllib.error.HTTPError as exc:
    print("HTTP_ERROR", exc.code)
    print(exc.read().decode("utf-8", errors="replace"))
    raise
