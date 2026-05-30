import json
import time
import uuid
import urllib.request
import urllib.error

FRONTEND = "https://app.trance-formation.com.au"

TESTS = [
    "seo_agent",
    "email_reply_agent",
    "crm_ai_agent",
    "marketing_specialist_agent",
    "social_media_manager_content_creator_agent",
]

for agent in TESTS:
    request_id = f"admin-cert-{agent}-{uuid.uuid4()}"
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
            "task": f"Create a short launch readiness summary for a premium ecommerce store. Test agent: {agent}.",
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
            "x-request-id": request_id,
            "x-idempotency-key": request_id,
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
    print(body[:2500])
    time.sleep(1.2)