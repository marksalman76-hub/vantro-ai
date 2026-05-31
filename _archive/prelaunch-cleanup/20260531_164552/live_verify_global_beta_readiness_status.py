import json
import os
import urllib.request
import urllib.error

BASE_URL = os.getenv("API_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")
TOKEN = os.getenv("ADMIN_PLATFORM_TOKEN", "").strip()

if not TOKEN:
    raise RuntimeError("Set ADMIN_PLATFORM_TOKEN first.")

req = urllib.request.Request(
    f"{BASE_URL}/admin/global-beta-readiness/status",
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
            data.get("global_beta_readiness_enabled") is True,
            data.get("global_first_architecture") is True,
            data.get("customer_safe") is True,
            data.get("credential_values_exposed") is False,
            isinstance(data.get("rows"), dict),
            "row6_live_execution_quality" in data.get("rows", {}),
            "row15_launch_readiness" in data.get("rows", {}),
        ]

        if all(required):
            print("GLOBAL_BETA_READINESS_STATUS_VERIFIED")
        else:
            raise RuntimeError("GLOBAL_BETA_READINESS_STATUS_INCOMPLETE")
except urllib.error.HTTPError as exc:
    print("HTTP_ERROR", exc.code)
    print(exc.read().decode("utf-8", errors="replace"))
    raise
