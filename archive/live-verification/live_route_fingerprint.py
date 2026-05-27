import requests

BASE = "https://ecommerce-ai-agent-platform-1.onrender.com"

endpoints = [
    "/health",
    "/admin/ai-media-pipeline/readiness",
    "/admin/ai-media-creative-director/readiness",
]

for endpoint in endpoints:
    response = requests.get(BASE + endpoint, timeout=30)
    print("=" * 80)
    print(endpoint)
    print("STATUS", response.status_code)
    print(response.text[:1000])