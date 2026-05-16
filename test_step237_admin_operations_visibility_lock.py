import json
import urllib.request

BASE = "http://127.0.0.1:3000"

req = urllib.request.Request(
    BASE + "/api/admin-runtime",
    method="GET",
)

with urllib.request.urlopen(req, timeout=30) as res:
    data = json.loads(res.read().decode("utf-8"))

operations = data.get("operations") or {}
combined = json.dumps(data).lower()

checks = {
    "admin_runtime_success": data.get("success") is True,
    "operations_present": isinstance(operations, dict),
    "recovery_summary_present": "recovery_summary" in operations,
    "artifacts_present": "artifacts" in operations,
    "recovery_summary_ok": operations.get("recovery_summary", {}).get("ok") is True,
    "artifacts_ok": operations.get("artifacts", {}).get("ok") is True,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_237_ADMIN_OPERATIONS_VISIBILITY_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps(data, indent=2))
    raise SystemExit(1)

print("STEP_237_ADMIN_OPERATIONS_VISIBILITY_LOCK_OK")
