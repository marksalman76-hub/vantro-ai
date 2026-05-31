import json
import urllib.request
import urllib.error

FRONTEND = "https://app.trance-formation.com.au"

TESTS = [
    "seo_agent",
    "email_reply_agent",
    "email_marketing_agent",
]

for agent in TESTS:
    payload = {
        "path": "/run-agent",
        "method": "POST",
        "payload": {
            "tenant_id": "owner_admin",
            "account_reference": "owner_admin",
            "requested_agent": agent,
            "workflow_stage": "admin_proxy_execution_test",
            "action_type": "admin_owner_execution",
            "actor_role": "owner",
            "owner_approved": True,
            "task": "Create a short launch readiness summary for a premium ecommerce store.",
        },
    }

    req = urllib.request.Request(
        FRONTEND + "/api/admin-deployment-control",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            body = response.read().decode("utf-8", errors="ignore")
            status = response.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        status = exc.code

    print("\n" + "=" * 80)
    print("AGENT:", agent)
    print("HTTP:", status)
    print(body[:2000])