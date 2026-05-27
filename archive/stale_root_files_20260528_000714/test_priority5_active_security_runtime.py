import json
import requests

BASE = "http://127.0.0.1:8000"

print("PRIORITY5_ACTIVE_SECURITY_RUNTIME_TEST")

r = requests.get(BASE + "/admin/security/active-runtime-readiness", timeout=30)
print("READINESS_HTTP", r.status_code)
print(json.dumps(r.json(), indent=2))

data = r.json()
assert r.status_code == 200
assert data["success"] is True
assert data["security_profile"] == "priority5_active_security_runtime_v1"
assert data["active_rate_limiting"] is True
assert data["persistent_security_audit_events"] is True
assert data["request_fingerprinting"] is True
assert data["csrf_validation_available"] is True
assert data["secret_values_exposed"] is False

probe = requests.get(BASE + "/admin/security/final-readiness", timeout=30)
print("PROTECTED_HEADER_HTTP", probe.status_code)
print("SECURITY_HEADER", probe.headers.get("X-Security-Profile"))
assert probe.headers.get("X-Security-Profile") == "priority5_active_security_runtime_v1"

print("PRIORITY5_ACTIVE_SECURITY_RUNTIME_OK")
