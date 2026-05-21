import requests

API_URL = "https://api.trance-formation.com.au"
FRONTEND_URL = "https://trance-formation.com.au"

checks = []
failed = []

def check(name, url, headers=None):
    try:
        r = requests.get(url, headers=headers or {}, timeout=30)
        ok = 200 <= r.status_code < 500
        print(f"{name}: {'PASS' if ok else 'FAIL'} HTTP={r.status_code}")
        checks.append((name, ok))
        if not ok:
            failed.append((name, r.status_code, r.text[:300]))
    except Exception as exc:
        print(f"{name}: FAIL {exc}")
        checks.append((name, False))
        failed.append((name, "exception", str(exc)))

check("api_health", f"{API_URL}/health")
check("frontend_home", FRONTEND_URL)

headers = {
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
}

check("database_readiness", f"{API_URL}/admin/database-readiness", headers)
check("billing_readiness", f"{API_URL}/admin/billing/readiness", headers)
check("admin_deployment_summary", f"{API_URL}/admin/deployment-control/summary", headers)

print("")
print("PRODUCTION_SMOKE_LAUNCH_LOCK_RESULTS")
print("TOTAL_CHECKS", len(checks))
print("FAILED_COUNT", len(failed))

if failed:
    print("FAILED_DETAILS")
    for item in failed:
        print(item)
else:
    print("PRODUCTION_SMOKE_LAUNCH_LOCK_READY")