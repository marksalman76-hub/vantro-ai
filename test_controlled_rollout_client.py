import requests

API_URL = "https://api.trance-formation.com.au"

payload = {
    "company_name": "Controlled Rollout Test Client",
    "contact_email": "replace-with-your-test-email@example.com",
    "package": "Manual Unlimited",
    "unlimited_credits": True,
}

headers = {
    "Content-Type": "application/json",
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
}

response = requests.post(
    f"{API_URL}/admin/deployment-control/deploy-manual-client",
    json=payload,
    headers=headers,
    timeout=60,
)

print("HTTP", response.status_code)
print(response.text)