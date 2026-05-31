import json
import urllib.error
import urllib.request

url = "https://app.trance-formation.com.au/api/delegated-workforce-execution"

payload = {
    "implementation_plan": {
        "action_packets": [
            {
                "packet_id": "connected_live_002",
                "recommended_agent": "marketing_specialist_agent",
                "title": "Commission targeted healthcare technology market research and client interviews",
                "implementation_action": "Commission targeted healthcare technology market research and client interviews",
                "risk_level": "medium",
                "approval_required": False,
            }
        ]
    },
    "owner_approved": False,
    "client_owned_agents": ["marketing_specialist_agent"],
    "package_tier": "enterprise",
    "connected_integrations": ["email", "crm", "calendar"],
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=60) as response:
        body = response.read().decode("utf-8")
        print("HTTP_STATUS", response.status)
        print(body)

        parsed = json.loads(body)
        data = parsed.get("data", parsed)

        print("\nSUMMARY")
        print("connected_integrations:", data.get("connected_integrations"))
        print("external_integration_count:", data.get("external_integration_count"))
        print("completed_count:", data.get("completed_count"))
        print("queued_count:", data.get("queued_count"))
        print("blocked_count:", data.get("blocked_count"))

        completed = (data.get("completed_results") or [{}])[0]
        print("external_action_performed:", completed.get("external_action_performed"))
        print("live_external_call_executed:", completed.get("live_external_call_executed"))
        print("actions_performed:", completed.get("deliverable", {}).get("actions_performed"))

except urllib.error.HTTPError as e:
    print("HTTP_ERROR", e.code)
    print(e.read().decode("utf-8", errors="replace"))
except Exception as e:
    print("REQUEST_FAILED", repr(e))