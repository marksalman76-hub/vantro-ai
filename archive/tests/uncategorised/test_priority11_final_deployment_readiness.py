import json
import requests

BASE = "http://127.0.0.1:8000"
HEADERS = {"x-actor-role": "admin", "x-tenant-id": "owner"}

r = requests.get(f"{BASE}/admin/final-deployment-readiness", headers=HEADERS, timeout=30)
print(json.dumps(r.json(), indent=2)[:12000])

data = r.json()
assert r.status_code == 200
assert data["success"] is True
assert data["agent_registry"]["agent_count"] == 27
assert data["checks"]["agent_registry_27_ready"] is True
assert data["checks"]["all_agents_purchasable"] is True
assert data["checks"]["enterprise_contact_us"] is True
assert data["secret_exposure"] is False

print("\nPRIORITY11_FINAL_DEPLOYMENT_READINESS_OK")
