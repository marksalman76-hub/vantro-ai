import requests

BASE = "http://127.0.0.1:8000"
HEADERS = {"x-tenant-id": "client_demo_001", "x-actor-role": "customer", "Content-Type": "application/json"}

checks = []

def record(name, ok, detail=""):
    checks.append((name, ok, detail))
    print(f"{name}: {'PASS' if ok else 'FAIL'} {detail}")

r = requests.get(f"{BASE}/client/integrations", headers=HEADERS, timeout=30)
record("list_integrations", r.status_code == 200 and r.json().get("success"), f"HTTP={r.status_code}")

payload = {"integration_key": "email", "provider": "Brevo", "credential": "test_scoped_key_123456", "connection_mode": "scoped_api_key"}
r = requests.post(f"{BASE}/client/integrations/connect", json=payload, headers=HEADERS, timeout=30)
record("connect_email", r.status_code == 200 and r.json().get("success"), f"HTTP={r.status_code}")

r = requests.post(f"{BASE}/client/integrations/test", json={"integration_key": "email"}, headers=HEADERS, timeout=30)
record("test_email", r.status_code == 200 and r.json().get("success"), f"HTTP={r.status_code}")

r = requests.get(f"{BASE}/admin/integrations/audit", timeout=30)
record("audit_route", r.status_code == 200 and r.json().get("success"), f"HTTP={r.status_code}")

failed = [c for c in checks if not c[1]]
print("STEP_H_CLIENT_INTEGRATIONS_RESULTS")
print("FAILED_COUNT", len(failed))
if not failed:
    print("STEP_H_CLIENT_INTEGRATIONS_READY")
else:
    print("FAILED_DETAILS", failed)
