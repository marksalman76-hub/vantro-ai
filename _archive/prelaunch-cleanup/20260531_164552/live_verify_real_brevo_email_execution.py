import json
import urllib.request

url = "https://app.trance-formation.com.au/api/delegated-workforce-execution"

payload = {
    "implementation_plan": {
        "action_packets": [
            {
                "packet_id": "live_brevo_verify_001",
                "recommended_agent": "email_reply_agent",
                "title": "Send governed live Brevo execution verification email",
                "risk_level": "medium",
                "approval_required": False,
            }
        ]
    },
    "owner_approved": True,
    "client_owned_agents": [
        "email_reply_agent"
    ],
    "package_tier": "enterprise",
    "tenant_id": "client_demo_001",
    "connected_integrations": [
        "email"
    ],
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
    },
    method="POST",
)

with urllib.request.urlopen(req, timeout=120) as response:
    body = response.read().decode("utf-8")

    print("HTTP_STATUS", response.status)
    print(body)

    parsed = json.loads(body)

    data = parsed.get("data", {})
    completed = data.get("completed_results", [])

    if completed:
        result = completed[0]

        print("\nLIVE EXECUTION SUMMARY")
        print("external_action_performed:", result.get("external_action_performed"))
        print("live_external_call_executed:", result.get("live_external_call_executed"))

        deliverable = result.get("deliverable", {})
        actions = deliverable.get("actions_performed", [])

        for action in actions:
            print("\nACTION")
            print(json.dumps(action, indent=2))