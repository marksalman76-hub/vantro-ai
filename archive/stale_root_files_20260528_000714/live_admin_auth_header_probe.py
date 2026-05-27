import json
from pathlib import Path
import requests

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

token = load_env_value("ADMIN_PLATFORM_TOKEN") or load_env_value("ADMIN_AUTH_SECRET")

if not token:
    raise SystemExit("Missing local admin token")

endpoint = "/admin/ai-media-pipeline/readiness"

tests = {
    "authorization_bearer": {
        "Authorization": f"Bearer {token}",
        "x-actor-role": "owner_admin",
    },
    "x_admin_token": {
        "x-admin-token": token,
        "x-actor-role": "owner_admin",
    },
    "both_headers": {
        "Authorization": f"Bearer {token}",
        "x-admin-token": token,
        "x-actor-role": "owner_admin",
    },
}

results = {}

for name, headers in tests.items():
    response = requests.get(BASE + endpoint, headers=headers, timeout=30)
    results[name] = {
        "status_code": response.status_code,
        "ok": response.ok,
        "body": response.json() if response.text else None,
    }

print(json.dumps(results, indent=2))