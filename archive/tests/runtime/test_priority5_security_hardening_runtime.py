import json
import requests

BASE = "http://127.0.0.1:8000"

HEADERS = {
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
    "Content-Type": "application/json",
}

def show(label, response):
    print("\n===", label, "===")
    print("HTTP", response.status_code)
    print("X-Security-Profile:", response.headers.get("X-Security-Profile"))
    print("X-Request-Fingerprint:", response.headers.get("X-Request-Fingerprint"))
    try:
        print(json.dumps(response.json(), indent=2)[:2500])
    except Exception:
        print(response.text[:2500])

# 1. Normal readiness route should pass and include security headers.
r1 = requests.get(
    BASE + "/admin/security-hardening-readiness",
    headers=HEADERS,
    timeout=30,
)
show("READINESS_NORMAL", r1)

# 2. Suspicious blocked probe should return 403.
r2 = requests.get(
    BASE + "/.env",
    headers={"x-tenant-id": "unknown", "x-actor-role": "anonymous"},
    timeout=30,
)
show("BLOCKED_DOTENV_PROBE", r2)

# 3. Suspicious query should be logged as high severity but not necessarily blocked.
r3 = requests.get(
    BASE + "/admin/security-hardening-readiness?search=union%20select%20password",
    headers=HEADERS,
    timeout=30,
)
show("SUSPICIOUS_QUERY_LOGGED", r3)

# 4. Admin route with customer actor should be logged as high severity.
r4 = requests.get(
    BASE + "/admin/security-hardening-readiness",
    headers={"x-tenant-id": "client_demo_001", "x-actor-role": "customer"},
    timeout=30,
)
show("ADMIN_ROUTE_NON_ADMIN_ACTOR_LOGGED", r4)

# 5. Readiness should now show recent security events.
r5 = requests.get(
    BASE + "/admin/security-hardening-readiness",
    headers=HEADERS,
    timeout=30,
)
show("READINESS_AFTER_EVENTS", r5)

data = r5.json()
checks = {
    "normal_readiness_http_200": r1.status_code == 200,
    "security_profile_header_present": bool(r1.headers.get("X-Security-Profile")),
    "fingerprint_header_present": bool(r1.headers.get("X-Request-Fingerprint")),
    "dotenv_probe_blocked_403": r2.status_code == 403,
    "event_count_increased": int(data.get("event_count", 0)) >= 2,
    "severity_counts_present": bool(data.get("severity_counts")),
    "critical_event_seen": int(data.get("severity_counts", {}).get("critical", 0)) >= 1,
    "high_event_seen": int(data.get("severity_counts", {}).get("high", 0)) >= 1,
}

print("\n=== PRIORITY5_SECURITY_HARDENING_TEST_RESULTS ===")
for key, value in checks.items():
    print(key, value)

if all(checks.values()):
    print("PRIORITY5_SECURITY_HARDENING_TEST_OK")
else:
    print("PRIORITY5_SECURITY_HARDENING_TEST_NEEDS_REVIEW")