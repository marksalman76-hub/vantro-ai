import json
import requests
from pathlib import Path

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

AUDIT_LOG = Path("data/security/security_audit_events.jsonl")

def show(label, response):
    print("\n===", label, "===")
    print("HTTP", response.status_code)
    print("X-Security-Audit-Profile:", response.headers.get("X-Security-Audit-Profile"))
    print("X-Session-Auth-Profile:", response.headers.get("X-Session-Auth-Profile"))
    print("X-Security-Profile:", response.headers.get("X-Security-Profile"))
    try:
        print(json.dumps(response.json(), indent=2)[:3500])
    except Exception:
        print(response.text[:3500])

# 1. Normal readiness route should pass.
r1 = requests.get(
    BASE + "/admin/security-audit-enforcement-readiness",
    headers=OWNER_HEADERS,
    timeout=30,
)
show("AUDIT_READINESS_NORMAL", r1)

# 2. Customer actor hitting admin path should create high severity durable audit event.
r2 = requests.get(
    BASE + "/admin/security-audit-enforcement-readiness",
    headers=CUSTOMER_HEADERS,
    timeout=30,
)
show("CUSTOMER_TO_ADMIN_AUDIT_EVENT", r2)

# 3. Owner admin path with no admin token in development should log admin token issue, not block.
r3 = requests.get(
    BASE + "/admin/security-audit-enforcement-readiness",
    headers=OWNER_HEADERS,
    timeout=30,
)
show("ADMIN_TOKEN_AUDIT_EVENT_DEV_MODE", r3)

# 4. Trusted origin validation: state-changing customer request without origin should log.
r4 = requests.post(
    BASE + "/customer/security-audit-test",
    headers=CUSTOMER_HEADERS,
    json={"test": "trusted_origin_validation"},
    timeout=30,
)
show("TRUSTED_ORIGIN_AUDIT_EVENT_DEV_MODE", r4)

# 5. Abuse aggregation: repeat admin misuse enough times to increment top paths/reasons.
for _ in range(4):
    requests.get(
        BASE + "/admin/security-audit-enforcement-readiness",
        headers=CUSTOMER_HEADERS,
        timeout=30,
    )

# 6. Readiness should now show memory + durable audit events.
r6 = requests.get(
    BASE + "/admin/security-audit-enforcement-readiness",
    headers=OWNER_HEADERS,
    timeout=30,
)
show("AUDIT_READINESS_AFTER_EVENTS", r6)

data = r6.json()
events_text = json.dumps(data.get("recent_events", []))
top_reasons_text = json.dumps(data.get("top_reasons", {}))
top_paths_text = json.dumps(data.get("top_paths", {}))

audit_file_exists = AUDIT_LOG.exists()
audit_line_count = 0
if audit_file_exists:
    audit_line_count = len(AUDIT_LOG.read_text(encoding="utf-8").splitlines())

checks = {
    "normal_readiness_http_200": r1.status_code == 200,
    "audit_profile_header_present": bool(r1.headers.get("X-Security-Audit-Profile")),
    "memory_events_increased": int(data.get("memory_event_count", 0)) >= 3,
    "durable_events_increased": int(data.get("durable_event_count", 0)) >= 3,
    "audit_file_exists": audit_file_exists,
    "audit_file_has_lines": audit_line_count >= 3,
    "admin_invalid_actor_reason_logged": "admin_route_invalid_actor" in events_text or "admin_route_invalid_actor" in top_reasons_text,
    "admin_token_reason_logged": "admin_token_missing_or_invalid" in events_text or "admin_token_missing_or_invalid" in top_reasons_text,
    "trusted_origin_reason_logged": "trusted_origin_missing_or_invalid" in events_text or "trusted_origin_missing_or_invalid" in top_reasons_text,
    "api_abuse_aggregation_present": bool(data.get("top_reasons")) and bool(data.get("top_paths")),
    "customer_safe_mode_true": data.get("customer_safe_response_mode") is True,
    "no_secret_exposure": data.get("secret_exposure") is False,
    "governance_bypass_false": data.get("governance_bypass") is False,
    "entitlement_bypass_false": data.get("entitlement_bypass") is False,
}

print("\n=== PRIORITY5_SECURITY_AUDIT_ENFORCEMENT_TEST_RESULTS ===")
print("audit_file_exists", audit_file_exists)
print("audit_line_count", audit_line_count)
for key, value in checks.items():
    print(key, value)

if all(checks.values()):
    print("PRIORITY5_SECURITY_AUDIT_ENFORCEMENT_TEST_OK")
else:
    print("PRIORITY5_SECURITY_AUDIT_ENFORCEMENT_TEST_NEEDS_REVIEW")