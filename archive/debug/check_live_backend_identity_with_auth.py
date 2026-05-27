import requests
from pathlib import Path

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"

def load_env_value(key):
    for file_name in [".env.local", ".env"]:
        path = Path(file_name)
        if not path.exists():
            continue

        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            k, v = line.split("=", 1)
            if k.strip() == key:
                return v.strip().strip('"').strip("'")

    return None

token = (
    load_env_value("ADMIN_PLATFORM_TOKEN")
    or load_env_value("ADMIN_AUTH_SECRET")
    or load_env_value("ADMIN_AUTH_TOKEN")
)

headers = {
    "Authorization": f"Bearer {token}",
    "x-admin-token": token,
    "x-actor-role": "owner",
    "x-tenant-id": "owner_admin",
}

endpoints = [
    "/health",
    "/admin/security/readiness",
    "/admin/production-security/readiness",
    "/admin/ai-media-pipeline/readiness",
]

for endpoint in endpoints:
    response = requests.get(BASE + endpoint, headers=headers, timeout=30)
    print("=" * 80)
    print(endpoint)
    print("STATUS", response.status_code)
    print(response.text[:2000])