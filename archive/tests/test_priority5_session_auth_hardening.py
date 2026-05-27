import json
import requests

BASE = "http://127.0.0.1:8000"

OWNER_HEADERS = {
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
    "Content-Type": "application/json",
}

CUSTOMER_HEADERS = {
    "x-tenant-id": "client_demo_001",
    "x-actor-role": "customer",
    "Content-Type": "application/json",
}

def show(label, response):
    print("\n===", label, "===")
    print("HTTP", response.status_code)
    print("X-Session-Auth-Profile:", response.headers.get("X-Session-Auth-Profile"))
    print("X-Security-Profile:", response.headers.get("X-Security-Profile"))
    try:
        print(json.dumps(response.json(), indent=2)[:3000])
    except Exception:
        print(response.text[:3000])

# 1. Normal readiness route should pass.
r1 = requests.get(
    BASE + "/admin/session-auth-hardening-readiness",
    headers=OWNER_HEADERS,
    timeout=30,
)
show("SESSION_READINESS_NORMAL", r1)

# 2. Customer actor hitting admin path should log admin auth anomaly.
r2 = requests.get(
    BASE + "/admin/session-auth-hardening-readiness",
    headers=CUSTOMER_HEADERS,
    timeout=30,
)
show("CUSTOMER_TO_ADMIN_ANOMALY_LOGGED", r2)

# 3. Missing tenant on admin path should log missing tenant anomaly.
r3 = requests.get(
    BASE + "/admin/session-auth-hardening-readiness",
    headers={"x-actor-role": "owner", "Content-Type": "application/json"},
    timeout=30,
)
show("ADMIN_MISSING_TENANT_LOGGED", r3)

# 4. CSRF risk: state-changing customer request without origin/referer/csrf.
# In development this should log but not block.
r4 = requests.post(
    BASE + "/customer/security-session-test",
    headers=CUSTOMER_HEADERS,
    json={"test": "csrf_risk_detection"},
    timeout=30,
)
show("CSRF_RISK_LOGGED_DEV_MODE", r4)

# 5. Replay foundation: repeat same state-changing request with same idempotency key.
replay_headers = dict(CUSTOMER_HEADERS)
replay_headers["x-idempotency-key"] = "priority5-replay-proof-001"

r5a = requests.post(
    BASE + "/customer/security-session-test",
    headers=replay_headers,
    json={"test": "replay_detection"},
    timeout=30,
)
show("REPLAY_FIRST_REQUEST", r5a)

r5b = requests.post(
    BASE + "/customer/security-session-test",
    headers=replay_headers,
    json={"test": "replay_detection"},
    timeout=30,
)
show("REPLAY_SECOND_REQUEST_LOGGED", r5b)

# 6. Readiness should now show anomaly events.
r6 = requests.get(
    BASE + "/admin/session-auth-hardening-readiness",
    headers=OWNER_HEADERS,
    timeout=30,
)
show("SESSION_READINESS_AFTER_EVENTS", r6)

data = r6.json()
events = data.get("recent_events", [])
reason_text = json.dumps(events)

checks = {
    "normal_readiness_http_200": r1.status_code == 200,
    "session_auth_profile_header_present": bool(r1.headers.get("X-Session-Auth-Profile")),
    "event_count_increased": int(data.get("event_count", 0)) >= 3,
    "high_severity_seen": int(data.get("severity_counts", {}).get("high", 0)) >= 2,
    "medium_or_high_seen": (
        int(data.get("severity_counts", {}).get("medium", 0)) >= 1
        or int(data.get("severity_counts", {}).get("high", 0)) >= 1
    ),
    "admin_invalid_actor_logged": "admin_path_invalid_actor_role" in reason_text,
    "csrf_risk_logged": "csrf_token_or_origin_missing_for_state_change" in reason_text,
    "replay_detection_logged": "possible_replay_request_detected" in reason_text,
    "production_blocking_off_in_dev": data.get("production_blocking_mode") is False,
    "customer_safe_mode_true": data.get("customer_safe_response_mode") is True,
}

print("\n=== PRIORITY5_SESSION_AUTH_HARDENING_TEST_RESULTS ===")
for key, value in checks.items():
    print(key, value)

if all(checks.values()):
    print("PRIORITY5_SESSION_AUTH_HARDENING_TEST_OK")
else:
    print("PRIORITY5_SESSION_AUTH_HARDENING_TEST_NEEDS_REVIEW")