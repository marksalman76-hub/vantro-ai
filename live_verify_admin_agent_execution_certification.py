import json
import os
import urllib.request
import urllib.error

FRONTEND = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")

AGENTS = [
    "marketing_specialist",
    "seo_agent",
    "email_reply_agent",
    "social_media_content_creator",
    "crm_agent",
]

TASK = "Create a short launch readiness summary for a test ecommerce store. Keep it customer-safe and concise."

def post_run_agent(agent_id):
    url = FRONTEND + "/api/run-agent"
    payload = {
        "tenant_id": "owner_admin",
        "account_reference": "owner_admin",
        "requested_agent": agent_id,
        "workflow_stage": "admin_execution_certification",
        "action_type": "admin_owner_execution",
        "actor_role": "owner",
        "owner_approved": True,
        "task": TASK,
    }

    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "User-Agent": "AdminAgentExecutionCertification/1.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner_admin",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            text = response.read().decode("utf-8", errors="ignore")
            status = response.status
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="ignore")
        status = exc.code
    except Exception as exc:
        return {
            "agent_id": agent_id,
            "http_status": "ERROR",
            "error": str(exc),
            "success": False,
        }

    try:
        data = json.loads(text)
    except Exception:
        data = {"raw": text[:1200]}

    blocked_reason = (
        data.get("error")
        or data.get("status")
        or data.get("workflow_status")
        or data.get("execution_status")
        or data.get("reason")
        or ""
    )

    return {
        "agent_id": agent_id,
        "http_status": status,
        "success": data.get("success") is True,
        "blocked_or_review": any(
            marker in str(blocked_reason).lower()
            for marker in ["blocked", "denied", "review", "unauthorized", "auth"]
        ),
        "status": blocked_reason,
        "body_sample": data,
    }

results = [post_run_agent(agent) for agent in AGENTS]

summary = {
    "frontend_base_url": FRONTEND,
    "agent_count_tested": len(AGENTS),
    "results": results,
    "successful_agents": [r["agent_id"] for r in results if r.get("success")],
    "blocked_or_review_agents": [r["agent_id"] for r in results if r.get("blocked_or_review")],
    "failed_agents": [
        r["agent_id"]
        for r in results
        if not r.get("success")
    ],
    "admin_agent_execution_certification_passed": all(r.get("success") for r in results),
}

print(json.dumps(summary, indent=2))

if not summary["admin_agent_execution_certification_passed"]:
    print("ADMIN_AGENT_EXECUTION_CERTIFICATION_FAILED")
    raise SystemExit(1)

print("ADMIN_AGENT_EXECUTION_CERTIFICATION_PASSED")