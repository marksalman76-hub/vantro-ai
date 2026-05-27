import json
import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"

endpoints = [
    "/health",
    "/admin/security/readiness",
    "/admin/production-security/readiness",
    "/admin/ai-media-pipeline/readiness",
]

for endpoint in endpoints:
    try:
        response = requests.get(BASE + endpoint, timeout=30)
        print("=" * 80)
        print(endpoint)
        print("STATUS", response.status_code)
        print(response.text[:1500])
    except Exception as error:
        print("=" * 80)
        print(endpoint)
        print("ERROR", str(error))