import json
from pathlib import Path
import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"
FRONTEND = "https://trance-formation.com.au"

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

token = load_env_value("ADMIN_PLATFORM_TOKEN") or load_env_value("ADMIN_AUTH_SECRET") or load_env_value("ADMIN_AUTH_TOKEN")

headers = {
    "x-actor-role": "owner",
    "x-tenant-id": "owner_admin",
    "Authorization": f"Bearer {token}",
    "x-admin-token": token,
    "Content-Type": "application/json",
    "Origin": FRONTEND,
    "Referer": FRONTEND + "/admin",
}

payload = {
    "agent_id": "ugc_video_agent",
    "brand_name": "Live Test Brand",
    "product_name": "Premium Test Product",
    "target_audience": "online shoppers",
    "objective": "premium UGC ad",
    "platform": "TikTok",
    "media_type": "ugc video",
    "language": "English",
    "region": "global"
}

response = requests.post(
    BASE + "/admin/ai-media-pipeline/run",
    headers=headers,
    json=payload,
    timeout=60,
)

print("STATUS", response.status_code)
print("CONTENT_TYPE", response.headers.get("content-type"))
print(response.text[:3000])