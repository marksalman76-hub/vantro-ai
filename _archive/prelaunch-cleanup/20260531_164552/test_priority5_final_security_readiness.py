import requests
import json

BASE = "http://127.0.0.1:8000"

print("PRIORITY5_FINAL_SECURITY_READINESS_TEST")

r = requests.get(BASE + "/admin/security/final-readiness", timeout=30)
print("HTTP", r.status_code)
print(json.dumps(r.json(), indent=2))

data = r.json()

assert r.status_code == 200
assert data["success"] is True
assert data["security_profile"] == "priority5_final_security_readiness_v1"
assert data["secret_values_exposed"] is False
assert data["customer_safe_response_mode"] is True
assert "critical" in data["suspicious_activity_severity_model"]
assert data["security_layers"]["client_entitlement_isolation_required"] is True
assert data["security_layers"]["owner_admin_bypass_limited_to_internal_operations"] is True

print("PRIORITY5_FINAL_SECURITY_READINESS_OK")
