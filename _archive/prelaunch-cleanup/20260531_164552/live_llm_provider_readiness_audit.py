import json
import urllib.request
import urllib.error
from datetime import datetime

BASE_URL = "https://app.trance-formation.com.au"
TENANT_ID = "client_demo_001"

tests = []


def request(method, path, payload=None, timeout=90):
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
                body = {"raw": raw[:2000]}
            return {"ok": 200 <= res.status < 300, "status": res.status, "body": body, "url": url}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except Exception:
            body = {"raw": raw[:2000]}
        return {"ok": False, "status": exc.code, "body": body, "url": url}
    except Exception as exc:
        return {"ok": False, "status": "ERROR", "body": {"error": str(exc)}, "url": url}


def add(name, result, passed, expected):
    tests.append({
        "name": name,
        "passed": passed,
        "status": result["status"],
        "expected": expected,
        "url": result["url"],
        "body": result["body"],
    })


print("LIVE_LLM_PROVIDER_READINESS_AUDIT_STARTED", datetime.utcnow().isoformat())


payload = {
    "tenant_id": TENANT_ID,
    "requested_agent": "marketing_specialist_agent",
    "workflow_stage": "marketing_campaign",
    "task": "Create a short premium beta readiness marketing recommendation for a local service business.",
    "action_type": "marketing_campaign_execution",
    "region": "Australia",
    "language": "English",
    "currency": "AUD",
    "owner_approved": True,
    "execute_real_world_action": False,
    "actor_role": "owner_admin",
    "requested_credits": 0,
}

run_agent = request("POST", "/api/run-agent", payload)
body = run_agent.get("body", {})
data = body.get("data", body) if isinstance(body, dict) else {}

text_blob = json.dumps(data, ensure_ascii=False)

provider_ready = '"provider_ready": true' in text_blob or '"provider_ready":true' in text_blob
live_allowed = '"live_execution_allowed": true' in text_blob or '"live_execution_allowed":true' in text_blob
generated_content_present = '"generated_content": null' not in text_blob and "generated_content" in text_blob
blocked_until_ready = "openai_live_connector_blocked_until_ready" in text_blob
global_block = "global_live_llm_enabled" in text_blob
owner_block = "owner_live_execution_enabled" in text_blob

add(
    "run_agent_llm_provider_route",
    run_agent,
    passed=run_agent["status"] in {200, 201},
    expected="Run-agent route responds",
)

add(
    "provider_ready",
    run_agent,
    passed=provider_ready,
    expected="Provider readiness should be true for live LLM execution",
)

add(
    "live_execution_allowed",
    run_agent,
    passed=live_allowed,
    expected="Live LLM execution gate should allow execution",
)

add(
    "generated_content_present",
    run_agent,
    passed=generated_content_present,
    expected="Live LLM execution should return generated content",
)

add(
    "not_blocked_until_ready",
    run_agent,
    passed=not blocked_until_ready,
    expected="Should not be blocked until provider readiness",
)

add(
    "global_live_llm_enabled_not_blocking",
    run_agent,
    passed=not global_block,
    expected="Global live LLM flag should not block execution",
)

add(
    "owner_live_execution_enabled_not_blocking",
    run_agent,
    passed=not owner_block,
    expected="Owner live execution flag should not block execution",
)

summary = {
    "audit": "live_llm_provider_readiness_audit",
    "base_url": BASE_URL,
    "tenant_id": TENANT_ID,
    "total": len(tests),
    "passed": sum(1 for t in tests if t["passed"]),
    "failed": sum(1 for t in tests if not t["passed"]),
    "tests": tests,
}

print(json.dumps(summary, indent=2))
print("LIVE_LLM_PROVIDER_READINESS_AUDIT_COMPLETED")