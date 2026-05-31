import json
import urllib.request
import urllib.error
from datetime import datetime

BASE_URL = "https://app.trance-formation.com.au"

TENANT_ID = "client_demo_001"

TESTS = []


def request_json(method, path, payload=None, timeout=60):
    url = f"{BASE_URL}{path}"
    data = None
    headers = {"Content-Type": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except Exception:
                body = {"raw": raw}
            return {
                "ok": 200 <= response.status < 300,
                "status": response.status,
                "body": body,
                "url": url,
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except Exception:
            body = {"raw": raw}
        return {
            "ok": False,
            "status": exc.code,
            "body": body,
            "url": url,
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": "ERROR",
            "body": {"error": str(exc)},
            "url": url,
        }


def add_result(name, result, expected=None, passed=None):
    if passed is None:
        passed = result.get("ok") is True

    TESTS.append({
        "name": name,
        "passed": passed,
        "status": result.get("status"),
        "url": result.get("url"),
        "expected": expected,
        "body": result.get("body"),
    })


print("LIVE_BETA_FUNCTIONAL_AUDIT_STARTED", datetime.utcnow().isoformat())


# 1. Admin page reachable
admin_page = request_json("GET", "/admin")
add_result(
    "admin_page_reachable",
    admin_page,
    expected="HTTP 200 page response",
    passed=admin_page["status"] == 200,
)

# 2. Client page reachable
client_page = request_json("GET", "/client")
add_result(
    "client_page_reachable",
    client_page,
    expected="HTTP 200 page response",
    passed=client_page["status"] == 200,
)

# 3. Client me/session route
client_me = request_json("GET", "/api/client-me")
add_result(
    "client_session_route",
    client_me,
    expected="Route returns JSON without crashing",
    passed=client_me["status"] in {200, 401, 403},
)

# 4. Integrations status route
integrations = request_json("GET", f"/api/client-integrations?tenant_id={TENANT_ID}")
integrations_body = integrations.get("body", {})
add_result(
    "client_integrations_status",
    integrations,
    expected="Integration status route returns success JSON",
    passed=integrations["status"] == 200 and isinstance(integrations_body, dict),
)

# 5. Client execution matrix
matrix = request_json("GET", f"/api/client-execution-matrix?tenant_id={TENANT_ID}")
add_result(
    "client_execution_matrix",
    matrix,
    expected="Execution matrix route returns JSON",
    passed=matrix["status"] == 200,
)

# 6. Latest deliverable
latest = request_json("GET", f"/api/client-latest-deliverable?tenant_id={TENANT_ID}")
add_result(
    "client_latest_deliverable",
    latest,
    expected="Latest deliverable route returns JSON",
    passed=latest["status"] == 200,
)

# 7. Client evidence
client_evidence = request_json("GET", f"/api/client-execution-evidence?tenant_id={TENANT_ID}&limit=10")
client_evidence_body = client_evidence.get("body", {})
client_evidence_data = client_evidence_body.get("data", {}) if isinstance(client_evidence_body, dict) else {}
client_evidence_items = client_evidence_data.get("evidence_items", []) if isinstance(client_evidence_data, dict) else []
add_result(
    "client_execution_evidence",
    client_evidence,
    expected="Client-safe evidence returns at least one evidence item after Brevo proof",
    passed=client_evidence["status"] == 200 and len(client_evidence_items) > 0,
)

# 8. Admin evidence
admin_evidence = request_json("GET", f"/api/admin-execution-evidence?tenant_id={TENANT_ID}&limit=10")
admin_evidence_body = admin_evidence.get("body", {})
admin_evidence_data = admin_evidence_body.get("data", {}) if isinstance(admin_evidence_body, dict) else {}
admin_evidence_items = admin_evidence_data.get("evidence_items", []) if isinstance(admin_evidence_data, dict) else []
add_result(
    "admin_execution_evidence",
    admin_evidence,
    expected="Admin evidence returns at least one evidence item after Brevo proof",
    passed=admin_evidence["status"] == 200 and len(admin_evidence_items) > 0,
)

# 9. Run agent proxy route with safe payload
run_agent_payload = {
    "tenant_id": TENANT_ID,
    "requested_agent": "marketing_specialist_agent",
    "workflow_stage": "beta_functional_audit",
    "task": "Create a short live beta functional audit output for portal verification.",
    "action_type": "ad_copy_generation",
    "region": "Australia",
    "language": "English",
    "currency": "AUD",
    "owner_approved": True,
    "execute_real_world_action": False,
    "project_id": "beta_functional_audit",
    "actor_role": "owner_admin",
    "requested_credits": 0,
}

run_agent = request_json("POST", "/api/run-agent", run_agent_payload)
add_result(
    "run_agent_proxy",
    run_agent,
    expected="Run-agent proxy accepts owner/admin safe test request",
    passed=run_agent["status"] in {200, 201},
)

# 10. Delegated workforce proxy with connected email
delegated_payload = {
    "tenant_id": TENANT_ID,
    "implementation_plan": {
        "action_packets": [
            {
                "packet_id": "beta_audit_delegated_001",
                "recommended_agent": "email_reply_agent",
                "title": "Send governed beta audit email proof through connected email provider",
                "risk_level": "medium",
                "approval_required": False,
            }
        ]
    },
    "owner_approved": True,
    "client_owned_agents": ["email_reply_agent"],
    "package_tier": "enterprise",
    "connected_integrations": ["email"],
}

delegated = request_json("POST", "/api/delegated-workforce-execution", delegated_payload)
delegated_body = delegated.get("body", {})
delegated_data = delegated_body.get("data", {}) if isinstance(delegated_body, dict) else {}
completed = delegated_data.get("completed_results", []) if isinstance(delegated_data, dict) else []
first_action = {}
if completed:
    deliverable = completed[0].get("deliverable", {})
    actions = deliverable.get("actions_performed", [])
    if actions:
        first_action = actions[0]

add_result(
    "delegated_workforce_live_email",
    delegated,
    expected="Delegated workforce triggers live email_sent through Brevo with tenant client_demo_001",
    passed=(
        delegated["status"] == 200
        and first_action.get("type") == "email_sent"
        and first_action.get("tenant_id") == TENANT_ID
        and first_action.get("credential_exposed") is False
    ),
)

# 11. Evidence after delegated live execution
client_evidence_after = request_json("GET", f"/api/client-execution-evidence?tenant_id={TENANT_ID}&limit=10")
client_after_body = client_evidence_after.get("body", {})
client_after_data = client_after_body.get("data", {}) if isinstance(client_after_body, dict) else {}
client_after_items = client_after_data.get("evidence_items", []) if isinstance(client_after_data, dict) else []

has_email_sent = any(
    item.get("action_type") == "email_sent"
    and item.get("tenant_id") == TENANT_ID
    for item in client_after_items
)

add_result(
    "client_evidence_after_live_execution",
    client_evidence_after,
    expected="Client evidence includes email_sent for client_demo_001 after live delegated execution",
    passed=client_evidence_after["status"] == 200 and has_email_sent,
)


summary = {
    "audit": "live_beta_functional_audit",
    "base_url": BASE_URL,
    "tenant_id": TENANT_ID,
    "total": len(TESTS),
    "passed": sum(1 for t in TESTS if t["passed"]),
    "failed": sum(1 for t in TESTS if not t["passed"]),
    "tests": TESTS,
}

print(json.dumps(summary, indent=2))
print("LIVE_BETA_FUNCTIONAL_AUDIT_COMPLETED")