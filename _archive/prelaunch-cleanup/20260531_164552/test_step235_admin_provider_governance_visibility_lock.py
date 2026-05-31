import json
import urllib.request

BASE = "http://127.0.0.1:3000"

req = urllib.request.Request(
    BASE + "/api/admin-runtime",
    method="GET",
)

with urllib.request.urlopen(req, timeout=30) as res:
    data = json.loads(res.read().decode("utf-8"))

governance = data.get("provider_governance") or {}

combined_text = json.dumps(data).lower()

checks = {
    "admin_runtime_success": data.get("success") is True,
    "provider_governance_present": isinstance(governance, dict),
    "provider_readiness_present": "provider_readiness" in governance,
    "provider_audit_present": "provider_audit" in governance,
    "openai_sdk_readiness_present": "openai_sdk_readiness" in governance,
    "live_llm_dashboard_present": "live_llm_dashboard" in governance,
    "live_llm_control_present": "live_llm_control" in governance,
    "database_readiness_present": "database_readiness" in governance,
    "billing_readiness_present": "billing_readiness" in governance,
    "no_secret_values_exposed": all(secret not in combined_text for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_235_ADMIN_PROVIDER_GOVERNANCE_VISIBILITY_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps(data, indent=2))
    raise SystemExit(1)

print("STEP_235_ADMIN_PROVIDER_GOVERNANCE_VISIBILITY_LOCK_OK")
