import json
import os
from pathlib import Path

import requests


BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"


def load_env_value(key: str):
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

    return os.getenv(key)


token = load_env_value("ADMIN_PLATFORM_TOKEN") or load_env_value("ADMIN_AUTH_SECRET")

if not token:
    raise SystemExit("Missing ADMIN_PLATFORM_TOKEN or ADMIN_AUTH_SECRET in .env.local/.env")

headers = {
    "x-actor-role": "owner_admin",
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

endpoints = [
    "/admin/ai-media-creative-director/readiness",
    "/admin/ai-media-pipeline/readiness",
]

results = {}

for endpoint in endpoints:
    response = requests.get(BASE + endpoint, headers=headers, timeout=30)
    results[endpoint] = {
        "status_code": response.status_code,
        "ok": response.ok,
        "body": response.json() if response.text else None,
    }

payload = {
    "agent_id": "ugc_video_agent",
    "brand_name": "Live Test Brand",
    "product_name": "Premium Test Product",
    "target_audience": "online shoppers",
    "objective": "multilingual premium UGC conversion ad",
    "platform": "TikTok",
    "media_type": "ugc video dubbing",
    "language": "Spanish",
    "target_languages": ["Spanish", "Arabic"],
    "region": "global",
    "character_id": "creator_live_001",
    "reference_asset_id": "face_ref_live_001",
}

response = requests.post(
    BASE + "/admin/ai-media-pipeline/run",
    headers=headers,
    json=payload,
    timeout=60,
)

results["/admin/ai-media-pipeline/run"] = {
    "status_code": response.status_code,
    "ok": response.ok,
    "body": response.json() if response.text else None,
}

print(json.dumps(results, indent=2))