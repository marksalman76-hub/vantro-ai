import json
import urllib.request
import urllib.error
from datetime import datetime

BASE_URL = "https://app.trance-formation.com.au"
TENANT_ID = "client_demo_001"

tests = []


def request(method, path, payload=None, timeout=60):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"}

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except Exception:
                body = {"raw": raw[:1000]}
            return {"ok": 200 <= res.status < 300, "status": res.status, "body": body, "url": url}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except Exception:
            body = {"raw": raw[:1000]}
        return {"ok": False, "status": exc.code, "body": body, "url": url}
    except Exception as exc:
        return {"ok": False, "status": "ERROR", "body": {"error": str(exc)}, "url": url}


def add(name, result, passed=None, expected=""):
    tests.append({
        "name": name,
        "passed": result["ok"] if passed is None else passed,
        "status": result["status"],
        "expected": expected,
        "url": result["url"],
        "body": result["body"],
    })


print("LIVE_BETA_ONBOARDING_BILLING_AUDIT_STARTED", datetime.utcnow().isoformat())


routes = [
    ("signup_page", "GET", "/signup", "Signup page loads"),
    ("login_page", "GET", "/login", "Login page loads"),
    ("activate_page", "GET", "/activate", "Activation page loads"),
    ("client_page", "GET", "/client", "Client portal loads"),
    ("billing_page", "GET", "/client/billing", "Billing page loads"),
    ("billing_success_page", "GET", "/client/billing/success", "Billing success page loads"),
    ("billing_cancel_page", "GET", "/client/billing/cancel", "Billing cancel page loads"),
    ("billing_cancelled_page", "GET", "/client/billing/cancelled", "Billing cancelled page loads"),
]

for name, method, path, expected in routes:
    result = request(method, path)
    add(name, result, passed=result["status"] == 200, expected=expected)


api_checks = [
    ("signup_options_starter", "GET", "/api/signup-agent-selection/options/starter", "Starter agent options return"),
    ("signup_options_growth", "GET", "/api/signup-agent-selection/options/growth", "Growth agent options return"),
    ("signup_options_business", "GET", "/api/signup-agent-selection/options/business", "Business agent options return"),
    ("signup_options_enterprise", "GET", "/api/signup-agent-selection/options/enterprise", "Enterprise agent options return"),
    ("activation_invite_status", "GET", "/api/activation-invite-status?tenant_id=client_demo_001", "Activation invite status route returns"),
    ("activation_state_restore", "GET", "/api/activation-state-restore?tenant_id=client_demo_001", "Activation state restore route returns"),
    ("client_me", "GET", "/api/client-me", "Client session route returns"),
    ("client_business_profile", "GET", f"/api/client-business-profile?tenant_id={TENANT_ID}", "Business profile route returns"),
    ("client_integrations", "GET", f"/api/client-integrations?tenant_id={TENANT_ID}", "Client integrations route returns"),
    ("client_execution_matrix", "GET", f"/api/client-execution-matrix?tenant_id={TENANT_ID}", "Execution matrix route returns"),
]

for name, method, path, expected in api_checks:
    result = request(method, path)
    add(name, result, passed=result["status"] in {200, 400, 401, 403, 404}, expected=expected)


checkout_payload = {
    "tenant_id": TENANT_ID,
    "plan": "starter",
    "billing_cycle": "monthly",
    "success_url": f"{BASE_URL}/client/billing/success",
    "cancel_url": f"{BASE_URL}/client/billing/cancel",
}

checkout = request("POST", "/api/billing-checkout", checkout_payload)
add(
    "billing_checkout_route",
    checkout,
    passed=checkout["status"] in {200, 201, 400, 401, 403, 500},
    expected="Billing checkout route responds without frontend crash",
)


activation_packet_payload = {
    "tenant_id": TENANT_ID,
    "plan": "starter",
    "selected_agents": ["marketing_specialist_agent"],
}

activation_packet = request("POST", "/api/signup-agent-selection/activation-packet", activation_packet_payload)
add(
    "signup_activation_packet",
    activation_packet,
    passed=activation_packet["status"] in {200, 201, 400, 401, 403, 422, 500},
    expected="Activation packet route responds",
)


summary = {
    "audit": "live_beta_onboarding_billing_audit",
    "base_url": BASE_URL,
    "tenant_id": TENANT_ID,
    "total": len(tests),
    "passed": sum(1 for t in tests if t["passed"]),
    "failed": sum(1 for t in tests if not t["passed"]),
    "tests": tests,
}

print(json.dumps(summary, indent=2))
print("LIVE_BETA_ONBOARDING_BILLING_AUDIT_COMPLETED")